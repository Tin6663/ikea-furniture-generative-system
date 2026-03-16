"""
参数化CAD生成模块
职责：基于通过校验的结构方案，用CadQuery生成STEP格式的参数化CAD文件
"""

import os
import logging
import time
from typing import Optional
from models.structure_model import StructureSolution
from models.design_intent import DesignIntentIR
from config.api_config import CAD_OUTPUT_DIR

logger = logging.getLogger(__name__)


class CADGenerator:
    """
    参数化CAD生成器（使用CadQuery）
    生成STEP格式的CAD文件，包含桌面、桌腿等主要部件的三维模型
    """

    def __init__(self):
        os.makedirs(CAD_OUTPUT_DIR, exist_ok=True)

    def generate(
        self,
        solution: StructureSolution,
        ir: DesignIntentIR,
        output_filename: Optional[str] = None,
    ) -> dict:
        """
        生成CAD文件
        返回: dict，包含 step_file_path, assembly_tree, param_table
        """
        if output_filename is None:
            dims = ir.furniture_base_info.overall_dimensions
            output_filename = (
                f"desk_{int(dims.length)}x{int(dims.width)}x{int(dims.height)}"
                f"_{int(time.time())}.step"
            )
        step_path = os.path.join(CAD_OUTPUT_DIR, output_filename)

        # 提取关键尺寸
        dims = ir.furniture_base_info.overall_dimensions

        # 从BOM中读取实际零件参数（以数据库数据为准）
        panel = next(
            (item.part for item in solution.bom_items
             if item.part.part_category.value == "板材件"), None
        )
        leg = next(
            (item.part for item in solution.bom_items
             if item.part.part_category.value == "结构件"), None
        )
        leg_item = next(
            (item for item in solution.bom_items
             if item.part.part_category.value == "结构件"), None
        )

        # 实际CAD尺寸以零件数据库参数为准
        panel_l = (panel.length_cm if panel and panel.length_cm else dims.length) * 10  # mm
        panel_w = (panel.width_cm if panel and panel.width_cm else dims.width) * 10
        panel_t = (panel.thickness_cm if panel and panel.thickness_cm else 3.4) * 10
        leg_h = (leg.height_cm if leg and leg.height_cm else (dims.height - 3.4)) * 10
        leg_d = 50.0   # ADILS桌腿直径约50mm
        leg_count = leg_item.quantity if leg_item else 4

        try:
            step_path = self._build_cad(
                step_path, panel_l, panel_w, panel_t, leg_h, leg_d, leg_count
            )
            logger.info(f"STEP文件生成成功: {step_path}")
        except Exception as e:
            logger.error(f"CadQuery生成失败: {e}")
            raise RuntimeError(f"CAD文件生成失败: {e}")

        # 装配结构树（Markdown格式）
        assembly_tree = self._generate_assembly_tree(solution)

        # 参数化配置表
        param_table = self._generate_param_table(panel_l, panel_w, panel_t, leg_h, leg_count)

        return {
            "step_file_path": step_path,
            "assembly_tree": assembly_tree,
            "param_table": param_table,
        }

    def _build_cad(
        self,
        out_path: str,
        panel_l: float, panel_w: float, panel_t: float,
        leg_h: float, leg_d: float, leg_count: int
    ) -> str:
        """使用CadQuery构建桌子三维模型并导出STEP"""
        import cadquery as cq

        # ── 桌面 ──────────────────────────────────────────────────────────
        table_top = (
            cq.Workplane("XY")
            .box(panel_l, panel_w, panel_t)
            .edges("|Z")
            .fillet(5.0)           # 圆角处理（5mm圆角）
        )

        # ── 桌腿（圆管，4条或3条）─────────────────────────────────────────
        margin = leg_d * 1.5    # 桌腿距边缘的距离
        if leg_count == 4:
            leg_positions = [
                (-panel_l / 2 + margin, -panel_w / 2 + margin),
                ( panel_l / 2 - margin, -panel_w / 2 + margin),
                (-panel_l / 2 + margin,  panel_w / 2 - margin),
                ( panel_l / 2 - margin,  panel_w / 2 - margin),
            ]
        else:  # 3条腿（三角支撑）
            leg_positions = [
                (0, -panel_w / 2 + margin),
                (-panel_l / 3, panel_w / 2 - margin),
                ( panel_l / 3, panel_w / 2 - margin),
            ]

        legs_assembly = cq.Assembly()
        for i, (lx, ly) in enumerate(leg_positions):
            leg = (
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(lx, ly, -panel_t / 2 - leg_h / 2))
                .cylinder(leg_h, leg_d / 2)
            )
            legs_assembly.add(leg, name=f"leg_{i+1}")

        # ── 整体装配 ──────────────────────────────────────────────────────
        assembly = cq.Assembly()
        assembly.add(table_top, name="table_top", color=cq.Color("tan"))
        assembly.add(legs_assembly, name="legs", color=cq.Color("gray"))

        # 导出STEP
        assembly.save(out_path)
        return out_path

    def _generate_assembly_tree(self, solution: StructureSolution) -> str:
        """生成Markdown格式的装配结构树"""
        lines = ["## 装配结构树\n"]
        lines.append("```")
        lines.append("桌子总装配")
        for comp in solution.components:
            part = comp.matched_part.part
            qty = comp.matched_part.quantity
            lines.append(f"  ├── {comp.component_name}")
            lines.append(f"  │   ├── 零件: {part.part_name}")
            lines.append(f"  │   ├── 数量: {qty}件")
            lines.append(f"  │   └── 安装顺序: 第{comp.install_order}步")
        lines.append("```")
        return "\n".join(lines)

    def _generate_param_table(
        self,
        panel_l: float, panel_w: float, panel_t: float,
        leg_h: float, leg_count: int
    ) -> str:
        """生成参数化配置表（Markdown格式）"""
        rows = [
            ("桌面长度", f"{panel_l:.0f}mm", "由零件库桌面尺寸决定，需更换零件才能修改"),
            ("桌面宽度", f"{panel_w:.0f}mm", "由零件库桌面尺寸决定，需更换零件才能修改"),
            ("桌面厚度", f"{panel_t:.0f}mm", "由选定零件规格固定"),
            ("桌腿高度", f"{leg_h:.0f}mm", "ADILS固定高度；OLOV可调节范围600-900mm"),
            ("桌腿数量", str(leg_count), "通常为4条，可根据需求调整"),
            ("圆角半径", "5mm", "CAD模型圆角，不影响实际零件"),
        ]
        lines = [
            "## 参数化配置表\n",
            "| 参数名 | 当前值 | 修改说明 |",
            "|--------|--------|----------|",
        ]
        for name, val, desc in rows:
            lines.append(f"| {name} | {val} | {desc} |")
        return "\n".join(lines)
