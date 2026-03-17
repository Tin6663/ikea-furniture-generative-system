# IKEA 家具参数化设计系统（CS10）

基于宜家官方标准零件库，从用户设计意图到可制造家具方案的**端到端工程生成系统**。

## 系统功能

1. **AI意图解析**：使用智谱GLM-4解析自然语言设计需求，生成结构化设计意图（DesignIntentIR）
2. **宜家零件匹配**：从本地SQLite零件库（基于宜家官方公开数据）检索匹配零件，**不虚构任何数据**
3. **工程合规性校验**：承重、尺寸、可装配性、材料兼容性全维度量化校验
4. **参数化CAD生成**：使用CadQuery生成STEP格式三维模型，可用AutoCAD/SolidWorks/Fusion360打开
5. **BOM物料清单**：标准化Markdown+JSON格式物料清单
6. **组装说明书**：分步骤Markdown格式组装指南

## 环境要求

- Python 3.9+（macOS/Linux/Windows）
- 约500MB磁盘空间（CadQuery依赖较大）

## 快速开始

### 1. 克隆/下载项目

```bash
cd ikea-furniture-generative-system
```

### 2. 安装依赖

```bash
pip3 install zhipuai pydantic streamlit pandas requests httpx python-dotenv Jinja2 cadquery
```

### 3. 配置 API Key

在项目根目录创建 `.env` 文件，填入您的[智谱AI](https://open.bigmodel.cn/) API Key：

```bash
echo "ZHIPU_API_KEY=your_actual_api_key" > .env
```

或者直接编辑 `config/api_config.py`，将 `your_api_key_here` 替换为您的 API Key。

### 4. 初始化零件数据库

```bash
python3 data/init_db.py
```

输出示例：
```
✅ 数据库初始化完成：.../data/ikea_parts.db
   共插入 18 条零件数据
```

### 5. 启动WebUI

```bash
cd ikea-furniture-generative-system
streamlit run app.py
```

浏览器访问：http://localhost:8501

### 6. 运行集成测试（可选）

```bash
PYTHONPATH=. python3 tests/test_end2end.py
```

## 项目结构

```
ikea-furniture-generative-system/
├── README.md
├── requirements.txt
├── app.py                       # Streamlit WebUI 主入口
├── config/
│   ├── api_config.py            # 智谱AI & 数据库配置
│   ├── constraint_config.py     # 工程校验阈值配置
│   └── part_category_config.py  # 零件分类与匹配规则
├── core/
│   ├── intent_parser.py         # 设计意图解析（GLM-4）
│   ├── ikea_part_client.py      # 宜家零件数据库访问
│   ├── structure_reasoner.py    # 结构推理与零件匹配
│   ├── engineering_validator.py # 工程合规性校验
│   ├── cad_generator.py         # STEP格式CAD生成
│   └── manual_generator.py      # 组装说明书生成
├── models/
│   ├── design_intent.py         # DesignIntentIR 数据结构
│   ├── part_model.py            # 零件数据结构
│   └── structure_model.py       # 结构方案数据结构
├── utils/
│   ├── data_utils.py            # BOM生成工具
│   └── error_utils.py           # 错误处理工具
├── data/
│   ├── init_db.py               # 数据库初始化脚本
│   └── ikea_parts.db            # 本地零件数据库（运行init_db.py生成）
├── tests/
│   └── test_end2end.py          # 集成测试
└── output/
    ├── bom/                     # BOM输出文件
    ├── cad/                     # STEP文件输出
    └── manual/                  # 组装说明书输出
```

## 支持的宜家零件

| 系列 | 产品 | 规格 |
|------|------|------|
| LINNMON 利蒙 | 桌面（白色/黑褐色） | 100×60、120×60、150×75cm，实木颗粒板 |
| GERTON 格顿 | 桌面 | 155×75cm，实心山毛榉 |
| ADILS 阿迪斯 | 桌腿 | 70cm固定高度，钢制 |
| OLOV 奥洛夫 | 可调节桌腿 | 60-90cm可调，钢制 |
| CAPITA 卡必达 | 桌腿 | 10cm，不锈钢 |
| ALEX 亚历克斯 | 抽屉单元 | 36cm宽，5抽屉 |
| SIGNUM 西格纳姆 | 电线管理 | 70cm导轨 |
| FIXA 菲克萨 | 脚垫/螺丝 | 多种 |

> ⚠️ **数据说明**：零件名称、材质、尺寸基于宜家官网公开产品信息。货号与价格以[宜家官网（ikea.cn）](https://www.ikea.cn)最新数据为准。

## 承重约束说明

系统采用1.2×安全冗余系数进行承重校验：
- LINNMON桌面额定50kg → 最高支持**41kg**设计要求
- GERTON桌面额定75kg → 最高支持**62kg**设计要求
- 如需更高承重，建议使用商用级定制桌面

## 配置说明

所有配置项均在 `config/` 目录下：
- `api_config.py`：智谱AI API Key（需设置 `ZHIPU_API_KEY` 环境变量）、数据库路径、输出目录
- `api_config_template.py`：配置文件模板，供参考
- `constraint_config.py`：安全系数、尺寸公差等工程校验阈值
- `part_category_config.py`：家具结构模板、功能件映射规则

**配置 API Key 的推荐方式**：在项目根目录创建 `.env` 文件：
```
ZHIPU_API_KEY=your_actual_api_key
```

## 零件库数据来源

本项目零件数据库（`data/ikea_parts.db`）的数据来源与更新方法如下：

### 一、宜家（IKEA）官方渠道

| 渠道 | 地址 | 说明 |
|------|------|------|
| 宜家中国官网 | https://www.ikea.cn | 产品名称、尺寸、材质、价格、货号的权威来源 |
| 桌面分类页 | https://www.ikea.cn/cn/zh/cat/zhuo-mian-10785/ | 所有在售桌面型号 |
| 桌腿分类页 | https://www.ikea.cn/cn/zh/cat/zhuo-tui-10786/ | 所有在售桌腿型号 |
| IKEA 国际站 | https://www.ikea.com | 部分产品国际参考（货号格式相同） |

> ⚠️ 宜家**没有公开的官方API**，产品数据只能通过浏览官网或使用非官方手段获取。

**自动更新方式（推荐）**：使用项目内置抓取脚本，从宜家非官方API拉取最新数据：

```bash
# 安装依赖（首次）
pip install requests

# 抓取并写入数据库（需要能访问 ikea.cn 的网络环境）
python3 data/fetch_ikea_data.py

# 仅预览抓取结果，不写入数据库
python3 data/fetch_ikea_data.py --dry-run

# 自定义关键词
python3 data/fetch_ikea_data.py --keywords LAGKAPTEN LINNMON ADILS
```

脚本使用的API端点（宜家内部接口，非官方）：
- 搜索接口：`https://sik.search.blue.cdtapps.com/cn/zh/search-result-page?q={关键词}`
- 参考第三方库（已归档）：https://github.com/vrslev/ikea-api-client

### 二、Bunnings（澳大利亚五金连锁）

> 适用于需要通用五金件（螺丝、支架、合页等）替代宜家FIXA系列的场景。

| 渠道 | 地址 | 说明 |
|------|------|------|
| Bunnings官网 | https://www.bunnings.com.au | 澳洲市场，通用五金/板材 |
| 家具五金分类 | https://www.bunnings.com.au/our-range/building-hardware/furniture-fittings | 铰链、连接件、滑轨等 |

Bunnings **没有公开API**，数据需通过网页抓取获得。推荐品类：
- **通用螺丝/螺栓**：Zenith / Hillman 品牌，可替代 FIXA 螺丝套装
- **板材**：F4星级松木板，可替代 LINNMON 桌面自定义尺寸
- **合页/铰链**：Hafele/Sugatsune 品牌高质量铰链

### 三、零件数据手动维护

如需手动添加/修正零件，直接编辑 `data/init_db.py` 中的 `parts_data` 列表，然后重新运行：

```bash
python3 data/init_db.py
```

## 技术栈

| 模块 | 技术 |
|------|------|
| AI意图解析 | 智谱AI GLM-4-Flash |
| 数据存储 | SQLite |
| 数据校验 | Pydantic v2 |
| CAD生成 | CadQuery 2.x（STEP格式） |
| WebUI | Streamlit |
| 数据处理 | Pandas |

## 许可

本项目为 COMP5703 CS10 课程项目，仅用于学术研究。零件数据引用自宜家官方公开信息，版权归宜家所有。
