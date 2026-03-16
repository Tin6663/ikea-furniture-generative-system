"""
宜家零件数据结构定义模块
IKEAPart: 标准化零件数据结构，所有零件数据必须来自本地SQLite数据库
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PartCategory(str, Enum):
    """零件分类枚举"""
    PANEL = "板材件"          # 桌面、桌板、侧板等
    STRUCTURAL = "结构件"     # 桌腿、支撑框架、横梁等
    CONNECTOR = "连接件"      # 螺丝、三合一连接件、滑轨等
    FUNCTIONAL = "功能件"     # 抽屉、走线孔、升降装置等
    AUXILIARY = "辅材件"      # 脚垫、防撞条、封边条等


class IKEAPart(BaseModel):
    """
    宜家标准化零件数据结构
    数据来源: 本地SQLite数据库（基于公开的宜家产品信息）
    """
    part_id: str = Field(..., description="数据库内部零件ID")
    ikea_article_number: str = Field(..., description="宜家产品货号（参考）")
    part_name: str = Field(..., description="零件官方名称（中文）")
    part_name_en: str = Field(default="", description="零件官方名称（英文/瑞典文）")
    part_category: PartCategory = Field(..., description="零件分类")
    description: str = Field(default="", description="零件描述")

    # 尺寸参数
    length_cm: Optional[float] = Field(None, description="长度，单位cm")
    width_cm: Optional[float] = Field(None, description="宽度，单位cm")
    height_cm: Optional[float] = Field(None, description="高度/厚度，单位cm")
    thickness_cm: Optional[float] = Field(None, description="厚度，单位cm，适用于板材")

    # 承重与材质
    max_load_kg: Optional[float] = Field(None, description="最大承重，单位kg")
    material: str = Field(..., description="主要材质")
    color: str = Field(default="", description="颜色")
    surface_treatment: str = Field(default="", description="表面处理工艺")

    # 适配参数
    compatible_thickness_mm: Optional[float] = Field(
        None, description="适配板材厚度，单位mm，适用于连接件"
    )
    compatible_part_ids: List[str] = Field(
        default_factory=list, description="可适配的零件ID列表"
    )
    install_method: str = Field(default="", description="安装方式描述")

    # 采购信息
    price_cny: Optional[float] = Field(None, description="参考价格，人民币元")
    ikea_url: str = Field(default="", description="宜家官方产品页链接")
    is_available: bool = Field(default=True, description="是否当前可购买")

    # 工程参数
    adjustable: bool = Field(default=False, description="是否可调节高度")
    adjust_range_cm: Optional[str] = Field(None, description="可调节范围，如60-90cm")
    requires_tools: str = Field(default="", description="安装所需工具")
    package_weight_kg: Optional[float] = Field(None, description="包装重量kg")

    # 附加参数（不同品类不同）
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="品类特有扩展参数"
    )

    def get_dimension_str(self) -> str:
        """返回尺寸的文字描述"""
        parts = []
        if self.length_cm:
            parts.append(f"长{self.length_cm}cm")
        if self.width_cm:
            parts.append(f"宽{self.width_cm}cm")
        if self.height_cm:
            parts.append(f"高{self.height_cm}cm")
        if self.thickness_cm:
            parts.append(f"厚{self.thickness_cm}cm")
        return " × ".join(parts) if parts else "尺寸未知"

    def to_bom_dict(self) -> dict:
        """返回BOM清单所需的字段字典"""
        return {
            "ikea_article_number": self.ikea_article_number,
            "part_name": self.part_name,
            "part_category": self.part_category.value,
            "specification": self.get_dimension_str() + f" | {self.material}",
            "max_load_kg": self.max_load_kg,
            "price_cny": self.price_cny,
            "ikea_url": self.ikea_url,
        }


class PartMatchResult(BaseModel):
    """零件匹配结果，包含匹配的零件与匹配依据"""
    part: IKEAPart
    assembly_position: str = Field(..., description="装配位置，如桌面主体")
    quantity: int = Field(default=1, description="所需数量")
    matching_basis: str = Field(..., description="匹配依据说明")
    match_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="匹配评分，1.0为完全匹配"
    )
