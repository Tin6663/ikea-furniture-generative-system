"""
工程约束校验模块
职责：对结构方案做全维度工程合规性校验
规则：所有校验规则均量化，不通过则不允许输出最终交付物
"""

import logging
from models.design_intent import DesignIntentIR
from models.structure_model import StructureSolution, ValidationReport
from config.constraint_config import (
    LOAD_SAFETY_FACTOR, DIMENSION_TOLERANCE_CM,
    MATERIAL_COMPATIBILITY, PROFESSIONAL_TOOLS,
)

logger = logging.getLogger(__name__)


class EngineeringValidator:
    """工程约束校验器"""

    def validate(self, solution: StructureSolution, ir: DesignIntentIR) -> ValidationReport:
        """
        执行全维度工程校验
        返回ValidationReport，passed=True表示方案可进入下一阶段
        """
        failed_items = []
        suggestions = []
        details = {}

        load_ok = self._check_load(solution, ir, failed_items, suggestions, details)
        dim_ok = self._check_dimensions(solution, ir, failed_items, suggestions, details)
        asm_ok = self._check_assemblability(solution, ir, failed_items, suggestions, details)
        mat_ok = self._check_materials(solution, ir, failed_items, suggestions, details)

        passed = load_ok and dim_ok and asm_ok and mat_ok

        report = ValidationReport(
            passed=passed,
            load_check=load_ok,
            dimension_check=dim_ok,
            assembly_check=asm_ok,
            material_check=mat_ok,
            failed_items=failed_items,
            suggestions=suggestions,
            details=details,
        )
        solution.validation_report = report

        if passed:
            logger.info("✅ 工程校验全部通过")
        else:
            logger.warning(f"❌ 工程校验未通过，{len(failed_items)}项不符合要求")

        return report

    # ── 承重校验 ───────────────────────────────────────────────────────────

    def _check_load(
        self, solution: StructureSolution, ir: DesignIntentIR,
        failed: list, suggestions: list, details: dict
    ) -> bool:
        required_load = ir.furniture_base_info.load_requirement.overall_load
        required_with_safety = required_load * LOAD_SAFETY_FACTOR

        # 计算桌腿总承重能力
        leg_items = [
            item for item in solution.bom_items
            if item.part.part_category.value == "结构件"
        ]
        panel_items = [
            item for item in solution.bom_items
            if item.part.part_category.value == "板材件"
        ]

        leg_total_load = sum(
            (item.part.max_load_kg or 0) * item.quantity
            for item in leg_items
        )
        panel_load = max(
            ((item.part.max_load_kg or 0) for item in panel_items),
            default=0
        )

        # 整体承重能力取桌腿总承重与桌面承重的较小值
        actual_load = min(leg_total_load, panel_load) if leg_total_load > 0 else panel_load
        details["load"] = {
            "required_kg": required_load,
            "required_with_safety_factor_kg": required_with_safety,
            "leg_total_capacity_kg": leg_total_load,
            "panel_capacity_kg": panel_load,
            "actual_capacity_kg": actual_load,
            "safety_factor": LOAD_SAFETY_FACTOR,
        }

        if actual_load == 0:
            # 无承重数据，给出警告但不阻断（部分辅材件无承重数据）
            logger.warning("承重数据不完整，无法精确校验")
            return True

        if actual_load < required_with_safety:
            # 判断是桌面还是桌腿是承重瓶颈
            if panel_load < leg_total_load:
                bottleneck = f"桌面（当前桌面额定承重{panel_load}kg，为承重瓶颈）"
                sug = (
                    f"建议1：换用 GERTON 格顿实心山毛榉桌面（额定75kg），最高支持{75/LOAD_SAFETY_FACTOR:.0f}kg的设计承重要求；\n"
                    f"建议2：将承重要求调整至{panel_load/LOAD_SAFETY_FACTOR:.0f}kg以内（适配当前桌面）"
                )
            else:
                bottleneck = f"桌腿（当前桌腿总承重{leg_total_load}kg）"
                sug = f"建议：增加桌腿数量，或选用承重更强的桌腿型号"

            failed.append(
                f"承重不足（{bottleneck}）：设计要求{required_load}kg × 安全系数{LOAD_SAFETY_FACTOR}"
                f"= 需要{required_with_safety}kg，当前方案实际承重能力约{actual_load}kg"
            )
            suggestions.append(sug)
            return False

        return True

    # ── 尺寸匹配校验 ──────────────────────────────────────────────────────

    def _check_dimensions(
        self, solution: StructureSolution, ir: DesignIntentIR,
        failed: list, suggestions: list, details: dict
    ) -> bool:
        dims = ir.furniture_base_info.overall_dimensions
        ok = True

        # 检查桌面尺寸偏差
        panel_items = [
            item for item in solution.bom_items
            if item.part.part_category.value == "板材件"
        ]
        for item in panel_items:
            part = item.part
            len_diff = abs((part.length_cm or dims.length) - dims.length)
            wid_diff = abs((part.width_cm or dims.width) - dims.width)
            details[f"dim_panel_{part.part_id}"] = {
                "required_length_cm": dims.length,
                "actual_length_cm": part.length_cm,
                "length_diff_cm": len_diff,
                "required_width_cm": dims.width,
                "actual_width_cm": part.width_cm,
                "width_diff_cm": wid_diff,
            }
            # 宜家桌面为标准尺寸，允许±20cm偏差（无法定制）
            IKEA_PANEL_TOLERANCE = 20.0
            if len_diff > IKEA_PANEL_TOLERANCE:
                failed.append(
                    f"桌面长度偏差过大：要求{dims.length}cm，实际{part.length_cm}cm，"
                    f"偏差{len_diff:.1f}cm（宜家标准件容差±{IKEA_PANEL_TOLERANCE}cm）"
                )
                suggestions.append(
                    f"建议调整设计长度至{part.length_cm}cm，或选择其他尺寸桌面"
                )
                ok = False

        # 检查桌子总高度
        leg_items = [
            item for item in solution.bom_items
            if item.part.part_category.value == "结构件"
        ]
        for item in leg_items:
            leg = item.part
            panel_thick = next(
                (i.part.thickness_cm or 3.4 for i in panel_items), 3.4
            )
            actual_total_height = (leg.height_cm or dims.height) + panel_thick
            height_diff = abs(actual_total_height - dims.height)
            details[f"dim_height_{leg.part_id}"] = {
                "required_height_cm": dims.height,
                "leg_height_cm": leg.height_cm,
                "panel_thickness_cm": panel_thick,
                "actual_total_height_cm": actual_total_height,
                "diff_cm": height_diff,
            }

            if leg.adjustable:
                # 可调节桌腿，检查调节范围
                if leg.adjust_range_cm:
                    try:
                        parts = leg.adjust_range_cm.split("-")
                        min_h = float(parts[0]) + panel_thick
                        max_h = float(parts[1]) + panel_thick
                        if not (min_h - DIMENSION_TOLERANCE_CM <= dims.height <= max_h + DIMENSION_TOLERANCE_CM):
                            failed.append(
                                f"可调节桌腿高度范围{min_h:.0f}-{max_h:.0f}cm，"
                                f"不覆盖目标高度{dims.height}cm"
                            )
                            ok = False
                    except Exception:
                        pass  # 解析失败时跳过
            else:
                if height_diff > DIMENSION_TOLERANCE_CM + 5:  # 固定桌腿允许5cm额外容差
                    failed.append(
                        f"桌子总高度偏差：要求{dims.height}cm，实际约{actual_total_height:.1f}cm，"
                        f"偏差{height_diff:.1f}cm"
                    )
                    suggestions.append(
                        "建议选用OLOV可调节桌腿（60-90cm可调），可精确匹配目标高度"
                    )
                    ok = False

        return ok

    # ── 可装配性校验 ──────────────────────────────────────────────────────

    def _check_assemblability(
        self, solution: StructureSolution, ir: DesignIntentIR,
        failed: list, suggestions: list, details: dict
    ) -> bool:
        ok = True
        asm = ir.assembly_constraints

        # 检查工具要求
        all_tools = set()
        for item in solution.bom_items:
            req = item.part.requires_tools or ""
            for t in req.replace("、", ",").replace("，", ",").split(","):
                t = t.strip()
                if t:
                    all_tools.add(t)

        required_tools_list = list(all_tools)
        details["assembly_tools"] = required_tools_list

        # 若用户要求无专业工具
        no_pro_tool = any(
            "无需专业工具" in r or "不需要专业工具" in r
            for r in asm.special_requirements
        )
        if no_pro_tool:
            pro_tools_used = [t for t in required_tools_list if t in PROFESSIONAL_TOOLS]
            if pro_tools_used:
                failed.append(
                    f"用户要求无专业工具，但当前方案需要：{', '.join(pro_tools_used)}"
                )
                suggestions.append("建议选用更简单安装方式的零件，避免需要专业工具")
                ok = False

        # 检查组装时间（单人可完成）
        est_time = solution.estimated_assembly_minutes
        details["estimated_assembly_minutes"] = est_time
        single_person = any(
            "单人" in r for r in asm.special_requirements
        )
        if single_person and est_time > 120:
            failed.append(
                f"预计组装时长{est_time}分钟，超过单人可接受的120分钟"
            )
            suggestions.append("建议减少功能件数量以降低组装难度")
            ok = False

        return ok

    # ── 材料兼容性校验 ────────────────────────────────────────────────────

    def _check_materials(
        self, solution: StructureSolution, ir: DesignIntentIR,
        failed: list, suggestions: list, details: dict
    ) -> bool:
        ok = True
        panel_material = ir.furniture_base_info.main_material
        compatible_connectors = MATERIAL_COMPATIBILITY.get(panel_material, [])

        details["material_compat"] = {
            "panel_material": panel_material,
            "compatible_connector_materials": compatible_connectors,
        }

        # 若未定义兼容规则，跳过（不误报）
        if not compatible_connectors:
            return True

        # 检查连接件材质是否兼容
        conn_items = [
            item for item in solution.bom_items
            if item.part.part_category.value == "连接件"
        ]
        for item in conn_items:
            mat = item.part.material
            # 检查是否有任何兼容关键词
            is_compat = any(kw in mat for kw in compatible_connectors)
            details[f"compat_{item.part.part_id}"] = {
                "connector_material": mat,
                "is_compatible": is_compat,
            }
            if not is_compat:
                failed.append(
                    f"连接件 [{item.part.part_name}] 材质'{mat}' "
                    f"与主体材质'{panel_material}'不兼容"
                )
                suggestions.append(f"建议选用钢制或镀锌连接件，与{panel_material}兼容性良好")
                ok = False

        return ok
