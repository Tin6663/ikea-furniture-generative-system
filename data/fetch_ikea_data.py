#!/usr/bin/env python3
"""
IKEA 官方产品数据抓取脚本
从宜家未公开REST API中拉取产品数据，写入本地SQLite数据库

【数据来源说明】
宜家没有公开的官方API，但其官网内部使用以下可访问端点：
  - 搜索 API：  https://sik.search.blue.cdtapps.com/cn/zh/search-result-page
  - 产品详情：  https://api.ingka.ikea.com/cia/availabilities/ru/cn/{item_code}
  - 产品价格/信息（PIP）：爬取 https://www.ikea.cn/cn/zh/p/{slug}/

更多信息参考：
  - 第三方 Python 封装库（已归档）：https://github.com/vrslev/ikea-api-client
  - 第三方库文档：pip install ikea_api

【Bunnings 数据说明】
Bunnings (bunnings.com.au) 也没有官方API，其产品数据只能通过网页爬虫获取。
Bunnings主要提供通用五金件（螺丝、合页、支架等），可作为宜家FIXA系列的替代品。
与宜家主营家具部件不同，Bunnings更适合补充连接件、辅材件数据。

【使用方法】
  cd ikea-furniture-generative-system
  python3 data/fetch_ikea_data.py

  可选参数：
    --keywords LAGKAPTEN ADILS OLOV ...  # 指定搜索关键词
    --country cn --lang zh              # 指定国家/语言（默认中国）
    --dry-run                           # 仅打印结果，不写入数据库
    --limit 24                          # 每个关键词最多抓取条数

【注意事项】
  - 请遵守宜家网站使用条款，不要频繁大量抓取
  - 抓取的数据可能因地区/时间不同而有差异，使用前请核实
  - 价格、货号以宜家官网（ikea.cn）最新数据为准
"""

import json
import logging
import os
import sqlite3
import sys
import time
import argparse
from typing import Optional

import requests

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import DB_PATH

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── 默认抓取关键词（宜家桌类相关产品）─────────────────────────────────────────
DEFAULT_KEYWORDS = [
    "LINNMON", "LAGKAPTEN", "GERTON", "KARLBY",        # 桌面系列
    "ADILS", "OLOV", "CAPITA", "HILVER", "LERBERG",    # 桌腿/支架系列
    "ALEX",                                             # 抽屉单元
    "SIGNUM",                                           # 电线管理
    "FIXA",                                             # 螺丝/辅材
    "BEKANT", "TROTTEN",                                # 可升降桌框架
]

# ── IKEA API 端点 ─────────────────────────────────────────────────────────────
IKEA_SEARCH_API = "https://sik.search.blue.cdtapps.com/{country}/{lang}/search-result-page"
IKEA_SEARCH_PARAMS = {
    "c": "listView",
    "v": "20211005",
    "size": 24,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.ikea.cn/",
}


# ── 分类推断规则 ──────────────────────────────────────────────────────────────
def _infer_category(product: dict) -> str:
    """根据产品名称/类型推断零件分类"""
    name = (product.get("name", "") + " " + product.get("typeName", "")).lower()
    if any(k in name for k in ["table top", "desk top", "worktop", "桌面", "台面"]):
        return "板材件"
    if any(k in name for k in ["leg", "桌腿", "支腿", "trestle", "sawhorse"]):
        return "结构件"
    if any(k in name for k in ["drawer", "抽屉", "cabinet"]):
        return "功能件"
    if any(k in name for k in ["cable", "wire", "线", "走线"]):
        return "功能件"
    if any(k in name for k in ["screw", "bolt", "bracket", "螺丝", "螺栓", "支架"]):
        return "连接件"
    if any(k in name for k in ["pad", "felt", "脚垫", "防滑"]):
        return "辅材件"
    return "结构件"


def _extract_price(product: dict) -> Optional[float]:
    """从产品字典中提取价格"""
    try:
        sp = product.get("salesPrice", {})
        # 结构: salesPrice.current.wholeNumber 或 salesPrice.numeral
        if "current" in sp:
            return float(sp["current"].get("wholeNumber", 0) or 0) or None
        if "numeral" in sp:
            return float(sp["numeral"]) or None
        if "mainPriceProps" in sp:
            return float(sp["mainPriceProps"].get("numeral", 0) or 0) or None
    except (TypeError, ValueError, KeyError):
        pass
    return None


def _extract_dimensions(product: dict) -> dict:
    """从产品字典中提取尺寸信息（尽量解析）"""
    dims = {"length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None}
    try:
        measurements = product.get("measurements", {}).get("childItems", [])
        for m in measurements:
            label = m.get("label", "").lower()
            val_str = m.get("text", "")
            try:
                # 格式通常是 "120 cm" 或 "120×60 cm"
                if "×" in val_str or "x" in val_str.lower():
                    parts = val_str.lower().replace("×", "x").split("x")
                    nums = [float(p.strip().replace("cm", "").strip()) for p in parts]
                    if len(nums) >= 2:
                        dims["length_cm"] = nums[0]
                        dims["width_cm"] = nums[1]
                    if len(nums) >= 3:
                        dims["height_cm"] = nums[2]
                elif "cm" in val_str.lower():
                    val = float(val_str.lower().replace("cm", "").strip())
                    if "length" in label or "长" in label:
                        dims["length_cm"] = val
                    elif "width" in label or "宽" in label:
                        dims["width_cm"] = val
                    elif "height" in label or "高" in label or "depth" in label:
                        dims["height_cm"] = val
                    elif "thick" in label or "厚" in label:
                        dims["thickness_cm"] = val
            except ValueError:
                continue
    except (AttributeError, TypeError):
        pass
    return dims


# ── 搜索与解析 ────────────────────────────────────────────────────────────────
def search_ikea_products(
    keyword: str,
    country: str = "cn",
    lang: str = "zh",
    limit: int = 24,
    timeout: int = 15,
) -> list:
    """
    调用宜家搜索API，返回产品列表原始字典。

    参数：
        keyword: 搜索关键词，如 "LAGKAPTEN"
        country: 两位国家代码，如 "cn"（中国）、"au"（澳大利亚）
        lang:    语言代码，如 "zh"、"en"
        limit:   最多返回条数
        timeout: 请求超时秒数
    返回：
        list of product dicts (原始API返回格式)
    """
    url = IKEA_SEARCH_API.format(country=country, lang=lang)
    params = {**IKEA_SEARCH_PARAMS, "q": keyword, "size": limit}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"请求失败 [{keyword}]: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败 [{keyword}]: {e}")
        return []

    # 导航到产品列表
    try:
        products = (
            data.get("searchResultPage", {})
                .get("productWindow", [])
        )
        return [p.get("product", p) for p in products if p]
    except (AttributeError, KeyError):
        logger.warning(f"无法解析搜索结果 [{keyword}]，原始响应键：{list(data.keys())}")
        return []


def parse_product_to_db_row(product: dict, keyword: str) -> Optional[dict]:
    """
    将IKEA API产品字典转换为数据库行格式。

    参数：
        product: 来自搜索API的单个产品字典
        keyword: 搜索关键词（用于命名part_id）
    返回：
        可直接插入ikea_parts表的字典，或None（无法解析时）
    """
    item_no = str(product.get("itemNoGlobal", "")).strip()
    if not item_no:
        return None

    # 格式化货号为 XXX.XXX.XX
    if len(item_no) == 8 and item_no.isdigit():
        article_no = f"{item_no[:3]}.{item_no[3:6]}.{item_no[6:]}"
    else:
        article_no = item_no

    name = product.get("name", keyword)
    type_name = product.get("typeName", "")
    full_name = f"{name} {type_name}".strip()

    dims = _extract_dimensions(product)
    category = _infer_category(product)
    price = _extract_price(product)
    part_id = f"FETCHED_{keyword.upper()}_{item_no}"

    # 构造产品页URL
    country = "cn"
    lang = "zh"
    url_slug = product.get("url", "")
    ikea_url = f"https://www.ikea.cn{url_slug}" if url_slug.startswith("/") else ""

    return {
        "part_id": part_id,
        "ikea_article_number": article_no,
        "part_name": full_name,
        "part_name_en": product.get("nameEn", full_name),
        "part_category": category,
        "description": product.get("mainImageAlt", ""),
        "length_cm": dims["length_cm"],
        "width_cm": dims["width_cm"],
        "height_cm": dims["height_cm"],
        "thickness_cm": dims["thickness_cm"],
        "max_load_kg": None,
        "material": "",
        "color": product.get("colorLabel", ""),
        "surface_treatment": "",
        "compatible_thickness_mm": None,
        "install_method": "",
        "price_cny": price,
        "ikea_url": ikea_url,
        "is_available": 1,
        "adjustable": 0,
        "adjust_range_cm": "",
        "requires_tools": "",
        "package_weight_kg": None,
    }


# ── 写入数据库 ────────────────────────────────────────────────────────────────
INSERT_SQL = """
INSERT OR REPLACE INTO ikea_parts (
    part_id, ikea_article_number, part_name, part_name_en, part_category,
    description, length_cm, width_cm, height_cm, thickness_cm,
    max_load_kg, material, color, surface_treatment,
    compatible_thickness_mm, install_method, price_cny, ikea_url,
    is_available, adjustable, adjust_range_cm, requires_tools, package_weight_kg
) VALUES (
    :part_id, :ikea_article_number, :part_name, :part_name_en, :part_category,
    :description, :length_cm, :width_cm, :height_cm, :thickness_cm,
    :max_load_kg, :material, :color, :surface_treatment,
    :compatible_thickness_mm, :install_method, :price_cny, :ikea_url,
    :is_available, :adjustable, :adjust_range_cm, :requires_tools, :package_weight_kg
)
"""


def save_to_db(rows: list, db_path: str = DB_PATH) -> int:
    """将解析后的产品行列表插入数据库，返回成功插入数量。"""
    if not rows:
        return 0
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    saved = 0
    for row in rows:
        try:
            cur.execute(INSERT_SQL, row)
            saved += 1
        except sqlite3.Error as e:
            logger.warning(f"插入失败 [{row.get('part_id')}]: {e}")
    conn.commit()
    conn.close()
    return saved


# ── 主程序 ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="从宜家API抓取产品数据并写入本地数据库"
    )
    parser.add_argument(
        "--keywords", nargs="+", default=DEFAULT_KEYWORDS,
        help="搜索关键词列表（默认：宜家桌类相关产品）"
    )
    parser.add_argument(
        "--country", default="cn", help="国家代码（默认：cn）"
    )
    parser.add_argument(
        "--lang", default="zh", help="语言代码（默认：zh）"
    )
    parser.add_argument(
        "--limit", type=int, default=24, help="每个关键词最多抓取条数（默认：24）"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印结果，不写入数据库"
    )
    parser.add_argument(
        "--delay", type=float, default=1.5,
        help="请求间隔秒数，避免频繁访问（默认：1.5）"
    )
    args = parser.parse_args()

    total_fetched = 0
    total_saved = 0

    for keyword in args.keywords:
        logger.info(f"搜索：{keyword} ...")
        products = search_ikea_products(
            keyword, country=args.country, lang=args.lang, limit=args.limit
        )
        logger.info(f"  找到 {len(products)} 个产品")

        rows = []
        for p in products:
            row = parse_product_to_db_row(p, keyword)
            if row:
                rows.append(row)
                if args.dry_run:
                    print(f"  [{row['ikea_article_number']}] {row['part_name']}"
                          f"  价格：{'¥' + str(row['price_cny']) if row['price_cny'] else '未知'}"
                          f"  分类：{row['part_category']}")

        total_fetched += len(rows)

        if not args.dry_run:
            saved = save_to_db(rows)
            total_saved += saved
            logger.info(f"  写入数据库：{saved} 条")

        if args.delay > 0:
            time.sleep(args.delay)

    if args.dry_run:
        print(f"\n✅ 共解析 {total_fetched} 条产品数据（dry-run模式，未写入数据库）")
    else:
        print(f"\n✅ 共抓取 {total_fetched} 条，成功写入 {total_saved} 条 → {DB_PATH}")
        print("   ⚠️  抓取的数据为半结构化数据，材质/承重等字段可能为空，请人工核实后补全。")


if __name__ == "__main__":
    main()
