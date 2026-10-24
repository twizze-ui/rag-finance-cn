# 中文财报知识库 RAG 问答系统

> 基于开源项目 [IlyaRice/RAG-Challenge-2](https://github.com/IlyaRice/RAG-Challenge-2)（MIT License）做的**中文本地化改造**。
> 上游的解析、切块、检索骨架保留，中文语料适配、模型替换、开放式问答与前端为本仓库新增。

面向中文年报与券商研报的知识库问答 Demo：PDF → Markdown → 切块 → 向量库 → 检索 + 重排 → 结构化答案（含分步推理与引用页码）。

## 与原项目的主要差异

| 环节 | 上游项目 | 本仓库 |
| --- | --- | --- |
| PDF 解析 | Docling | MinerU API（对中文版面与表格更友好） |
| 文档落库 | JSON pages | Markdown 按行切块，保留行号区间 |
| Embedding | OpenAI `text-embedding-3-large` | DashScope `text-embedding-v1`（1536 维） |
| 生成模型 | GPT-4o / o3-mini | 通义千问 `qwen-turbo`（DashScope SDK） |
| 问答类型 | number / boolean / names | 新增开放式 `string`（四段结构化 JSON） |
| 前端 | 无 | Streamlit 单页问答界面 |
| 语料 | 英文年报 | 中文年报 + 券商研报 |

## 快速开始

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -e . -r requirements.txt

# 环境变量（见 .env.example）
set MINERU_API_KEY=...
set MINERU_PDF_BASE_URL=https://your-oss-bucket/pdf
set DASHSCOPE_API_KEY=...
```

按顺序跑：

```bash
python -m src.pipeline          # 切块 → 建向量库 → 生成答案
streamlit run app_streamlit.py  # 前端问答
```

数据目录结构（需自备，见下文）：

```
data/stock_data/
├── pdf_reports/                 # 你的 PDF
├── subset.csv                   # sha1,file_name,company_name
├── questions.json               # [{"text": "...", "kind": "string"}]
├── debug_data/03_reports_markdown/   # MinerU 输出的 full.md
└── databases/
    ├── chunked_reports/         # 切块结果
    └── vector_dbs/              # 每份文档一个 faiss
```

## 实测数据

对 1 份年报（6419 行）实测（`measure_rag.py stats`，未随仓库提供）：

| 指标 | 数值 |
| --- | --- |
| chunk 数 | 257 |
| 字符数 | 均值 1503、P95 3643、max 16221 |
| 超 embedding 上限（2048 字符） | 44 个（17.1%），被截正文占全库 20.4% |
| 表格字符占比 | 59.7% |
| 行覆盖 / 重叠重复 | 100% / 19.9% |

## 已知限制

这些是当前实现的真实短板，不是待办清单式的客套：

- **引用页码无效**：chunk 只存了行号区间，没有 `page`，答案里的 `relevant_pages` 拿不到真实页码。
- **LLM 重排未真正生效**：DashScope 分支的分数没有解析出来，实际排序接近纯向量相似度。
- **BM25 未接入**：`BM25Ingestor` / `BM25Retriever` 已实现，但主流程只走向量检索。
- **embedding 截断**：单条 2048 字符上限，超长 chunk（多为大表格）正文未进向量。
- **无评估集**：目前只有链路验证，没有 Recall@K 等指标。

## 数据与版权

年报、券商研报的版权归原发布机构，**本仓库不包含任何 PDF 与解析产物**。请自行准备合法来源的文档。

## License

MIT，见 [LICENSE](LICENSE)。上游版权声明（Copyright (c) 2025 IlyaRice）予以保留。
