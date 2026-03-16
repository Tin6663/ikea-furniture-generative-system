"""
宜家零件本地数据库初始化脚本
数据说明：
  - 所有产品均为宜家（IKEA）官方真实在售或历史在售产品
  - 产品名称、材质、尺寸基于宜家官网公开信息整理
  - 货号(article_number)仅供参考，请以宜家官网最新数据为准
  - 价格为参考价，以宜家官方当前定价为准
  - 本数据库仅收录与桌类家具组装强相关的零件/产品
运行方式: python3 data/init_db.py
"""

import sqlite3
import os
import sys

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import DB_PATH


def init_database():
    """初始化数据库，建表并插入初始零件数据"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── 建表 ──────────────────────────────────────────────────────────────
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS ikea_parts (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        part_id                 TEXT UNIQUE NOT NULL,
        ikea_article_number     TEXT NOT NULL,
        part_name               TEXT NOT NULL,
        part_name_en            TEXT DEFAULT '',
        part_category           TEXT NOT NULL,
        description             TEXT DEFAULT '',
        length_cm               REAL,
        width_cm                REAL,
        height_cm               REAL,
        thickness_cm            REAL,
        max_load_kg             REAL,
        material                TEXT NOT NULL,
        color                   TEXT DEFAULT '',
        surface_treatment       TEXT DEFAULT '',
        compatible_thickness_mm REAL,
        install_method          TEXT DEFAULT '',
        price_cny               REAL,
        ikea_url                TEXT DEFAULT '',
        is_available            INTEGER DEFAULT 1,
        adjustable              INTEGER DEFAULT 0,
        adjust_range_cm         TEXT DEFAULT '',
        requires_tools          TEXT DEFAULT '',
        package_weight_kg       REAL,
        extra_params            TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS part_compatibility (
        part_id         TEXT NOT NULL,
        compatible_id   TEXT NOT NULL,
        PRIMARY KEY (part_id, compatible_id)
    );
    """)

    # ── 宜家零件数据 ──────────────────────────────────────────────────────
    # 数据来源：宜家中国官网公开产品页面（ikea.cn）
    # 最后核验日期：2024年
    parts_data = [

        # ================================================================
        # 板材件 - 桌面 (LINNMON / GERTON系列)
        # ================================================================
        {
            "part_id": "PANEL_LINNMON_120_60_W",
            "ikea_article_number": "002.513.09",
            "part_name": "LINNMON 利蒙 桌面 白色",
            "part_name_en": "LINNMON Table top, white",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色，适合与ADILS、OLOV等桌腿搭配使用",
            "length_cm": 120.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "compatible_thickness_mm": None,
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 179.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/linnmon-li-meng-zhuo-mian-bai-se-00251309/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具或内六角扳手",
            "package_weight_kg": 14.0,
        },
        {
            "part_id": "PANEL_LINNMON_150_75_W",
            "ikea_article_number": "103.397.65",
            "part_name": "LINNMON 利蒙 桌面 白色 150×75cm",
            "part_name_en": "LINNMON Table top, white, 150x75cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色，150×75cm，适合较宽的工作台或餐桌",
            "length_cm": 150.0, "width_cm": 75.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 249.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/linnmon-li-meng-zhuo-mian-bai-se-10339765/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 19.0,
        },
        {
            "part_id": "PANEL_LINNMON_100_60_W",
            "ikea_article_number": "903.397.61",
            "part_name": "LINNMON 利蒙 桌面 白色 100×60cm",
            "part_name_en": "LINNMON Table top, white, 100x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色，100×60cm，小户型首选",
            "length_cm": 100.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 149.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/linnmon-li-meng-zhuo-mian-bai-se-90339761/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 11.0,
        },
        {
            "part_id": "PANEL_LINNMON_120_60_BB",
            "ikea_article_number": "702.513.15",
            "part_name": "LINNMON 利蒙 桌面 黑褐色 120×60cm",
            "part_name_en": "LINNMON Table top, black-brown, 120x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，黑褐色，120×60cm，深色系风格",
            "length_cm": 120.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "黑褐色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 179.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/linnmon-li-meng-zhuo-mian-hei-he-se-70251315/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 14.0,
        },
        {
            "part_id": "PANEL_GERTON_155_75",
            "ikea_article_number": "104.839.62",
            "part_name": "GERTON 格顿 桌面 实木山毛榉",
            "part_name_en": "GERTON Table top, beech, 155x75cm",
            "part_category": "板材件",
            "description": "实心山毛榉木桌面，155×75cm，天然木纹，高承重，适合重度使用场景",
            "length_cm": 155.0, "width_cm": 75.0, "height_cm": None, "thickness_cm": 3.0,
            "max_load_kg": 75.0,
            "material": "实木", "color": "山毛榉原木色",
            "surface_treatment": "透明清漆",
            "install_method": "与桌腿或支架通过螺栓连接",
            "price_cny": 999.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/gerton-ge-dun-zhuo-mian-shan-mao-ju-10483962/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 30.0,
        },

        # ================================================================
        # 结构件 - 桌腿 (ADILS / OLOV / CAPITA系列)
        # ================================================================
        {
            "part_id": "STRUCT_ADILS_LEG_BLK",
            "ikea_article_number": "702.513.83",
            "part_name": "ADILS 阿迪斯 桌腿 黑色",
            "part_name_en": "ADILS Leg, black",
            "part_category": "结构件",
            "description": "钢制圆管桌腿，高70cm，黑色，适配LINNMON等大多数宜家桌面，单腿承重约50kg，4腿整桌承重200kg",
            "length_cm": None, "width_cm": None, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "黑色",
            "surface_treatment": "粉末喷涂",
            "install_method": "直接拧入桌面预埋螺母，无需额外工具",
            "price_cny": 30.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/adils-a-di-si-zhuo-tui-hei-se-70251383/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具（手拧）",
            "package_weight_kg": 1.5,
        },
        {
            "part_id": "STRUCT_ADILS_LEG_WHT",
            "ikea_article_number": "202.513.81",
            "part_name": "ADILS 阿迪斯 桌腿 白色",
            "part_name_en": "ADILS Leg, white",
            "part_category": "结构件",
            "description": "钢制圆管桌腿，高70cm，白色，与白色桌面完美搭配",
            "length_cm": None, "width_cm": None, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "白色",
            "surface_treatment": "粉末喷涂",
            "install_method": "直接拧入桌面预埋螺母，无需额外工具",
            "price_cny": 30.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/adils-a-di-si-zhuo-tui-bai-se-20251381/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具（手拧）",
            "package_weight_kg": 1.5,
        },
        {
            "part_id": "STRUCT_OLOV_ADJ_BLK",
            "ikea_article_number": "302.537.16",
            "part_name": "OLOV 奥洛夫 可调式桌腿 黑色",
            "part_name_en": "OLOV Leg, black, adjustable",
            "part_category": "结构件",
            "description": "钢制可调节高度桌腿，高度范围60-90cm，黑色，适合需要高度灵活调节的桌子",
            "length_cm": None, "width_cm": None, "height_cm": 75.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "黑色",
            "surface_treatment": "粉末喷涂",
            "install_method": "拧入桌面预埋螺母，旋转底部调节高度",
            "price_cny": 69.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/olov-ao-luo-fu-ke-diao-shi-zhuo-tui-hei-se-30253716/",
            "is_available": 1, "adjustable": 1,
            "adjust_range_cm": "60-90",
            "requires_tools": "无需工具（手拧调节）",
            "package_weight_kg": 2.5,
        },
        {
            "part_id": "STRUCT_OLOV_ADJ_WHT",
            "ikea_article_number": "902.537.14",
            "part_name": "OLOV 奥洛夫 可调式桌腿 白色",
            "part_name_en": "OLOV Leg, white, adjustable",
            "part_category": "结构件",
            "description": "钢制可调节高度桌腿，高度范围60-90cm，白色",
            "length_cm": None, "width_cm": None, "height_cm": 75.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "白色",
            "surface_treatment": "粉末喷涂",
            "install_method": "拧入桌面预埋螺母，旋转底部调节高度",
            "price_cny": 69.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/olov-ao-luo-fu-ke-diao-shi-zhuo-tui-bai-se-90253714/",
            "is_available": 1, "adjustable": 1,
            "adjust_range_cm": "60-90",
            "requires_tools": "无需工具（手拧调节）",
            "package_weight_kg": 2.5,
        },
        {
            "part_id": "STRUCT_CAPITA_LEG_10CM",
            "ikea_article_number": "902.816.69",
            "part_name": "CAPITA 卡必达 桌腿 不锈钢色",
            "part_name_en": "CAPITA Leg, stainless steel color",
            "part_category": "结构件",
            "description": "不锈钢色桌腿，高10cm，通常用于抬高柜体底部，也可4个组合作矮桌腿使用",
            "length_cm": None, "width_cm": None, "height_cm": 10.0, "thickness_cm": None,
            "max_load_kg": 100.0,
            "material": "不锈钢", "color": "不锈钢色",
            "surface_treatment": "拉丝处理",
            "install_method": "自攻螺丝安装于柜体底部",
            "price_cny": 99.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/capita-ka-bi-da-zhuo-tui-bu-xiu-gang-se-90281669/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "十字螺丝刀",
            "package_weight_kg": 0.5,
        },

        # ================================================================
        # 功能件 - 抽屉单元 (ALEX系列)
        # ================================================================
        {
            "part_id": "FUNC_ALEX_DRAWER_WHITE",
            "ikea_article_number": "104.736.43",
            "part_name": "ALEX 亚历克斯 抽屉单元 白色",
            "part_name_en": "ALEX Drawer unit, white",
            "part_category": "功能件",
            "description": "实木颗粒板抽屉单元，36×70×58cm（宽×高×深），含5个抽屉，可置于桌面下方。注意：该产品本身带腿，可直接落地使用",
            "length_cm": 36.0, "width_cm": 58.0, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 40.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "独立落地摆放于桌面旁边或下方，需配合足够高度的桌腿",
            "price_cny": 699.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/alex-ya-li-ke-si-chou-ti-dan-yuan-bai-se-10473643/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手（组装时）",
            "package_weight_kg": 28.0,
        },
        {
            "part_id": "FUNC_ALEX_DRAWER_GREY",
            "ikea_article_number": "404.791.90",
            "part_name": "ALEX 亚历克斯 抽屉单元 灰色",
            "part_name_en": "ALEX Drawer unit, grey",
            "part_category": "功能件",
            "description": "实木颗粒板抽屉单元，36×70×58cm，含5个抽屉，灰色",
            "length_cm": 36.0, "width_cm": 58.0, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 40.0,
            "material": "实木颗粒板", "color": "灰色",
            "surface_treatment": "纸质贴面",
            "install_method": "独立落地摆放于桌面旁边或下方",
            "price_cny": 699.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/alex-ya-li-ke-si-chou-ti-dan-yuan-hui-se-40479190/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 28.0,
        },

        # ================================================================
        # 功能件 - 走线孔 / 电缆管理
        # ================================================================
        {
            "part_id": "FUNC_SIGNUM_CABLE",
            "ikea_article_number": "502.822.87",
            "part_name": "SIGNUM 西格纳姆 电线管理导轨 银色",
            "part_name_en": "SIGNUM Cable management, horizontal, silver color",
            "part_category": "功能件",
            "description": "水平电线管理导轨，可安装于桌面下方，整理整理电线，长70cm，银色",
            "length_cm": 70.0, "width_cm": 8.0, "height_cm": 6.0, "thickness_cm": None,
            "max_load_kg": None,
            "material": "钢", "color": "银色",
            "surface_treatment": "镀铬",
            "install_method": "螺丝固定于桌面下方（含安装螺丝）",
            "price_cny": 49.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/signum-xi-ge-na-mu-dian-xian-guan-li-dao-gui-shui-ping-yin-se-50282287/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "十字螺丝刀",
            "package_weight_kg": 0.9,
        },

        # ================================================================
        # 连接件 - IKEA通用五金连接件
        # ================================================================
        {
            "part_id": "CONN_EKBY_BRACKET",
            "ikea_article_number": "000.627.85",
            "part_name": "EKBY 埃克比 托架 白色",
            "part_name_en": "EKBY Bracket, white",
            "part_category": "连接件",
            "description": "钢制L形托架，适配16-19mm厚板材，用于搁板与墙面的连接固定，每个承重25kg",
            "length_cm": 19.0, "width_cm": 19.0, "height_cm": None, "thickness_cm": None,
            "max_load_kg": 25.0,
            "material": "钢", "color": "白色",
            "surface_treatment": "粉末喷涂",
            "compatible_thickness_mm": 16.0,
            "install_method": "墙面膨胀螺丝固定，配合搁板使用",
            "price_cny": 15.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/ekby-ai-ke-bi-tuo-jia-bai-se-00062785/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "电钻、十字螺丝刀",
            "package_weight_kg": 0.3,
        },
        {
            "part_id": "CONN_FIXA_SCREWS",
            "ikea_article_number": "601.229.90",
            "part_name": "FIXA 菲克萨 螺丝套装",
            "part_name_en": "FIXA Screw set",
            "part_category": "连接件",
            "description": "通用家具组装螺丝套装，包含多种尺寸螺丝和螺母，适配宜家大多数板式家具的板材厚度（16-18mm），每套约160件",
            "length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None,
            "max_load_kg": None,
            "material": "钢", "color": "金属色",
            "surface_treatment": "镀锌",
            "compatible_thickness_mm": 16.0,
            "install_method": "螺丝刀拧入，适用于木质板材",
            "price_cny": 35.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/fixa-fei-ke-sa-luo-si-tao-zhuang-60122990/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "十字螺丝刀",
            "package_weight_kg": 0.3,
        },
        {
            "part_id": "CONN_ADILS_BOLT",
            "ikea_article_number": "117.936.36",
            "part_name": "ADILS 阿迪斯 桌腿固定螺栓套装",
            "part_name_en": "ADILS leg mounting hardware",
            "part_category": "连接件",
            "description": "专用于ADILS/OLOV桌腿与LINNMON等桌面连接的固定螺栓，每套含4个螺栓，适配桌面预埋螺母",
            "length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "金属色",
            "surface_treatment": "镀锌",
            "compatible_thickness_mm": 34.0,
            "install_method": "手拧（无需工具）",
            "price_cny": 15.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具",
            "package_weight_kg": 0.2,
        },

        # ================================================================
        # 辅材件 - 脚垫 / 防滑
        # ================================================================
        {
            "part_id": "AUX_FIXA_FOOTPAD",
            "ikea_article_number": "703.028.10",
            "part_name": "FIXA 菲克萨 自粘式脚垫 透明",
            "part_name_en": "FIXA Self-adhesive floor protector, transparent",
            "part_category": "辅材件",
            "description": "EVA材质自粘式脚垫，透明色，直径25mm，一套20个，防止桌腿刮伤地板、减少噪音",
            "length_cm": None, "width_cm": None, "height_cm": 0.4, "thickness_cm": None,
            "max_load_kg": None,
            "material": "EVA", "color": "透明",
            "surface_treatment": "自粘背胶",
            "install_method": "撕去背胶直接粘贴于桌腿底部",
            "price_cny": 10.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/fixa-fei-ke-sa-zi-zhan-shi-jiao-dian-tou-ming-70302810/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具",
            "package_weight_kg": 0.1,
        },
        {
            "part_id": "AUX_FIXA_FELT_PAD",
            "ikea_article_number": "002.917.41",
            "part_name": "FIXA 菲克萨 毡制脚垫 白色",
            "part_name_en": "FIXA Felt pads, white",
            "part_category": "辅材件",
            "description": "羊毛毡材质脚垫，白色，多尺寸，一套69个，有效保护木质/瓷砖地板",
            "length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None,
            "max_load_kg": None,
            "material": "羊毛毡", "color": "白色",
            "surface_treatment": "自粘背胶",
            "install_method": "撕去背胶粘贴于家具底部",
            "price_cny": 19.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/fixa-fei-ke-sa-zhan-zhi-jiao-dian-bai-se-00291741/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具",
            "package_weight_kg": 0.1,
        },
    ]

    # ── 插入数据 ──────────────────────────────────────────────────────────
    insert_sql = """
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

    inserted = 0
    for p in parts_data:
        # 确保所有字段存在
        defaults = {
            "adjust_range_cm": "", "requires_tools": "",
            "surface_treatment": "", "install_method": "",
            "color": "", "description": "", "part_name_en": "",
            "ikea_url": "", "compatible_thickness_mm": None,
            "package_weight_kg": None,
        }
        for k, v in defaults.items():
            p.setdefault(k, v)
        cur.execute(insert_sql, p)
        inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成：{DB_PATH}")
    print(f"   共插入 {inserted} 条零件数据")
    return DB_PATH


if __name__ == "__main__":
    init_database()
