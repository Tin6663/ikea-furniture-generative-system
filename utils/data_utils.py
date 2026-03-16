"""
BOM清单生成工具
"""

import os
import json
import time
import logging
from models.structure_model import StructureSolution
from models.design_intent import DesignIntentIR
from config.api_config import BOM_OUTPUT_DIR

logger = logging.getLogger(__name__)


def generate_bom(solution: StructureSolution, ir: DesignIntentIR) -> tuple:
    """
    生成标准化BOM清单（Markdown表格 + JSON结构化数据）
    返回: (md_text, json_text, md_path, json_path)
    """
    os.makedirs(BOM_OUTPUT_DIR, exist_ok=True)
    dims = ir.furniture_base_info.overall_dimensions
    ts = int(time.time())
    md_path = os.path.join(BOM_OUTPUT_DIR, f"bom_{int(dims.length)}x{int(dims.width)}x{int(dims.height)}_{ts}.md")
    json_path = md_path.replace(".md", ".json")

    md_lines = [
        f"# 物料清单（BOM）\n",
        f"**家具类型**: {ir.furniture_base_info.sub_category or ir.furniture_base_info.category}  ",
        f"**整体尺寸**: {dims.length}×{dims.width}×{dims.height}cm  ",
        f"**主体材质**: {ir.furniture_base_info.main_material}  ",
        f"**承重要求**: ≥{ir.furniture_base_info.load_requirement.overall_load}kg  \n",
        "| 序号 | 宜家货号 | 零件名称 | 分类 | 规格参数 | 数量 | 装配位置 | 匹配依据 | 参考价格 |",
        "|------|----------|----------|------|----------|------|----------|----------|----------|",
    ]

    bom_json = []
    serial = 1
    for item in solution.bom_items:
        p = item.part
        spec = p.get_dimension_str()
        if p.material:
            spec += f" | {p.material}"
        if p.max_load_kg:
            spec += f" | 承重{p.max_load_kg}kg"
        price_str = f"¥{p.price_cny:.0f}" if p.price_cny else "—"

        md_lines.append(
            f"| {serial} | {p.ikea_article_number} | {p.part_name} | "
            f"{p.part_category.value} | {spec} | {item.quantity}件 | "
            f"{item.assembly_position} | {item.matching_basis[:40]}... | {price_str} |"
            if len(item.matching_basis) > 40
            else
            f"| {serial} | {p.ikea_article_number} | {p.part_name} | "
            f"{p.part_category.value} | {spec} | {item.quantity}件 | "
            f"{item.assembly_position} | {item.matching_basis} | {price_str} |"
        )

        bom_json.append({
            "part_serial_number": serial,
            "ikea_part_id": p.part_id,
            "ikea_article_number": p.ikea_article_number,
            "part_name": p.part_name,
            "part_category": p.part_category.value,
            "specification": spec,
            "quantity": item.quantity,
            "assembly_position": item.assembly_position,
            "matching_basis": item.matching_basis,
            "acquisition_channel": f"宜家官网 {p.ikea_url}" if p.ikea_url else "宜家门店",
            "price_cny": p.price_cny,
            "max_load_kg": p.max_load_kg,
        })
        serial += 1

    # 汇总行
    total_price = sum(
        (item.part.price_cny or 0) * item.quantity for item in solution.bom_items
    )
    total_qty = sum(item.quantity for item in solution.bom_items)
    md_lines.append(f"\n**零件总数量**: {total_qty}件  ")
    md_lines.append(f"**零件总参考价格**: ¥{total_price:.0f}（以宜家官方当前价格为准）  ")
    md_lines.append("\n> ⚠️ 所有零件来自宜家官方产品线。价格与产品规格以宜家官网（ikea.cn）最新信息为准。")

    md_text = "\n".join(md_lines)
    json_text = json.dumps(bom_json, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_text)

    logger.info(f"BOM生成完成: {md_path}")
    return md_text, json_text, md_path, json_path
