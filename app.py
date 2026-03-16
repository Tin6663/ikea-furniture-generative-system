"""
宜家家具参数化设计系统 - Streamlit WebUI
入口文件：app.py
运行方式: streamlit run app.py
"""

import sys
import os
import logging

# 确保项目根目录在Python路径中
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# ── 自动初始化数据库（若不存在）─────────────────────────────────────────────
def _auto_init_db():
    """在WebUI启动时自动检测并初始化数据库，无需手动运行 init_db.py"""
    db_path = os.path.join(PROJECT_ROOT, "data", "ikea_parts.db")
    if not os.path.exists(db_path):
        try:
            sys.path.insert(0, PROJECT_ROOT)
            from data.init_db import init_database
            init_database()
        except Exception as e:
            pass  # 若失败，后续 get_part_client() 会给出明确报错

_auto_init_db()

import streamlit as st

# ── 页面基础配置 ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IKEA 家具参数化设计系统 | CS10",
    page_icon="🪑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 延迟加载重量级模块（加速首页渲染）────────────────────────────────────────
@st.cache_resource(show_spinner="正在初始化零件数据库...")
def get_part_client():
    from core.ikea_part_client import IKEAPartClient
    return IKEAPartClient()

@st.cache_resource
def get_structure_reasoner():
    from core.structure_reasoner import StructureReasoner
    client = get_part_client()
    return StructureReasoner(client)

@st.cache_resource
def get_validator():
    from core.engineering_validator import EngineeringValidator
    return EngineeringValidator()

# CAD生成器不缓存，每次新建（包含输出路径逻辑）
def get_cad_generator():
    from core.cad_generator import CADGenerator
    return CADGenerator()

def get_manual_generator():
    from core.manual_generator import ManualGenerator
    return ManualGenerator()

logging.basicConfig(level=logging.INFO)

# ── 侧边栏：系统信息 ──────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ikea_logo.svg/200px-Ikea_logo.svg.png", width=100)
    st.title("CS10 · 家具设计系统")
    st.markdown("""
**核心功能**
- 🧠 AI意图解析（智谱GLM-4）
- 🔍 宜家零件库匹配
- ✅ 工程合规性校验
- 📐 参数化CAD生成
- 📋 组装说明书生成

---
**数据源**：宜家官方公开产品数据（本地库）  
**注意**：零件价格以官网为准
""")

    st.markdown("---")
    try:
        client = get_part_client()
        count = client.get_parts_count()
        st.success(f"✅ 零件库已就绪（{count}种零件）")
    except Exception as e:
        st.error(f"❌ 零件库初始化失败: {e}\n请先运行 `python3 data/init_db.py`")
        st.stop()

# ── 主页面标题 ────────────────────────────────────────────────────────────────
st.title("🪑 宜家家具参数化设计系统")
st.markdown(
    "基于宜家官方标准零件库，从设计意图到可制造方案的**端到端工程生成系统**"
)
st.markdown("---")

# ── 输入区 ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📝 设计需求输入")

    input_mode = st.radio(
        "输入方式",
        ["自然语言描述", "结构化参数填写"],
        horizontal=True,
    )

    user_input_text = ""

    if input_mode == "自然语言描述":
        user_input_text = st.text_area(
            "请用自然语言描述您的家具设计需求",
            placeholder=(
                "例如：我要一个长120cm宽60cm高75cm的家用书桌，"
                "主体用实木颗粒板，整体承重不低于80kg，带1个抽屉，"
                "可拆装，圆角桌面，用宜家标准零件，单人可完成组装"
            ),
            height=150,
        )
    else:
        # 结构化参数表单
        with st.form("structured_input"):
            c1, c2, c3 = st.columns(3)
            with c1:
                length = st.number_input("桌子长度 (cm)", min_value=60.0, max_value=300.0, value=120.0, step=5.0)
            with c2:
                width = st.number_input("桌子宽度 (cm)", min_value=40.0, max_value=150.0, value=60.0, step=5.0)
            with c3:
                height = st.number_input("桌子高度 (cm)", min_value=50.0, max_value=120.0, value=75.0, step=1.0)

            c4, c5 = st.columns(2)
            with c4:
                material = st.selectbox(
                    "主体材质",
                    ["实木颗粒板", "实木（山毛榉）", "钢化玻璃"],
                )
            with c5:
                load = st.number_input("整体承重要求 (kg)", min_value=20.0, max_value=300.0, value=80.0, step=10.0)

            sub_cat = st.selectbox(
                "桌子类型",
                ["书桌", "电脑桌", "餐桌", "办公桌", "工作桌"],
            )

            funcs = st.multiselect(
                "功能需求（可多选）",
                ["带抽屉", "走线孔/电线管理", "可调节高度", "可拆装"],
            )
            constraints = st.multiselect(
                "结构约束（可多选）",
                ["4条桌腿", "圆角桌面", "白色", "黑色"],
            )
            asm_reqs = st.multiselect(
                "装配约束（可多选）",
                ["无需专业工具", "单人可完成组装"],
            )

            submitted = st.form_submit_button("生成设计方案", type="primary")

        if submitted:
            func_parts = [f"带{f}" if not f.startswith("带") else f for f in funcs]
            user_input_text = (
                f"我要一个长{length}cm宽{width}cm高{height}cm的{sub_cat}，"
                f"主体用{material}，整体承重不低于{load}kg，"
                + ("，".join(func_parts) + "，" if func_parts else "")
                + ("，".join(constraints) + "，" if constraints else "")
                + ("，".join(asm_reqs) + "，" if asm_reqs else "")
                + "用宜家标准零件"
            )

with col2:
    st.subheader("ℹ️ 宜家零件库覆盖范围")
    st.markdown("""
**桌面系列**
- LINNMON 利蒙：100×60、120×60、150×75cm，实木颗粒板
- GERTON 格顿：155×75cm，实心山毛榉

**桌腿系列**
- ADILS 阿迪斯：70cm固定高度，钢制
- OLOV 奥洛夫：60-90cm可调节，钢制
- CAPITA 卡必达：10cm，不锈钢

**功能件**
- ALEX 亚历克斯：抽屉单元（36cm宽）
- SIGNUM 西格纳姆：电线管理导轨

**连接件 & 辅材**
- FIXA 菲克萨：螺丝套装、脚垫
""")
    st.info("💡 零件数据基于宜家官网公开信息。如有变动请以官网（ikea.cn）为准。")

# ── 生成按钮（仅自然语言模式下显示）────────────────────────────────────────────
if input_mode == "自然语言描述":
    run_btn = st.button("🚀 生成设计方案", type="primary", disabled=not user_input_text.strip())
else:
    run_btn = submitted and bool(user_input_text.strip())

st.markdown("---")

# ── 主流程 ────────────────────────────────────────────────────────────────────
if run_btn and user_input_text.strip():
    from utils.error_utils import format_error_for_user

    # 状态跟踪
    progress = st.progress(0, text="准备中...")
    status_area = st.empty()

    # Session state存储结果
    if "result" not in st.session_state:
        st.session_state.result = {}

    try:
        # ── Step 1: 解析设计意图 ─────────────────────────────────────────
        progress.progress(10, text="🧠 正在解析设计意图（智谱GLM-4）...")
        status_area.info("正在调用AI解析您的设计需求，请稍候（约10-20秒）...")

        from core.intent_parser import parse_design_intent
        ir = parse_design_intent(user_input_text)

        progress.progress(30, text="✅ 设计意图解析完成")
        st.session_state.result["ir"] = ir

        # 展示解析结果
        with st.expander("📋 设计意图解析结果（可折叠）", expanded=True):
            st.success(f"✅ 解析完成：{ir.to_summary()}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.json({
                    "家具类型": ir.furniture_base_info.category,
                    "子类型": ir.furniture_base_info.sub_category,
                    "尺寸": {
                        "长": f"{ir.furniture_base_info.overall_dimensions.length}cm",
                        "宽": f"{ir.furniture_base_info.overall_dimensions.width}cm",
                        "高": f"{ir.furniture_base_info.overall_dimensions.height}cm",
                    },
                    "主体材质": ir.furniture_base_info.main_material,
                    "承重要求": f"{ir.furniture_base_info.load_requirement.overall_load}kg",
                })
            with col_b:
                st.json({
                    "功能需求": [f.function_name for f in ir.functional_requirements],
                    "结构约束": ir.structural_constraints.special_constraints,
                    "装配约束": ir.assembly_constraints.special_requirements,
                    "颜色要求": ir.extended_params.color_requirement or "未指定",
                })

        # ── Step 2: 零件匹配 ─────────────────────────────────────────────
        progress.progress(45, text="🔍 正在从零件库匹配宜家零件...")
        status_area.info("正在从宜家零件数据库检索匹配零件...")

        reasoner = get_structure_reasoner()
        solution = reasoner.reason(ir)
        st.session_state.result["solution"] = solution

        progress.progress(60, text="✅ 零件匹配完成")

        # ── Step 3: 工程校验 ─────────────────────────────────────────────
        progress.progress(65, text="✅ 正在执行工程合规性校验...")
        status_area.info("正在执行承重、尺寸、装配、材料兼容性全维度校验...")

        validator = get_validator()
        report = validator.validate(solution, ir)
        st.session_state.result["report"] = report

        if not report.passed:
            progress.progress(70, text="❌ 工程校验未通过")
            st.error("## ❌ 工程校验未通过，请调整设计参数")
            for item in report.failed_items:
                st.error(f"• {item}")
            st.warning("**修改建议：**")
            for sug in report.suggestions:
                st.info(f"💡 {sug}")
            st.stop()

        progress.progress(75, text="✅ 工程校验全部通过")
        with st.expander("🔧 工程校验报告", expanded=False):
            st.success("✅ 全部校验通过")
            col1v, col2v = st.columns(2)
            with col1v:
                st.markdown(f"- {'✅' if report.load_check else '❌'} 承重校验")
                st.markdown(f"- {'✅' if report.dimension_check else '❌'} 尺寸匹配校验")
            with col2v:
                st.markdown(f"- {'✅' if report.assembly_check else '❌'} 可装配性校验")
                st.markdown(f"- {'✅' if report.material_check else '❌'} 材料兼容性校验")

        # ── Step 4: 生成BOM ──────────────────────────────────────────────
        progress.progress(80, text="📋 正在生成BOM物料清单...")
        status_area.info("正在生成标准化物料清单...")

        from utils.data_utils import generate_bom
        bom_md, bom_json, bom_md_path, bom_json_path = generate_bom(solution, ir)
        st.session_state.result["bom_md"] = bom_md
        st.session_state.result["bom_json"] = bom_json

        # ── Step 5: 生成CAD ──────────────────────────────────────────────
        progress.progress(85, text="📐 正在生成参数化CAD文件（STEP格式）...")
        status_area.info("正在用CadQuery生成3D模型，首次运行较慢（约30-60秒）...")

        cad_gen = get_cad_generator()
        cad_result = cad_gen.generate(solution, ir)
        st.session_state.result["cad"] = cad_result

        # ── Step 6: 生成组装说明书 ───────────────────────────────────────
        progress.progress(93, text="📖 正在生成组装说明书...")
        status_area.info("正在生成标准化组装说明书...")

        manual_gen = get_manual_generator()
        manual_content, manual_path = manual_gen.generate(solution, ir)
        st.session_state.result["manual"] = manual_content
        st.session_state.result["manual_path"] = manual_path

        progress.progress(100, text="✅ 全部生成完成！")
        status_area.success("🎉 所有交付物生成完成！")

    except ValueError as e:
        progress.progress(0, text="")
        st.error(format_error_for_user(e))
        st.stop()
    except RuntimeError as e:
        progress.progress(0, text="")
        st.error(format_error_for_user(e))
        st.stop()
    except Exception as e:
        progress.progress(0, text="")
        st.error(format_error_for_user(e))
        st.stop()

# ── 展示交付物 ─────────────────────────────────────────────────────────────────
if st.session_state.get("result", {}).get("bom_md"):
    result = st.session_state.result
    solution = result.get("solution")
    ir = result.get("ir")

    st.header("📦 三大核心交付物")

    tab1, tab2, tab3 = st.tabs(["📋 BOM物料清单", "📐 CAD设计文件", "📖 组装说明书"])

    # ── Tab 1: BOM ──────────────────────────────────────────────────────
    with tab1:
        st.markdown(result["bom_md"])
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "⬇️ 下载 BOM Markdown",
                data=result["bom_md"].encode("utf-8"),
                file_name="bom.md",
                mime="text/markdown",
            )
        with col_dl2:
            st.download_button(
                "⬇️ 下载 BOM JSON",
                data=result["bom_json"].encode("utf-8"),
                file_name="bom.json",
                mime="application/json",
            )

    # ── Tab 2: CAD ──────────────────────────────────────────────────────
    with tab2:
        cad = result.get("cad", {})
        step_path = cad.get("step_file_path", "")

        if step_path and os.path.exists(step_path):
            st.success(f"✅ STEP文件生成成功")
            with open(step_path, "rb") as f:
                st.download_button(
                    "⬇️ 下载 STEP 文件（可用AutoCAD/SolidWorks/Fusion360打开）",
                    data=f.read(),
                    file_name=os.path.basename(step_path),
                    mime="application/octet-stream",
                )

        st.markdown(cad.get("assembly_tree", ""))
        st.markdown("---")
        st.markdown(cad.get("param_table", ""))

    # ── Tab 3: 组装说明书 ────────────────────────────────────────────────
    with tab3:
        st.markdown(result.get("manual", ""))
        st.download_button(
            "⬇️ 下载组装说明书 Markdown",
            data=result["manual"].encode("utf-8"),
            file_name="assembly_manual.md",
            mime="text/markdown",
        )
