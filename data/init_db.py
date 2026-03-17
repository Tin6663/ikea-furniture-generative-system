"""
宜家零件本地数据库初始化脚本

【数据说明】
  - 所有产品均为宜家（IKEA）官方真实在售或历史在售产品
  - 产品名称、材质、尺寸基于宜家中国官网（ikea.cn）公开信息整理
  - 货号(article_number)仅供参考，请以宜家官网最新数据为准
  - 价格为参考价（截至数据整理时），以宜家官方当前定价为准
  - 本数据库仅收录与桌类家具组装强相关的零件/产品

【数据来源渠道】
  1. 宜家中国官网（主要来源）：https://www.ikea.cn
     - 产品页：https://www.ikea.cn/cn/zh/cat/zhuo-mian-10785/（桌面分类）
     - 产品页：https://www.ikea.cn/cn/zh/cat/zhuo-tui-10786/（桌腿分类）
  2. 宜家非官方API（可编程获取）：
     - 搜索：https://sik.search.blue.cdtapps.com/cn/zh/search-result-page?q={关键词}
     - 使用 data/fetch_ikea_data.py 脚本自动抓取，详见脚本注释
  3. 宜家全球官网：https://www.ikea.com（国际市场参考）

【运行方式】
  python3 data/init_db.py          # 初始化/重置基础数据
  python3 data/fetch_ikea_data.py  # 从IKEA官网实时更新数据（需联网）
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

        # ================================================================
        # 板材件 - LAGKAPTEN 系列桌面（LINNMON 的升级替代系列）
        # 数据来源：宜家中国官网 ikea.cn，2024年整理
        # ================================================================
        {
            "part_id": "PANEL_LAGKAPTEN_120_60_W",
            "ikea_article_number": "504.946.74",
            "part_name": "LAGKAPTEN 拉格卡普腾 桌面 白色 120×60cm",
            "part_name_en": "LAGKAPTEN Table top, white, 120x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色纸质贴面，120×60cm，LINNMON系列的升级版，厚度一致，可与ADILS/OLOV桌腿配合使用",
            "length_cm": 120.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 199.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/lagkapten-la-ge-ka-pu-teng-zhuo-mian-bai-se-50494674/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 14.0,
        },
        {
            "part_id": "PANEL_LAGKAPTEN_140_60_W",
            "ikea_article_number": "404.946.63",
            "part_name": "LAGKAPTEN 拉格卡普腾 桌面 白色 140×60cm",
            "part_name_en": "LAGKAPTEN Table top, white, 140x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色，140×60cm，适合需要更大桌面的工作场景",
            "length_cm": 140.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 229.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/lagkapten-la-ge-ka-pu-teng-zhuo-mian-bai-se-40494663/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 17.0,
        },
        {
            "part_id": "PANEL_LAGKAPTEN_200_60_W",
            "ikea_article_number": "104.946.58",
            "part_name": "LAGKAPTEN 拉格卡普腾 桌面 白色 200×60cm",
            "part_name_en": "LAGKAPTEN Table top, white, 200x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，白色，200×60cm，适合L形转角桌或多人共用工作台",
            "length_cm": 200.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 299.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/lagkapten-la-ge-ka-pu-teng-zhuo-mian-bai-se-10494658/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 24.0,
        },
        {
            "part_id": "PANEL_LAGKAPTEN_120_60_DG",
            "ikea_article_number": "204.946.79",
            "part_name": "LAGKAPTEN 拉格卡普腾 桌面 深灰色 120×60cm",
            "part_name_en": "LAGKAPTEN Table top, dark grey, 120x60cm",
            "part_category": "板材件",
            "description": "实木颗粒板桌面，深灰色，120×60cm，现代工业风格",
            "length_cm": 120.0, "width_cm": 60.0, "height_cm": None, "thickness_cm": 3.4,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "深灰色",
            "surface_treatment": "纸质贴面",
            "install_method": "与桌腿通过螺栓连接",
            "price_cny": 199.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/lagkapten-la-ge-ka-pu-teng-zhuo-mian-shen-hui-se-20494679/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 14.0,
        },

        # ================================================================
        # 板材件 - KARLBY 系列（高端台面，常用于站立式工作台）
        # 数据来源：宜家中国官网 ikea.cn，2024年整理
        # ================================================================
        {
            "part_id": "PANEL_KARLBY_186_63",
            "ikea_article_number": "303.852.67",
            "part_name": "KARLBY 卡尔比 台面 胡桃木贴皮 186×63.5cm",
            "part_name_en": "KARLBY Countertop, walnut veneer, 186x63.5cm",
            "part_category": "板材件",
            "description": "高密度实木颗粒板芯材，表面胡桃木薄木贴皮，厚3.8cm，承重力强。常与ALEX抽屉柜或BEKANT框架组合为高端工作站",
            "length_cm": 186.0, "width_cm": 63.5, "height_cm": None, "thickness_cm": 3.8,
            "max_load_kg": 50.0,
            "material": "实木颗粒板", "color": "胡桃木色",
            "surface_treatment": "胡桃木薄木贴皮，清漆表面",
            "install_method": "与桌腿或抽屉柜顶端固定，可用SIGNUM导轨固定",
            "price_cny": 1299.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/karlby-ka-er-bi-tai-mian-hu-tao-mu-30385267/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 38.0,
        },

        # ================================================================
        # 结构件 - HILVER 系列桌腿（锥形实木桌腿）
        # 数据来源：宜家中国官网 ikea.cn，2024年整理
        # ================================================================
        {
            "part_id": "STRUCT_HILVER_LEG_70_BCHCLR",
            "ikea_article_number": "903.498.00",
            "part_name": "HILVER 希尔弗 桌腿 竹色 70cm",
            "part_name_en": "HILVER Leg, bamboo, 70cm",
            "part_category": "结构件",
            "description": "锥形实木（竹）桌腿，高70cm，无漆原色，自然现代风格。适配LINNMON、LAGKAPTEN等宜家桌面，4腿组合整体承重约200kg",
            "length_cm": None, "width_cm": None, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "竹", "color": "竹原色",
            "surface_treatment": "清漆",
            "install_method": "拧入桌面预埋螺母，手拧即可",
            "price_cny": 69.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/hilver-xi-er-fu-zhuo-tui-zhu-90349800/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具（手拧）",
            "package_weight_kg": 1.8,
        },
        {
            "part_id": "STRUCT_HILVER_LEG_70_BLK",
            "ikea_article_number": "204.364.52",
            "part_name": "HILVER 希尔弗 桌腿 黑色 70cm",
            "part_name_en": "HILVER Leg, black, 70cm",
            "part_category": "结构件",
            "description": "锥形实木桌腿，黑色喷漆，高70cm，适配LINNMON、LAGKAPTEN等宜家桌面",
            "length_cm": None, "width_cm": None, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "实木", "color": "黑色",
            "surface_treatment": "黑色哑光喷漆",
            "install_method": "拧入桌面预埋螺母",
            "price_cny": 69.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/hilver-xi-er-fu-zhuo-tui-hei-se-20436452/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具（手拧）",
            "package_weight_kg": 1.8,
        },

        # ================================================================
        # 结构件 - LERBERG 系列（A形搁架/桌腿支架）
        # 数据来源：宜家中国官网 ikea.cn，2024年整理
        # ================================================================
        {
            "part_id": "STRUCT_LERBERG_TRESTLE_GY",
            "ikea_article_number": "802.523.03",
            "part_name": "LERBERG 勒贝里 搁架腿 灰色",
            "part_name_en": "LERBERG Trestle, grey",
            "part_category": "结构件",
            "description": "A形金属支架，高70cm，底部宽度67cm，灰色粉末喷涂。两个配合使用可支撑GERTON/LAGKAPTEN等宽幅桌面，单个承重50kg",
            "length_cm": 67.0, "width_cm": None, "height_cm": 70.0, "thickness_cm": None,
            "max_load_kg": 50.0,
            "material": "钢", "color": "灰色",
            "surface_treatment": "粉末喷涂",
            "install_method": "两个支架置于桌面两端，无需固定即可使用（可选螺丝固定）",
            "price_cny": 149.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/lerberg-le-bei-li-ge-jia-tui-hui-se-80252303/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具",
            "package_weight_kg": 5.5,
        },

        # ================================================================
        # 结构件 - BEKANT 系列桌架（可调节高度框架）
        # 数据来源：宜家中国官网 ikea.cn，2024年整理
        # ================================================================
        {
            "part_id": "STRUCT_BEKANT_FRAME_ELEC",
            "ikea_article_number": "792.822.52",
            "part_name": "BEKANT 贝肯特 电动升降桌架 白色",
            "part_name_en": "BEKANT Underframe for table top, sit/stand, white",
            "part_category": "结构件",
            "description": "电动升降桌框架，高度可在60–125cm范围内调节，白色，含两套电动支腿，需配合宜家桌面使用（适合120×80cm桌面）。支持坐立两用工作场景",
            "length_cm": None, "width_cm": None, "height_cm": 92.5, "thickness_cm": None,
            "max_load_kg": 70.0,
            "material": "钢", "color": "白色",
            "surface_treatment": "粉末喷涂",
            "install_method": "螺丝固定于桌面底部，内附说明书",
            "price_cny": 3999.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/bekant-bei-ken-te-dian-dong-sheng-jiang-zhuo-jia-bai-se-79282252/",
            "is_available": 1, "adjustable": 1,
            "adjust_range_cm": "60-125",
            "requires_tools": "内六角扳手、十字螺丝刀",
            "package_weight_kg": 45.0,
        },

        # ================================================================
        # 功能件 - LAGKAPTEN/ALEX 组合用抽屉（ALEX单抽款）
        # ================================================================
        {
            "part_id": "FUNC_ALEX_DRAWER_1_WHITE",
            "ikea_article_number": "603.397.91",
            "part_name": "ALEX 亚历克斯 单抽屉 白色",
            "part_name_en": "ALEX Drawer unit with 1 drawer, white",
            "part_category": "功能件",
            "description": "实木颗粒板单抽屉单元，白色，36×58cm（宽×深），高30cm，可置于桌面下用于收纳键盘/文件",
            "length_cm": 36.0, "width_cm": 58.0, "height_cm": 30.0, "thickness_cm": None,
            "max_load_kg": 15.0,
            "material": "实木颗粒板", "color": "白色",
            "surface_treatment": "纸质贴面",
            "install_method": "可直接落地或搭配支腿使用",
            "price_cny": 299.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/alex-ya-li-ke-si-dan-chou-ti-dan-yuan-bai-se-60339791/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "内六角扳手",
            "package_weight_kg": 10.0,
        },

        # ================================================================
        # 连接件 - FIXA 三合一连接件（板式家具通用）
        # ================================================================
        {
            "part_id": "CONN_FIXA_3IN1_BOLT",
            "ikea_article_number": "501.229.80",
            "part_name": "FIXA 菲克萨 三合一连接件套装",
            "part_name_en": "FIXA 3-in-1 furniture connector set",
            "part_category": "连接件",
            "description": "宜家通用三合一家具连接件，适配16-18mm厚板材，用于板式家具侧板与横板之间的固定，隐藏式安装，每套20组",
            "length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None,
            "max_load_kg": None,
            "material": "锌合金", "color": "金属色",
            "surface_treatment": "镀镍",
            "compatible_thickness_mm": 16.0,
            "install_method": "需用电钻预钻孔后安装",
            "price_cny": 25.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/fixa-fei-ke-sa-san-he-yi-lian-jie-jian-tao-zhuang-50122980/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "电钻、一字螺丝刀",
            "package_weight_kg": 0.2,
        },
        {
            "part_id": "CONN_UTRUSTA_HINGE",
            "ikea_article_number": "802.917.01",
            "part_name": "UTRUSTA 乌斯塔 暗铰链 110°",
            "part_name_en": "UTRUSTA Hinge, 110°",
            "part_category": "连接件",
            "description": "杯形暗铰链，开合角度110°，适配宜家板材厚度15-20mm，用于桌子盖板或门板连接，软关闭功能，一套含2个铰链",
            "length_cm": None, "width_cm": None, "height_cm": None, "thickness_cm": None,
            "max_load_kg": 10.0,
            "material": "钢", "color": "银色",
            "surface_treatment": "镀镍",
            "compatible_thickness_mm": 16.0,
            "install_method": "杯孔直径35mm，需预钻孔",
            "price_cny": 29.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/utrusta-wu-si-ta-an-jiao-lian-110-80291701/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "电钻（35mm钻头）、十字螺丝刀",
            "package_weight_kg": 0.1,
        },

        # ================================================================
        # 辅材件 - RILL 脚轮（可移动桌子）
        # ================================================================
        {
            "part_id": "AUX_RILL_CASTER",
            "ikea_article_number": "702.179.16",
            "part_name": "RILL 里尔 脚轮",
            "part_name_en": "RILL Caster",
            "part_category": "辅材件",
            "description": "万向脚轮，直径75mm，附带制动器，适配宜家大多数带螺纹插脚的桌腿，可将固定式桌腿改为可移动桌子，最大承重30kg/个",
            "length_cm": None, "width_cm": None, "height_cm": 7.5, "thickness_cm": None,
            "max_load_kg": 30.0,
            "material": "塑料", "color": "黑色",
            "surface_treatment": "哑光",
            "install_method": "直接插入空心桌腿底部（适配ADILS/OLOV等螺纹腿）",
            "price_cny": 49.0,
            "ikea_url": "https://www.ikea.cn/cn/zh/p/rill-li-er-jiao-lun-70217916/",
            "is_available": 1, "adjustable": 0,
            "requires_tools": "无需工具",
            "package_weight_kg": 0.3,
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
