"""
结构方案数据结构定义模块
StructureSolution: 零件匹配与装配关系的完整描述
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from models.part_model import PartMatchResult, IKEAPart


class AssemblyRelation(BaseModel):
    """装配关系：描述两个零件之间的连接方式"""
    parent_position: str = Field(..., description="父零件装配位置")
    child_position: str = Field(..., description="子零件装配位置")
    connection_type: str = Field(..., description="连接方式，如螺栓连接、卡扣连接")
    connector_part_id: Optional[str] = Field(
        None, description="使用的连接件零件ID（若有）"
    )
    spatial_description: str = Field(default="", description="空间位置描述")


class StructureComponent(BaseModel):
    """结构组件：家具的一个层级结构单元"""
    component_name: str = Field(..., description="结构组件名称，如桌面组件")
    component_role: str = Field(..., description="组件功能角色，如支撑/储物/连接")
    matched_part: PartMatchResult = Field(..., description="匹配到的宜家零件")
    sub_components: List["StructureComponent"] = Field(
        default_factory=list, description="子组件列表"
    )
    install_order: int = Field(..., description="安装顺序序号")
    notes: str = Field(default="", description="安装备注")


class ValidationReport(BaseModel):
    """工程校验报告"""
    passed: bool = Field(..., description="是否通过所有校验")
    load_check: bool = Field(default=False, description="承重校验是否通过")
    dimension_check: bool = Field(default=False, description="尺寸匹配校验是否通过")
    assembly_check: bool = Field(default=False, description="可装配性校验是否通过")
    material_check: bool = Field(default=False, description="材料兼容性校验是否通过")
    failed_items: List[str] = Field(
        default_factory=list, description="未通过的校验项描述"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="修改建议列表"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="各校验项的详细计算数据"
    )


class StructureSolution(BaseModel):
    """
    家具结构方案完整数据结构
    包含所有零件匹配结果、装配关系、工程校验结果
    """
    solution_id: str = Field(..., description="方案唯一ID")
    ir_id: str = Field(..., description="对应的设计意图IR ID")
    create_time: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # 结构组件树
    components: List[StructureComponent] = Field(
        default_factory=list, description="顶层结构组件列表"
    )

    # 装配关系列表
    assembly_relations: List[AssemblyRelation] = Field(
        default_factory=list, description="零件间的装配关系"
    )

    # 汇总BOM（平铺的零件清单，含数量）
    bom_items: List[PartMatchResult] = Field(
        default_factory=list, description="BOM物料清单，含所有零件与数量"
    )

    # 工程校验结果
    validation_report: Optional[ValidationReport] = Field(
        None, description="工程校验报告，校验后填充"
    )

    # 汇总统计
    total_parts_count: int = Field(default=0, description="零件总数量")
    total_price_cny: Optional[float] = Field(None, description="零件总参考价格")
    estimated_assembly_minutes: int = Field(
        default=60, description="预计组装时长（分钟）"
    )
    required_tools: List[str] = Field(
        default_factory=list, description="所需工具清单"
    )

    def get_all_parts(self) -> List[PartMatchResult]:
        """返回所有零件匹配结果（去重）"""
        return self.bom_items

    def get_total_actual_load_kg(self) -> float:
        """估算结构总承重能力（取最弱承重链）"""
        min_load = float('inf')
        for item in self.bom_items:
            if item.part.max_load_kg is not None and item.part.part_category.value in ["结构件", "板材件"]:
                per_unit = item.part.max_load_kg * item.quantity
                if per_unit < min_load:
                    min_load = per_unit
        return min_load if min_load != float('inf') else 0.0
