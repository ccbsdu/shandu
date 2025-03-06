
# Shandu API 文档

## ResearchGraph 类

### 初始化
```python
def __init__(
    self, 
    llm: Optional[ChatOpenAI] = None, 
    searcher: Optional[UnifiedSearcher] = None, 
    scraper: Optional[WebScraper] = None, 
    temperature: float = 0.5,
    date: Optional[str] = None
)
```

### 研究方法
```python
async def research(
    self, 
    query: str, 
    depth: int = 2, 
    breadth: int = 4, 
    progress_callback: Optional[Callable] = None,
    include_objective: bool = False,
    detail_level: str = "high" 
) -> ResearchResult
```

### 同步研究方法
```python
def research_sync(
    self, 
    query: str, 
    depth: int = 2, 
    breadth: int = 4, 
    progress_callback: Optional[Callable] = None,
    include_objective: bool = False,
    detail_level: str = "high"
) -> ResearchResult
```

## AISearcher 类

### 初始化
```python
def __init__(
    self,
    llm: Optional[ChatOpenAI] = None,
    searcher: Optional[UnifiedSearcher] = None,
    scraper: Optional[WebScraper] = None,
    max_results: int = 10,
    max_pages_to_scrape: int = 3
)
```

### 搜索方法
```python
async def search(
    self, 
    query: str,
    engines: Optional[List[str]] = None,
    detailed: bool = False,
    enable_scraping: bool = True
) -> AISearchResult
```
```

2. 技术实现文档：
```markdown:/Users/Mac/Traeproject/Shundu/shandu/docs/IMPLEMENTATION.md
# Shandu 技术实现文档

## 提示词工程

Shandu 使用精心设计的提示词模板：

- 查询明确化
- 研究规划
- 内容分析
- 源评估
- 报告生成
- 引用格式化

## 异步处理

广泛使用 async/await 模式：

- 并行搜索执行
- 并发网页抓取
- 高效内容处理
- 响应式UI更新

## 缓存系统

多级缓存机制：

- 搜索结果缓存
- 网页内容缓存
- 内容分析缓存
- LLM响应缓存

## 研究算法优化

我们的研究算法针对以下方面进行优化：

1. **广度**：探索多个相关子主题
2. **深度**：深入重要细节
3. **收敛**：聚焦最相关信息
4. **覆盖**：确保主题全面探索
5. **源质量**：优先可靠权威来源
6. **综合**：创建连贯结构化报告
```

3. 集成指南：
```markdown:/Users/Mac/Traeproject/Shundu/shandu/docs/INTEGRATION.md
# Shandu 集成指南

## 集成方式

Shandu 设计了多种集成方式：

### CLI 接口
- 直接使用的命令行工具
- 支持批处理和自动化

### Python API
- 清晰文档化的API
- 支持其他应用集成

### 可扩展组件
- 添加新搜索引擎
- 自定义网页抓取器
- 定制处理步骤

### 自定义 LLM 支持
- 支持任何 LangChain 兼容的 LLM
- 灵活的模型配置

### 回调系统
- 进度跟踪
- 事件钩子
- 自定义处理器
```

