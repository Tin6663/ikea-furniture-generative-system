"""
组装说明书生成模块
职责：基于最终结构方案和BOM，生成Markdown格式的标准化家具组装说明书
"""

import os
import time
import logging
from typing import List
from models.structure_model import StructureSolution
from models.design_intent import DesignIntentIR
from models.part_model import PartMatchResult
from config.api_config import MANUAL_OUTPUT_DIR

logger = logging.getLogger(__name__)


class ManualGenerator:
    """家具组装说明书生成器"""

    def __init__(self):
        os.makedirs(MANUAL_OUTPUT_DIR, exist_ok=True)

    def generate(
        self,
        solution: StructureSolution,
        ir: DesignIntentIR,
        output_filename: str = None,
    ) -> str:
        """
        生成组装说明书Markdown文件
        返回: (markdown文本内容, 输出文件路径)
        """
        dims = ir.furniture_base_info.overall_dimensions
        if output_filename is None:
            output_filename = (
                f"assembly_manual_{int(dims.length)}x{int(dims.width)}x{int(dims.height)}"
                f"_{int(time.time())}.md"
            )
        out_path = os.path.join(MANUAL_OUTPUT_DIR, output_filename)

        content = self._build_manual(solution, ir)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"组装说明书生成成功: {out_path}")
        return content, out_path

    def _build_manual(self, solution: StructureSolution, ir: DesignIntentIR) -> str:
        dims = ir.furniture_base_info.overall_dimensions
        load = ir.furniture_base_info.load_requirement
        category = ir.furniture_base_info.sub_category or ir.furniture_base_info.category
        total_items = solution.total_parts_count
        tools = solution.required_tools or ["内六角扳手"]
        est_min = solution.estimated_assembly_minutes

        parts = []

        # ────────────────────────────────────────────────────────────────
        # 1. 说明书概览
        # ────────────────────────────────────────────────────────────────
        parts.append(f"""# {category}组装说明书

## 1. 说明书概览

| 项目 | 说明 |
|------|------|
| 家具名称 | {category} |
| 整体尺寸 | 长{dims.length}cm × 宽{dims.width}cm × 高{dims.height}cm |
| 整体承重 | ≥{load.overall_load}kg |
| 零件总数 | {total_items}件 |
| 预计组装时长 | 约{est_min}分钟 |
| 所需工具 | {', '.join(tools)} |

> ⚠️ 注意：所有零件均来自宜家标准产品线，请在开始前逐一核对零件清单。
""")

        # ────────────────────────────────────────────────────────────────
        # 2. 零件核对清单（对应BOM）
        # ────────────────────────────────────────────────────────────────
        parts.append("## 2. 零件核对清单\n")
        parts.append("| 序号 | 宜家货号 | 零件名称 | 分类 | 规格 | 数量 | 核对 |")
        parts.append("|------|----------|----------|------|------|------|------|")
        for i, item in enumerate(solution.bom_items, 1):
            p = item.part
            spec = p.get_dimension_str() or p.material
            parts.append(
                f"| {i} | {p.ikea_article_number} | {p.part_name} | "
                f"{p.part_category.value} | {spec} | {item.quantity}件 | ☐ |"
            )
        parts.append(
            "\n> 💡 建议：按清单逐一将零件摆放在干净平坦的地面上，确认无缺失后再开始组装。\n"
        )

        # ────────────────────────────────────────────────────────────────
        # 3. 前置准备与安全提示
        # ────────────────────────────────────────────────────────────────
        parts.append(f"""## 3. 前置准备与安全提示

### 3.1 组装环境要求
- 准备至少 {dims.length + 50:.0f}cm × {dims.width + 50:.0f}cm 的平坦操作区域
- 地面铺设软垫或纸板，防止组装过程中划伤桌面

### 3.2 所需工具
""")
        for tool in tools:
            parts.append(f"- **{tool}**")

        parts.append("""
### 3.3 安全注意事项
- ⚠️ 确保所有螺丝拧紧到位，松动的螺丝会导致结构不稳
- ⚠️ 组装完成前勿在桌面放置重物
- ⚠️ 若需要倾斜桌子操作，请确保有人协助扶稳
- ⚠️ 所有零件均来自宜家，请勿使用非原配零件替换
- ✅ 遇到问题请停止操作，查阅本说明书或联系宜家客服
""")

        # ────────────────────────────────────────────────────────────────
        # 4. 分步组装流程
        # ────────────────────────────────────────────────────────────────
        parts.append("## 4. 分步组装流程\n")

        steps = self._build_assembly_steps(solution, ir)
        for step in steps:
            parts.append(step)

        # ────────────────────────────────────────────────────────────────
        # 5. 整体结构校验
        # ────────────────────────────────────────────────────────────────
        parts.append(f"""## 5. 整体结构校验

组装完成后，请按以下清单逐项检查：

- [ ] **稳定性检查**：用手轻推桌面四角，确认无明显晃动
- [ ] **水平检查**：将水平仪放置于桌面，确认桌面水平（若倾斜请调节桌腿）
- [ ] **承重测试**：在桌面中心放置约 {min(load.overall_load * 0.5, 30):.0f}kg 重物，保持5分钟，确认结构无异常
- [ ] **螺丝复查**：用扳手再次确认所有螺丝均已拧紧
- [ ] **外观检查**：检查桌面、桌腿无明显划痕、变形
- [ ] **零件核对**：确认所有包装中的零件均已使用，无剩余结构件

### 5.1 调整方法
若桌面不水平：
1. 将桌子翻转，桌面朝下放在软垫上
2. 调节倾斜侧的桌腿（拧入方向为顺时针=缩短，逆时针=伸长）
3. 或调整OLOV可调节桌腿的高度旋钮

""")

        # ────────────────────────────────────────────────────────────────
        # 6. 拆卸与维护
        # ────────────────────────────────────────────────────────────────
        parts.append(f"""## 6. 拆卸与维护说明

### 6.1 拆卸方法
按组装步骤逆序操作：
1. 清空桌面，将桌子翻转至桌面朝下（放在软垫上保护桌面）
2. 用内六角扳手松开桌腿固定螺栓
3. 旋转桌腿逆时针方向取下
4. 分类收纳所有零件和螺丝

### 6.2 日常维护
- **桌面清洁**：用干燥或微湿的软布擦拭，禁止使用腐蚀性清洁剂
- **承重提示**：日常使用不超过{load.overall_load}kg，避免长期超载
- **松动检查**：每3-6个月检查一次螺丝是否松动，发现松动及时拧紧

### 6.3 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 桌子晃动 | 螺丝未拧紧 / 桌腿不等高 | 拧紧所有螺丝；调节桌腿高度 |
| 桌面不水平 | 桌腿高度不一致 | 调节各桌腿高度至一致 |
| 螺丝拧不紧 | 预埋螺母受损 | 联系宜家客服获取替换零件 |
| 抽屉开合不顺 | 滑轨未对齐 | 重新调整滑轨位置 |

---
*本说明书由宜家家具参数化设计系统（CS10）自动生成，零件数据来源于宜家公开产品信息。*  
*请以宜家官方提供的产品说明书为准，如有疑问请联系宜家客服：400-800-2345（中国大陆）*
""")

        return "\n".join(parts)

    def _build_assembly_steps(self, solution: StructureSolution, ir: DesignIntentIR) -> List[str]:
        """生成具体的分步组装步骤"""
        # 按install_order排序组件
        sorted_comps = sorted(solution.components, key=lambda c: c.install_order)

        steps = []
        step_no = 1

        # 基础步骤（固定顺序）
        # 步骤1: 安装桌腿
        leg_comp = next((c for c in sorted_comps if "桌腿" in c.component_name), None)
        if leg_comp:
            leg = leg_comp.matched_part.part
            qty = leg_comp.matched_part.quantity
            steps.append(f"""### 步骤{step_no}：安装桌腿

**所需零件：** {leg.part_name} × {qty}条  
**所需工具：** 无需工具（手拧）  

**操作步骤：**
1. 将桌面翻转，桌面朝下放置在软垫上（防止划伤）
2. 找到桌面底部的{qty}个预埋螺母孔位（位于四角，距边缘约8cm）
3. 将桌腿上端螺杆对准孔位，顺时针旋转手拧至拧紧

**校验节点：** 手推每条桌腿，确认无松动，桌腿垂直于桌面

> 💡 易错点：确保螺杆完全旋入螺母（听到"咔哒"声为止），避免桌腿松动
""")
            step_no += 1

        # 步骤2: 安装连接件/固定螺栓（若有）
        conn_comp = next((c for c in sorted_comps if "连接件" in c.component_name), None)
        if conn_comp:
            conn = conn_comp.matched_part.part
            qty = conn_comp.matched_part.quantity
            steps.append(f"""### 步骤{step_no}：安装固定连接件

**所需零件：** {conn.part_name} × {qty}套  
**所需工具：** 内六角扳手  

**操作步骤：**
1. 检查桌腿与桌面的连接处，确认螺栓已到位
2. 用内六角扳手进一步拧紧每个连接螺栓
3. 确认桌腿与桌面紧密贴合，无缝隙

**校验节点：** 用手摇晃桌腿，确认无松动

""")
            step_no += 1

        # 步骤3: 竖起桌子
        steps.append(f"""### 步骤{step_no}：竖起桌子

**操作步骤：**
1. 确认所有桌腿安装牢固后，由1-2人协助将桌子翻正
2. 将桌子放置于目标位置
3. 检查桌子是否平稳（四条桌腿均着地）

**校验节点：** 用手轻压桌面四角，确认无翘动

""")
        step_no += 1

        # 步骤4: 安装功能件（抽屉、走线等）
        func_comps = [c for c in sorted_comps
                      if "功能" in c.component_role or "功能" in c.component_name]
        for fc in func_comps:
            part = fc.matched_part.part
            qty = fc.matched_part.quantity
            if "抽屉" in part.part_name or "抽屉" in fc.component_name:
                steps.append(f"""### 步骤{step_no}：摆放抽屉单元

**所需零件：** {part.part_name} × {qty}件  
**所需工具：** 内六角扳手（组装抽屉单元本身）  

**操作步骤：**
1. 按{part.part_name}随附的说明书先独立组装抽屉单元
2. 将组装好的抽屉单元推入桌面下方指定位置
3. 根据需要，用安全绳或L形角码将抽屉单元与桌面固定（防倾倒）

**校验节点：** 逐一拉开每个抽屉，确认开合顺畅，承重测试：每个抽屉放入约5kg重物，确认正常

""")
            elif "走线" in part.part_name or "线" in fc.component_name:
                steps.append(f"""### 步骤{step_no}：安装电线管理导轨

**所需零件：** {part.part_name} × {qty}件  
**所需工具：** 十字螺丝刀  

**操作步骤：**
1. 将导轨定位于桌面下方中部，距后沿约10cm
2. 用提供的螺丝将导轨固定在桌面底部（先轻拧定位，确认位置后再拧紧）
3. 将电线整理后穿入导轨

**校验节点：** 拉扯导轨，确认固定牢固，导轨不晃动

""")
            step_no += 1

        # 步骤5: 安装脚垫
        aux_comps = [c for c in sorted_comps if "辅材" in c.component_name]
        if aux_comps:
            pad = aux_comps[0].matched_part.part
            steps.append(f"""### 步骤{step_no}：安装地板保护脚垫

**所需零件：** {pad.part_name} × 4片  
**所需工具：** 无需工具  

**操作步骤：**
1. 将桌子轻轻倾斜，露出每条桌腿底部
2. 撕去脚垫背面的保护纸
3. 将脚垫粘贴于桌腿底部中心位置，用力按压5秒

**校验节点：** 确认4个脚垫均粘贴牢固，放回桌子时桌腿平稳落地

""")
            step_no += 1

        # 最终步骤
        steps.append(f"""### 步骤{step_no}：最终检查

**操作步骤：**
1. 将桌子放置于最终位置
2. 在桌面放置水平仪，确认桌面水平
3. 用手推桌子各个方向，确认结构稳固无晃动
4. 清理组装区域，收纳多余的小零件和包装

**✅ 组装完成！**

""")

        return steps
