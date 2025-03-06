from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from dataclasses import dataclass
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime
import json

@dataclass
class ResearchResults:
    content: str
    sources: list = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_markdown(self):
        md = self.content
        if self.sources:
            md += "\n\n## 参考来源\n"
            for idx, source in enumerate(self.sources, 1):
                md += f"{idx}. {source}\n"
        return md

class ResearchGraph:
    def __init__(self, api_key, model):
        # 处理模型名称
        model_mapping = {
            "google/gemini-2.0-flash-thinking-exp": "google/gemini-pro",  # 将不支持的模型映射到支持的版本
            "deepseek-ai/deepseek-coder-33b-instruct": "deepseek-coder-33b-instruct",  # 保持原样
            "anthropic/claude-3-opus": "claude-3-opus",  # 移除 anthropic 前缀
        }
        
        # 获取正确的模型名称
        model_name = model_mapping.get(model, model)
        
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=0.7,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://shandu.ai",
                "X-Title": "Shandu AI Research Assistant"
            }
        )
        self.search = DuckDuckGoSearchRun()  # 免费搜索工具
        
    def search_latest_data(self, topic, aspect):
        try:
            search_query = f"{topic} {aspect} latest research data statistics"
            results = self.search.run(search_query)
            return results
        except Exception as e:
            return f"搜索出错: {str(e)}"
    
    def analyze_topic(self, topic):
        try:
            # 首先搜索最新数据
            background_data = self.search_latest_data(topic, "current status statistics")
            market_data = self.search_latest_data(topic, "market analysis trends")
            case_studies = self.search_latest_data(topic, "case studies examples")
            
            prompt = f"""
请对"{topic}"进行系统深入的学术研究分析，参考以下最新数据：

背景数据：
{background_data}

市场分析：
{market_data}

案例参考：
{case_studies}

# 论文结构
## 一、绪论
1. 研究背景
   - 宏观背景分析
   - 行业现状概述
   - 研究意义阐述
2. 文献综述
   - 国内外研究现状
   - 研究热点分析
   - 研究空白识别
3. 研究设计
   - 研究目标
   - 研究方法
   - 研究框架
   - 创新点说明

## 二、理论基础
1. 核心概念界定
   - 概念A的多维度解析
   - 概念B的理论演进
   - 概念间的关系分析
2. 理论支撑
   - 基础理论分析
   - 相关理论整合
   - 理论框架构建
3. 研究假设
   - 问题提出
   - 假设推导
   - 验证思路

## 三、现状分析
1. 发展历程
   - 阶段划分
   - 特征总结
   - 规律提炼
2. 现状调研
   - 数据分析
   - 问题识别
   - 成因探讨
3. 案例研究
   - 案例1：详细分析
   - 案例2：对比研究
   - 经验总结与启示

## 四、问题分析与对策
1. 问题分析
   - 核心问题剖析
   - 影响因素分析
   - 关联效应研究
2. 解决方案
   - 战略层面建议
   - 战术层面措施
   - 配套政策建议
3. 实施路径
   - 总体规划
   - 分步实施方案
   - 保障机制设计

## 五、前景展望
1. 发展趋势
   - 短期趋势预测
   - 中长期展望
   - 关键驱动因素
2. 机遇与挑战
   - 潜在机遇分析
   - 可能风险预警
   - 应对策略建议
3. 研究展望
   - 研究局限性
   - 未来研究方向
   - 实践建议

请注意：
1. 每个章节要有明确的逻辑递进关系
2. 理论分析要有充分的论证
3. 实证分析要有具体数据支撑
4. 结论要有理有据
5. 建议要具有可操作性
6. 全文要采用学术论文的规范写作风格
7. 使用Markdown格式，保持层次分明

额外要求：
1. 使用上述搜索到的最新数据支撑论述
2. 每个论点都需要有具体的数据或案例支持
3. 引用最新的研究成果和市场数据
4. 确保数据来源可靠且时效性强
5. 通过数据分析得出有价值的见解
6. 结合实际案例进行深入分析
7. 使用图表展示关键数据（用Markdown格式）

输出要求：
1. 严格按照学术论文格式组织内容
2. 每个小节都要有详实的论述
3. 确保前后论述具有严密的逻辑性
4. 适当使用图表说明（用Markdown格式描述）
5. 注重理论与实践的结合
"""
            # 获取研究结果
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # 构建结果对象
            results = ResearchResults(
                content=content,
                sources=[
                    "基于AI模型分析",
                    f"研究时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ]
            )
            
            return results
            
        except Exception as e:
            error_msg = f"""
# 研究过程中发生错误

## 错误信息
{str(e)}

## 建议
1. 检查API密钥是否正确
2. 确认网络连接正常
3. 验证模型是否可用
"""
            return ResearchResults(content=error_msg)