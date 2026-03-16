"""
错误处理工具模块
"""

import logging
import traceback
from typing import Optional

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """流水线业务异常基类"""
    def __init__(self, message: str, stage: str = "", suggestion: str = ""):
        super().__init__(message)
        self.stage = stage
        self.suggestion = suggestion


class InputError(PipelineError):
    """用户输入异常：缺失必填参数或参数不合法"""
    pass


class PartMatchError(PipelineError):
    """零件匹配异常：无匹配的宜家零件"""
    pass


class ValidationError(PipelineError):
    """工程校验异常：方案不通过校验"""
    pass


class CADGenerationError(PipelineError):
    """CAD生成异常"""
    pass


def format_error_for_user(e: Exception) -> str:
    """
    将异常转为用户友好的提示文字
    """
    if isinstance(e, InputError):
        return f"⚠️ **输入参数问题**\n\n{str(e)}\n\n请修改后重新提交。"
    elif isinstance(e, PartMatchError):
        return f"🔍 **零件匹配失败**\n\n{str(e)}"
    elif isinstance(e, ValidationError):
        return f"❌ **工程校验未通过**\n\n{str(e)}"
    elif isinstance(e, CADGenerationError):
        return f"⚙️ **CAD生成失败**\n\n{str(e)}\n\n请检查输入参数后重试。"
    elif isinstance(e, ValueError):
        return f"⚠️ **参数问题**\n\n{str(e)}"
    elif isinstance(e, RuntimeError):
        return f"⚙️ **系统错误**\n\n{str(e)}"
    else:
        logger.error(f"未预期异常: {traceback.format_exc()}")
        return f"❌ **系统出现未预期错误**\n\n{str(e)}\n\n请联系系统管理员。"
