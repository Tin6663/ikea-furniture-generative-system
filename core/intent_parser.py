"""
设计意图解析模块
职责：调用智谱AI GLM-4解析用户自然语言输入，生成标准化DesignIntentIR
原则：LLM仅做信息提取与结构化，不生成任何零件数据
"""

import json
import logging
import time
from typing import Optional
from zhipuai import ZhipuAI
from models.design_intent import (
    DesignIntentIR, FurnitureBaseInfo, OverallDimensions,
    LoadRequirement, FunctionalRequirement, StructuralConstraints,
    AssemblyConstraints, ExtendedParams
)
from config.api_config import ZHIPU_API_KEY, ZHIPU_MODEL, ZHIPU_MAX_TOKENS, ZHIPU_TEMPERATURE, LLM_MAX_RETRIES

logger = logging.getLogger(__name__)

# 用于意图解析的系统提示词（严格约束输出格式）
INTENT_PARSE_SYSTEM_PROMPT = """你是一个专业的家具设计意图解析器。
你的任务：从用户的自然语言输入中，精确提取家具设计参数，输出严格的JSON格式。

【严格要求】
1. 只提取用户明确说明的信息，不要猜测或补全用户没有说的内容
2. 缺失的字段使用null，不要自行填写默认值
3. 必须输出合法的JSON，不要有任何解释文字
4. 所有数值必须是数字类型，不要带单位字符串

【输出格式】
{
  "category": "家具品类（如：桌子）",
  "sub_category": "子品类（如：电脑桌、书桌、餐桌），如果用户未说明则为空字符串",
  "length_cm": 数字或null,
  "width_cm": 数字或null,
  "height_cm": 数字或null,
  "main_material": "主体材质，如：实木颗粒板、实木、钢化玻璃，如未说明则为null",
  "overall_load_kg": 数字或null（整体承重要求kg）,
  "functional_requirements": [
    {"name": "功能名称", "desc": "描述", "params": {}}
  ],
  "structure_type": "结构类型，如：4腿框架式，未说明则为空字符串",
  "component_list": ["桌面", "桌腿", ...],
  "special_constraints": ["圆角桌面", "可拆装", ...],
  "tool_requirement": "工具要求，如：无需专业工具，未说明则为空字符串",
  "assembly_difficulty": "简单/中等/复杂，根据功能复杂度判断",
  "special_assembly_requirements": ["单人可完成组装", ...],
  "color": "颜色，未说明则为null",
  "budget_cny": 数字或null（预算，元）,
  "missing_required_fields": ["缺失的必填字段列表，如length_cm、main_material等"]
}

【家具品类识别规则】
- 桌子相关：电脑桌、书桌、餐桌、办公桌、工作桌 → category统一为"桌子"
- 当前系统仅支持桌子品类"""


def parse_design_intent(user_input: str) -> DesignIntentIR:
    """
    解析用户输入，生成标准化DesignIntentIR
    
    参数:
        user_input: 用户的自然语言描述或结构化输入
    返回:
        DesignIntentIR: 标准化设计意图数据结构
    异常:
        ValueError: 用户输入缺少必填字段时抛出，msg中包含缺失字段提示
        RuntimeError: LLM API调用失败时抛出
    """
    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 带重试的LLM调用
    last_error = None
    for attempt in range(LLM_MAX_RETRIES):
        try:
            logger.info(f"调用GLM-4解析意图（第{attempt+1}次）")
            response = client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": INTENT_PARSE_SYSTEM_PROMPT},
                    {"role": "user", "content": f"请解析以下家具设计需求：\n{user_input}"}
                ],
                max_tokens=ZHIPU_MAX_TOKENS,
                temperature=ZHIPU_TEMPERATURE,
            )
            raw_content = response.choices[0].message.content.strip()
            break
        except Exception as e:
            last_error = e
            logger.warning(f"LLM调用失败（第{attempt+1}次）: {e}")
            if attempt < LLM_MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 指数退避
    else:
        raise RuntimeError(f"LLM API调用失败（已重试{LLM_MAX_RETRIES}次）: {last_error}")

    # 解析JSON输出
    parsed = _extract_json(raw_content)
    if parsed is None:
        raise RuntimeError(f"LLM返回格式不合法，无法解析JSON。原始输出: {raw_content[:300]}")

    # 检查缺失的必填字段
    missing = parsed.get("missing_required_fields", [])
    critical_missing = []
    if not parsed.get("length_cm"):
        critical_missing.append("length_cm（桌子长度，单位cm）")
    if not parsed.get("width_cm"):
        critical_missing.append("width_cm（桌子宽度，单位cm）")
    if not parsed.get("height_cm"):
        critical_missing.append("height_cm（桌子高度，单位cm）")
    if not parsed.get("main_material"):
        critical_missing.append("main_material（主体材质）")
    if not parsed.get("overall_load_kg"):
        critical_missing.append("overall_load_kg（整体承重要求，单位kg）")

    if critical_missing:
        raise ValueError(
            f"以下必填参数缺失，请补充后重新提交：\n" +
            "\n".join(f"  • {f}" for f in critical_missing)
        )

    # 构建DesignIntentIR
    return _build_ir(user_input, parsed)


def _extract_json(text: str) -> Optional[dict]:
    """从LLM输出中提取JSON，处理可能的markdown代码块"""
    # 去除markdown代码块标记
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    # 去除可能的前缀文字
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}\n原始文本: {text[:500]}")
        return None


def _build_ir(raw_input: str, parsed: dict) -> DesignIntentIR:
    """将解析后的dict构建为DesignIntentIR"""
    # 功能需求列表
    func_reqs = []
    for f in parsed.get("functional_requirements") or []:
        func_reqs.append(FunctionalRequirement(
            function_name=f.get("name") or "",
            function_desc=f.get("desc") or "",
            constraint_params=f.get("params") or {},
        ))

    # 结构约束
    struct = StructuralConstraints(
        structure_type=parsed.get("structure_type") or "框架式",
        component_list=parsed.get("component_list") or ["桌面", "桌腿", "连接件"],
        special_constraints=parsed.get("special_constraints") or [],
    )

    # 装配约束
    assembly = AssemblyConstraints(
        tool_requirement=parsed.get("tool_requirement") or "普通家用工具",
        assembly_difficulty=parsed.get("assembly_difficulty") or "简单",
        special_requirements=parsed.get("special_assembly_requirements") or [],
    )

    # 扩展参数
    extended = ExtendedParams(
        color_requirement=parsed.get("color"),
        budget_constraint=parsed.get("budget_cny"),
    )

    ir = DesignIntentIR(
        raw_input=raw_input,
        furniture_base_info=FurnitureBaseInfo(
            category=parsed.get("category") or "桌子",
            sub_category=parsed.get("sub_category") or "",
            overall_dimensions=OverallDimensions(
                length=float(parsed["length_cm"]),
                width=float(parsed["width_cm"]),
                height=float(parsed["height_cm"]),
            ),
            main_material=parsed["main_material"],
            load_requirement=LoadRequirement(
                overall_load=float(parsed.get("overall_load_kg", 50)),
            ),
        ),
        functional_requirements=func_reqs,
        structural_constraints=struct,
        assembly_constraints=assembly,
        extended_params=extended,
    )
    return ir
