"""
零件分类与检索规则配置
定义各品类零件的标准字段、检索优先级、匹配规则
"""

# 家具结构拆解模板（按品类）
# 每个条目: {组件名: {角色, 零件分类, 是否必选, 数量规则, 检索优先字段}}
FURNITURE_STRUCTURE_TEMPLATES = {
    "桌子": [
        {
            "component": "桌面",
            "role": "主体承载面",
            "part_category": "板材件",
            "required": True,
            "quantity": 1,
            "search_fields": ["length_cm", "width_cm", "material", "max_load_kg"],
            "install_order": 3,
        },
        {
            "component": "桌腿",
            "role": "垂直支撑",
            "part_category": "结构件",
            "required": True,
            "quantity": 4,  # 默认4条桌腿，可被设计意图覆盖
            "search_fields": ["height_cm", "material", "max_load_kg", "adjustable"],
            "install_order": 1,
        },
        {
            "component": "连接件",
            "role": "零件连接固定",
            "part_category": "连接件",
            "required": True,
            "quantity": 8,  # 默认，按实际零件匹配后调整
            "search_fields": ["compatible_thickness_mm", "material"],
            "install_order": 2,
        },
        {
            "component": "脚垫",
            "role": "底部防滑保护",
            "part_category": "辅材件",
            "required": False,
            "quantity": 4,
            "search_fields": ["material"],
            "install_order": 4,
        },
    ]
}

# 功能件映射：用户功能需求关键词 -> 对应零件分类与检索条件
FUNCTION_PART_MAPPING = {
    "抽屉": {
        "part_category": "功能件",
        "keywords": ["抽屉", "drawer"],
        "search_fields": ["width_cm", "height_cm", "material"],
    },
    "走线孔": {
        "part_category": "功能件",
        "keywords": ["走线", "线孔", "cable"],
        "search_fields": ["material"],
    },
    "可调节高度": {
        "part_category": "结构件",
        "keywords": ["可调", "adjustable", "升降"],
        "search_fields": ["adjustable", "adjust_range_cm"],
    },
    "滑轮": {
        "part_category": "功能件",
        "keywords": ["滑轮", "脚轮", "caster"],
        "search_fields": ["material", "max_load_kg"],
    },
}

# 材质检索关键词标准化映射
MATERIAL_KEYWORD_MAP = {
    "实木颗粒板": ["颗粒板", "刨花板", "实木颗粒", "particle board", "particleboard"],
    "实木": ["实木", "solid wood", "solid beech", "实心木"],
    "桦木": ["桦木", "birch", "白桦"],
    "钢化玻璃": ["钢化玻璃", "tempered glass", "玻璃"],
    "钢": ["钢", "steel", "碳钢"],
    "不锈钢": ["不锈钢", "stainless steel"],
    "铝合金": ["铝合金", "aluminum", "aluminium"],
}
