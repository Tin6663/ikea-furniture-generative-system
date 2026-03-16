"""
宜家零件库本地数据库对接模块
职责：从SQLite数据库检索符合设计意图的零件，严禁虚构数据
所有返回的零件必须来自数据库真实记录
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from models.part_model import IKEAPart, PartCategory
from config.api_config import DB_PATH

logger = logging.getLogger(__name__)


class IKEAPartClient:
    """
    宜家零件数据库访问客户端
    所有零件数据来自本地SQLite数据库（ikea_parts.db）
    不得从任何其他来源生成或补充零件数据
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._verify_db()

    def _verify_db(self):
        """验证数据库文件存在且可访问"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM ikea_parts")
            count = cur.fetchone()[0]
            conn.close()
            logger.info(f"零件数据库加载成功，共 {count} 条记录")
        except Exception as e:
            raise RuntimeError(
                f"无法访问零件数据库 {self.db_path}，请先运行 data/init_db.py\n错误: {e}"
            )

    def _row_to_part(self, row: sqlite3.Row) -> IKEAPart:
        """将数据库行转换为IKEAPart对象"""
        d = dict(row)
        # 将 part_category 字符串映射为枚举
        category_map = {
            "板材件": PartCategory.PANEL,
            "结构件": PartCategory.STRUCTURAL,
            "连接件": PartCategory.CONNECTOR,
            "功能件": PartCategory.FUNCTIONAL,
            "辅材件": PartCategory.AUXILIARY,
        }
        cat = category_map.get(d.get("part_category", ""), PartCategory.PANEL)

        return IKEAPart(
            part_id=d["part_id"],
            ikea_article_number=d["ikea_article_number"],
            part_name=d["part_name"],
            part_name_en=d.get("part_name_en", ""),
            part_category=cat,
            description=d.get("description", ""),
            length_cm=d.get("length_cm"),
            width_cm=d.get("width_cm"),
            height_cm=d.get("height_cm"),
            thickness_cm=d.get("thickness_cm"),
            max_load_kg=d.get("max_load_kg"),
            material=d["material"],
            color=d.get("color", ""),
            surface_treatment=d.get("surface_treatment", ""),
            compatible_thickness_mm=d.get("compatible_thickness_mm"),
            install_method=d.get("install_method", ""),
            price_cny=d.get("price_cny"),
            ikea_url=d.get("ikea_url", ""),
            is_available=bool(d.get("is_available", 1)),
            adjustable=bool(d.get("adjustable", 0)),
            adjust_range_cm=d.get("adjust_range_cm") or None,
            requires_tools=d.get("requires_tools", ""),
            package_weight_kg=d.get("package_weight_kg"),
            extra_params=json.loads(d.get("extra_params", "{}")),
        )

    def _query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """执行数据库查询并返回行列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    # ── 公开检索接口 ──────────────────────────────────────────────────────

    def get_all_parts(self) -> List[IKEAPart]:
        """获取数据库中所有零件"""
        rows = self._query(
            "SELECT * FROM ikea_parts WHERE is_available = 1 ORDER BY part_category"
        )
        return [self._row_to_part(r) for r in rows]

    def get_by_category(self, category: str) -> List[IKEAPart]:
        """按零件分类检索，category为中文分类名"""
        rows = self._query(
            "SELECT * FROM ikea_parts WHERE part_category = ? AND is_available = 1",
            (category,)
        )
        return [self._row_to_part(r) for r in rows]

    def get_panels(
        self,
        min_length_cm: Optional[float] = None,
        min_width_cm: Optional[float] = None,
        max_length_cm: Optional[float] = None,
        material_keyword: Optional[str] = None,
    ) -> List[IKEAPart]:
        """
        检索桌面板材件
        参数:
            min_length_cm: 最小长度（cm），若有则要求零件长度≥此值
            min_width_cm:  最小宽度（cm）
            max_length_cm: 最大长度（cm），允许略大
            material_keyword: 材质关键词，如"实木颗粒"
        """
        conditions = ["part_category = '板材件'", "is_available = 1"]
        params: List[Any] = []

        if min_length_cm is not None:
            # 允许±15cm的匹配范围（宜家桌面尺寸固定，无法定制）
            conditions.append("length_cm >= ?")
            params.append(min_length_cm - 15)
        if max_length_cm is not None:
            conditions.append("length_cm <= ?")
            params.append(max_length_cm + 15)
        if min_width_cm is not None:
            conditions.append("width_cm >= ?")
            params.append(min_width_cm - 10)
        if material_keyword:
            conditions.append("material LIKE ?")
            params.append(f"%{material_keyword}%")

        sql = f"SELECT * FROM ikea_parts WHERE {' AND '.join(conditions)} ORDER BY ABS(length_cm - {min_length_cm or 120})"
        rows = self._query(sql, tuple(params))
        return [self._row_to_part(r) for r in rows]

    def get_legs(
        self,
        target_height_cm: Optional[float] = None,
        adjustable: Optional[bool] = None,
        material_keyword: Optional[str] = None,
    ) -> List[IKEAPart]:
        """
        检索桌腿结构件
        参数:
            target_height_cm: 目标桌腿高度（cm），若有则优先匹配
            adjustable:       是否要求可调节高度
            material_keyword: 材质关键词
        """
        conditions = ["part_category = '结构件'", "is_available = 1"]
        params: List[Any] = []

        if adjustable is True:
            conditions.append("adjustable = 1")
        elif adjustable is False:
            conditions.append("adjustable = 0")
        if material_keyword:
            conditions.append("material LIKE ?")
            params.append(f"%{material_keyword}%")

        order = f"ABS(height_cm - {target_height_cm})" if target_height_cm else "height_cm"
        sql = f"SELECT * FROM ikea_parts WHERE {' AND '.join(conditions)} ORDER BY {order}"
        rows = self._query(sql, tuple(params))
        return [self._row_to_part(r) for r in rows]

    def get_functional_parts(self, keyword: str) -> List[IKEAPart]:
        """
        检索功能件，按关键词匹配名称或描述
        keyword: 如"抽屉"、"走线"
        """
        rows = self._query(
            """SELECT * FROM ikea_parts
               WHERE part_category = '功能件' AND is_available = 1
               AND (part_name LIKE ? OR description LIKE ? OR part_name_en LIKE ?)""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        return [self._row_to_part(r) for r in rows]

    def get_connectors(self, thickness_mm: Optional[float] = None) -> List[IKEAPart]:
        """
        检索连接件
        thickness_mm: 适配板材厚度（mm），若有则优先匹配
        """
        conditions = ["part_category = '连接件'", "is_available = 1"]
        params: List[Any] = []

        if thickness_mm is not None:
            # 允许±3mm的适配范围
            conditions.append("(compatible_thickness_mm IS NULL OR ABS(compatible_thickness_mm - ?) <= 3)")
            params.append(thickness_mm)

        sql = f"SELECT * FROM ikea_parts WHERE {' AND '.join(conditions)}"
        rows = self._query(sql, tuple(params))
        return [self._row_to_part(r) for r in rows]

    def get_auxiliary_parts(self) -> List[IKEAPart]:
        """获取所有辅材件（脚垫等）"""
        rows = self._query(
            "SELECT * FROM ikea_parts WHERE part_category = '辅材件' AND is_available = 1"
        )
        return [self._row_to_part(r) for r in rows]

    def get_part_by_id(self, part_id: str) -> Optional[IKEAPart]:
        """按零件ID精确获取"""
        rows = self._query("SELECT * FROM ikea_parts WHERE part_id = ?", (part_id,))
        return self._row_to_part(rows[0]) if rows else None

    def get_parts_count(self) -> int:
        """获取数据库总零件数"""
        rows = self._query("SELECT COUNT(*) as cnt FROM ikea_parts WHERE is_available = 1")
        return rows[0]["cnt"] if rows else 0
