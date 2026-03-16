"""
设计意图数据结构定义模块
DesignIntentIR: 系统全流程唯一输入数据结构，基于Pydantic定义
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class OverallDimensions(BaseModel):
    """整体尺寸规格"""
    length: float = Field(..., description="长度，单位cm", gt=0)
    width: float = Field(..., description="宽度，单位cm", gt=0)
    height: float = Field(..., description="高度，单位cm", gt=0)
    tolerance: float = Field(default=0.5, description="公差，单位cm")


class LoadRequirement(BaseModel):
    """承重需求"""
    overall_load: float = Field(..., description="整体承重，单位kg", gt=0)
    partial_load: Dict[str, float] = Field(
        default_factory=dict,
        description="局部承重，键为部位名称，值为承重量kg"
    )


class FurnitureBaseInfo(BaseModel):
    """家具基础信息"""
    category: str = Field(..., description="家具品类，如桌子")
    sub_category: str = Field(default="", description="子品类，如电脑桌、书桌、餐桌")
    overall_dimensions: OverallDimensions
    main_material: str = Field(..., description="主体材质，如实木颗粒板、实木、钢化玻璃")
    load_requirement: LoadRequirement


class FunctionalRequirement(BaseModel):
    """功能需求单项"""
    function_name: str = Field(..., description="功能名称")
    function_desc: str = Field(default="", description="功能描述")
    constraint_params: Dict[str, Any] = Field(
        default_factory=dict, description="量化参数字典"
    )


class StructuralConstraints(BaseModel):
    """结构约束"""
    structure_type: str = Field(default="框架式", description="结构类型")
    component_list: List[str] = Field(
        default_factory=list, description="结构组件列表，如桌面、桌腿"
    )
    special_constraints: List[str] = Field(
        default_factory=list, description="特殊约束，如圆角桌面、4条桌腿"
    )


class AssemblyConstraints(BaseModel):
    """装配约束"""
    tool_requirement: str = Field(
        default="普通家用工具", description="工具要求"
    )
    assembly_difficulty: Optional[str] = Field(
        default="简单", description="难度等级：简单/中等/复杂"
    )
    special_requirements: List[str] = Field(
        default_factory=list,
        description="特殊要求，如单人可完成组装、无需专业工具"
    )


class ExtendedParams(BaseModel):
    """选填扩展参数"""
    color_requirement: Optional[str] = Field(None, description="颜色要求")
    budget_constraint: Optional[float] = Field(None, description="预算约束，单位元")
    reference_image: Optional[str] = Field(None, description="参考图片链接")
    material_breakdown: Optional[Dict[str, str]] = Field(
        None, description="分部位材质要求"
    )
    manufacturing_process: Optional[str] = Field(None, description="制造工艺要求")


class DesignIntentIR(BaseModel):
    """
    设计意图中间表示（Design Intent Intermediate Representation）
    系统全流程唯一的输入数据结构，由用户输入解析后生成
    所有下游模块必须以此结构作为输入源
    """
    ir_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="唯一标识ID"
    )
    create_time: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="生成时间"
    )
    raw_input: str = Field(default="", description="用户原始输入文本，保留供追溯")
    furniture_base_info: FurnitureBaseInfo
    functional_requirements: List[FunctionalRequirement] = Field(
        default_factory=list
    )
    structural_constraints: StructuralConstraints = Field(
        default_factory=StructuralConstraints
    )
    assembly_constraints: AssemblyConstraints = Field(
        default_factory=AssemblyConstraints
    )
    extended_params: ExtendedParams = Field(default_factory=ExtendedParams)

    def to_summary(self) -> str:
        """返回设计意图的文字摘要，用于日志与UI展示"""
        dims = self.furniture_base_info.overall_dimensions
        load = self.furniture_base_info.load_requirement
        funcs = [f.function_name for f in self.functional_requirements]
        return (
            f"[{self.furniture_base_info.category}] "
            f"{dims.length}×{dims.width}×{dims.height}cm | "
            f"材质: {self.furniture_base_info.main_material} | "
            f"承重: {load.overall_load}kg | "
            f"功能: {', '.join(funcs) if funcs else '无'}"
        )
