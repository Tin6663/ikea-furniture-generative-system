"""
结构推理与零件匹配模块
职责：基于DesignIntentIR和宜家零件库，完成家具结构拆解与零件匹配
原则：只从数据库返回的真实零件中选择，不补充任何虚构数据
"""

import uuid
import logging
from typing import List, Optional, Tuple
from models.design_intent import DesignIntentIR
from models.part_model import IKEAPart, PartMatchResult, PartCategory
from models.structure_model import StructureSolution, StructureComponent, AssemblyRelation
from core.ikea_part_client import IKEAPartClient
from config.part_category_config import FURNITURE_STRUCTURE_TEMPLATES, FUNCTION_PART_MAPPING

logger = logging.getLogger(__name__)


class StructureReasoner:
    """
    家具结构推理器
    基于设计意图，从宜家零件数据库中匹配合适零件，生成结构方案
    若无匹配零件，返回明确的失败信息，不虚构数据
    """

    def __init__(self, part_client: IKEAPartClient):
        self.client = part_client

    def reason(self, ir: DesignIntentIR) -> StructureSolution:
        """
        主入口：生成完整的结构方案
        返回StructureSolution，其中bom_items包含所有匹配零件
        若有结构单元无法匹配，抛出ValueError
        """
        logger.info(f"开始结构推理: {ir.to_summary()}")
        dims = ir.furniture_base_info.overall_dimensions
        load = ir.furniture_base_info.load_requirement
        material = ir.furniture_base_info.main_material
        func_names = [f.function_name for f in ir.functional_requirements]
        special = ir.structural_constraints.special_constraints
        assembly_reqs = ir.assembly_constraints.special_requirements

        bom_items: List[PartMatchResult] = []
        components: List[StructureComponent] = []
        assembly_relations: List[AssemblyRelation] = []
        unmatched: List[str] = []

        # ── 步骤1: 匹配桌面 ─────────────────────────────────────────────
        panel, panel_note = self._match_panel(
            dims.length, dims.width, material
        )
        if panel is None:
            unmatched.append(f"桌面板材（{dims.length}×{dims.width}cm，{material}）")
        else:
            pmr = PartMatchResult(
                part=panel,
                assembly_position="桌面主体",
                quantity=1,
                matching_basis=panel_note,
                match_score=self._panel_score(panel, dims.length, dims.width),
            )
            bom_items.append(pmr)
            components.append(StructureComponent(
                component_name="桌面组件",
                component_role="主体承载面",
                matched_part=pmr,
                install_order=3,
                notes=panel_note,
            ))

        # ── 步骤2: 匹配桌腿 ─────────────────────────────────────────────
        # 计算桌腿目标高度（桌子总高 - 桌面厚度）
        panel_thickness = panel.thickness_cm if panel else 3.4
        leg_target_h = dims.height - panel_thickness
        need_adjustable = any(
            "可调节" in s or "升降" in s for s in special + func_names
        )
        leg_count = self._determine_leg_count(special)

        leg, leg_note = self._match_leg(leg_target_h, need_adjustable)
        if leg is None:
            unmatched.append(f"桌腿（目标高{leg_target_h:.1f}cm，{'可调节' if need_adjustable else '固定'}）")
        else:
            leg_pmr = PartMatchResult(
                part=leg,
                assembly_position="桌角支撑",
                quantity=leg_count,
                matching_basis=leg_note,
                match_score=self._leg_score(leg, leg_target_h),
            )
            bom_items.append(leg_pmr)
            components.append(StructureComponent(
                component_name="桌腿支撑组件",
                component_role="垂直承重支撑",
                matched_part=leg_pmr,
                install_order=1,
                notes=leg_note,
            ))

        # ── 步骤3: 匹配连接件 ────────────────────────────────────────────
        panel_thick_mm = (panel.thickness_cm * 10) if panel else 34.0
        connectors = self.client.get_connectors(thickness_mm=panel_thick_mm)
        if connectors:
            # 优先选择专用桌腿固定螺栓
            bolt = next((c for c in connectors if "ADILS" in c.part_id or "桌腿固定" in c.part_name), connectors[0])
            conn_pmr = PartMatchResult(
                part=bolt,
                assembly_position="桌腿与桌面连接处",
                quantity=leg_count,
                matching_basis=f"适配{panel_thick_mm:.0f}mm厚板材，用于固定{leg_count}条桌腿",
                match_score=1.0,
            )
            bom_items.append(conn_pmr)
            components.append(StructureComponent(
                component_name="连接件组件",
                component_role="零件连接固定",
                matched_part=conn_pmr,
                install_order=2,
                notes="桌腿安装时使用",
            ))
            # 装配关系
            if len(components) >= 2:
                assembly_relations.append(AssemblyRelation(
                    parent_position="桌面主体",
                    child_position="桌角支撑",
                    connection_type="螺栓连接",
                    connector_part_id=bolt.part_id,
                    spatial_description="桌腿垂直固定于桌面四角",
                ))

        # ── 步骤4: 匹配功能件（抽屉、走线等）──────────────────────────────
        for func_req in ir.functional_requirements:
            fname = func_req.function_name
            matched_func, func_note = self._match_functional(fname, dims)
            if matched_func:
                qty = func_req.constraint_params.get("count", 1)
                if isinstance(qty, str):
                    try:
                        qty = int(qty)
                    except Exception:
                        qty = 1
                func_pmr = PartMatchResult(
                    part=matched_func,
                    assembly_position=f"{fname}安装位置",
                    quantity=qty,
                    matching_basis=func_note,
                    match_score=0.9,
                )
                bom_items.append(func_pmr)
                components.append(StructureComponent(
                    component_name=f"{fname}组件",
                    component_role="功能扩展",
                    matched_part=func_pmr,
                    install_order=5,
                    notes=func_note,
                ))
            else:
                logger.warning(f"功能件 [{fname}] 在数据库中无匹配零件，跳过")

        # ── 步骤5: 匹配辅材件（脚垫）────────────────────────────────────
        aux_parts = self.client.get_auxiliary_parts()
        if aux_parts:
            # 优先选毡制脚垫
            pad = next((a for a in aux_parts if "毡" in a.part_name), aux_parts[0])
            pad_pmr = PartMatchResult(
                part=pad,
                assembly_position="桌腿底部",
                quantity=1,
                matching_basis="防止桌腿刮伤地板，通用辅材",
                match_score=1.0,
            )
            bom_items.append(pad_pmr)
            components.append(StructureComponent(
                component_name="辅材件组件",
                component_role="地板保护",
                matched_part=pad_pmr,
                install_order=6,
                notes="安装在桌腿底部",
            ))

        # ── 步骤6: 若有关键零件未匹配，报错 ─────────────────────────────
        if unmatched:
            raise ValueError(
                "以下结构单元在宜家零件库中未找到匹配零件：\n" +
                "\n".join(f"  • {u}" for u in unmatched) +
                "\n\n建议调整：\n"
                "  • 尺寸：宜家桌面标准尺寸为100×60cm、120×60cm、150×75cm、155×75cm\n"
                "  • 材质：可选实木颗粒板或实木（山毛榉）\n"
                "  • 高度：ADILS桌腿为固定70cm，OLOV可调60-90cm"
            )

        # ── 汇总 ─────────────────────────────────────────────────────────
        total_count = sum(item.quantity for item in bom_items)
        total_price = sum(
            (item.part.price_cny or 0) * item.quantity
            for item in bom_items
        )
        tools = self._infer_tools(bom_items)
        est_minutes = self._estimate_assembly_time(bom_items, func_names)

        solution = StructureSolution(
            solution_id=str(uuid.uuid4()),
            ir_id=ir.ir_id,
            components=components,
            assembly_relations=assembly_relations,
            bom_items=bom_items,
            total_parts_count=total_count,
            total_price_cny=round(total_price, 2),
            estimated_assembly_minutes=est_minutes,
            required_tools=tools,
        )
        logger.info(f"结构推理完成：{len(bom_items)}类零件，共{total_count}件，预计{est_minutes}分钟组装")
        return solution

    # ── 私有匹配方法 ──────────────────────────────────────────────────────

    def _match_panel(
        self, length_cm: float, width_cm: float, material: str
    ) -> Tuple[Optional[IKEAPart], str]:
        """匹配最合适的桌面板材"""
        # 提取材质关键词
        mat_kw = None
        if "实木颗粒" in material or "颗粒板" in material or "刨花" in material:
            mat_kw = "实木颗粒板"
        elif "实木" in material:
            mat_kw = "实木"

        panels = self.client.get_panels(
            min_length_cm=length_cm,
            min_width_cm=width_cm,
            max_length_cm=length_cm + 40,
            material_keyword=mat_kw,
        )
        if not panels:
            # 放宽条件重试
            panels = self.client.get_panels(
                min_length_cm=length_cm - 20,
                min_width_cm=width_cm - 10,
                max_length_cm=length_cm + 40,
            )

        if not panels:
            return None, ""

        # 选最接近目标尺寸的
        best = min(panels, key=lambda p: abs((p.length_cm or 0) - length_cm) + abs((p.width_cm or 0) - width_cm))
        note = (
            f"目标尺寸{length_cm}×{width_cm}cm，"
            f"匹配到{best.length_cm}×{best.width_cm}cm桌面"
        )
        if best.length_cm != length_cm or best.width_cm != width_cm:
            note += f"（尺寸差±{abs((best.length_cm or 0)-length_cm):.0f}cm，宜家桌面为标准尺寸，无法定制）"
        return best, note

    def _match_leg(
        self, target_height_cm: float, need_adjustable: bool
    ) -> Tuple[Optional[IKEAPart], str]:
        """匹配桌腿"""
        legs = self.client.get_legs(
            target_height_cm=target_height_cm,
            adjustable=True if need_adjustable else None,
        )
        if not legs:
            legs = self.client.get_legs()
        if not legs:
            return None, ""

        best = min(legs, key=lambda l: abs((l.height_cm or 0) - target_height_cm))
        note = (
            f"目标桌腿高{target_height_cm:.1f}cm，"
            f"匹配到{best.part_name}（高{best.height_cm}cm"
            + ("，可调节范围" + best.adjust_range_cm + "cm" if best.adjustable and best.adjust_range_cm else "")
            + "）"
        )
        return best, note

    def _match_functional(
        self, func_name: str, dims
    ) -> Tuple[Optional[IKEAPart], str]:
        """匹配功能件"""
        keyword_map = {
            "抽屉": "抽屉",
            "走线孔": "走线",
            "走线": "走线",
            "电线管理": "走线",
        }
        kw = keyword_map.get(func_name)
        if not kw:
            # 用功能名直接搜索
            kw = func_name

        results = self.client.get_functional_parts(kw)
        if not results:
            return None, f"数据库中未找到与'{func_name}'匹配的功能件"

        best = results[0]
        note = f"匹配'{func_name}'功能需求，选用{best.part_name}"
        return best, note

    def _determine_leg_count(self, special_constraints: List[str]) -> int:
        """从特殊约束中解析桌腿数量"""
        for c in special_constraints:
            if "4条" in c or "四条" in c or "4腿" in c:
                return 4
            if "3条" in c or "三条" in c:
                return 3
        return 4  # 默认4条

    def _panel_score(self, panel: IKEAPart, target_l: float, target_w: float) -> float:
        """计算桌面匹配评分"""
        if panel.length_cm is None or panel.width_cm is None:
            return 0.5
        diff = abs(panel.length_cm - target_l) + abs(panel.width_cm - target_w)
        return max(0.3, 1.0 - diff / 50)

    def _leg_score(self, leg: IKEAPart, target_h: float) -> float:
        """计算桌腿匹配评分"""
        if leg.height_cm is None:
            return 0.5
        diff = abs(leg.height_cm - target_h)
        return max(0.3, 1.0 - diff / 30)

    def _infer_tools(self, bom_items: List[PartMatchResult]) -> List[str]:
        """推断所需工具列表"""
        tools = set()
        for item in bom_items:
            req = item.part.requires_tools or ""
            if "内六角" in req:
                tools.add("内六角扳手")
            if "十字螺丝刀" in req or "螺丝刀" in req:
                tools.add("十字螺丝刀")
        if not tools:
            tools.add("内六角扳手")
        return sorted(tools)

    def _estimate_assembly_time(
        self, bom_items: List[PartMatchResult], func_names: List[str]
    ) -> int:
        """估算组装时长（分钟）"""
        base = 30  # 基础时间
        base += sum(item.quantity * 3 for item in bom_items)
        base += len(func_names) * 10
        return min(base, 120)
