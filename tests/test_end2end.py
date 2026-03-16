#!/usr/bin/env python3
"""
核心流水线集成测试（不调用LLM，直接构造IR）
"""
import sys
import os
# 将项目根目录加入 sys.path，确保可以导入 core/models/utils/config 等包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.design_intent import (
    DesignIntentIR, FurnitureBaseInfo, OverallDimensions, LoadRequirement,
    FunctionalRequirement, StructuralConstraints, AssemblyConstraints, ExtendedParams
)
from core.ikea_part_client import IKEAPartClient
from core.structure_reasoner import StructureReasoner
from core.engineering_validator import EngineeringValidator
from utils.data_utils import generate_bom
from core.manual_generator import ManualGenerator

def test_pipeline():
    print("=== 核心流水线集成测试 ===\n")

    # 构造测试用 DesignIntentIR
    ir = DesignIntentIR(
        raw_input="测试输入：120x60x75cm书桌",
        furniture_base_info=FurnitureBaseInfo(
            category="桌子",
            sub_category="书桌",
            overall_dimensions=OverallDimensions(length=120, width=60, height=75),
            main_material="实木颗粒板",
            load_requirement=LoadRequirement(overall_load=40),  # 40kg: LINNMON 50kg / 1.2安全系数 = 41.7kg，40kg可通过校验
        ),
        functional_requirements=[
            FunctionalRequirement(
                function_name="抽屉",
                function_desc="带一个抽屉用于储物",
                constraint_params={"count": 1}
            )
        ],
        structural_constraints=StructuralConstraints(
            structure_type="4腿框架式",
            component_list=["桌面", "桌腿", "连接件"],
            special_constraints=["圆角桌面"],
        ),
        assembly_constraints=AssemblyConstraints(
            tool_requirement="无需专业工具",
            assembly_difficulty="简单",
            special_requirements=["无需专业工具", "单人可完成组装"],
        ),
    )
    print(f"1. IR构建成功: {ir.to_summary()}")

    # 零件库客户端
    client = IKEAPartClient()
    print(f"2. 零件库加载: {client.get_parts_count()}种零件")

    # 结构推理
    reasoner = StructureReasoner(client)
    solution = reasoner.reason(ir)
    print(f"3. 结构推理完成: {len(solution.bom_items)}类零件")
    for item in solution.bom_items:
        print(f"   - {item.assembly_position}: {item.part.part_name} x{item.quantity}")

    # 工程校验
    validator = EngineeringValidator()
    report = validator.validate(solution, ir)
    print(f"4. 工程校验: {'通过 ✅' if report.passed else '未通过 ❌'}")
    if not report.passed:
        for f in report.failed_items:
            print(f"   FAIL: {f}")
        return False

    # BOM生成
    bom_md, bom_json, bom_path, json_path = generate_bom(solution, ir)
    print(f"5. BOM生成: {bom_path}")

    # 组装说明书生成
    manual_gen = ManualGenerator()
    content, manual_path = manual_gen.generate(solution, ir)
    print(f"6. 组装说明书: {manual_path}")

    print("\n=== 全部测试通过 ===")
    print(f"   总零件数: {solution.total_parts_count}件")
    print(f"   总参考价格: ¥{solution.total_price_cny}")
    print(f"   预计组装时长: {solution.estimated_assembly_minutes}分钟")
    return True


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
