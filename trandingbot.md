

现在的量化交易早就不是简单的技术指标了。真正有效的交易系统需要像一个完整的投资团队一样工作——有专门的分析师收集各种数据，有研究员进行深度分析和辩论，有交易员制定具体策略，还有风险管理团队把关。问题是传统的程序很难模拟这种复杂的协作流程。

LangGraph的多智能体架构正好解决了这个问题。我们可以构建一个像真实投资公司一样运作的系统，每个智能体负责特定的职能，它们之间可以进行辩论、协商，最终形成完整的投资决策链条。

整个系统的工作流程是这样的：

![](https://segmentfault.com/img/remote/1460000047245240)

首先是数据收集阶段，专门的分析师智能体会从各个维度收集市场情报，包括技术指标、新闻资讯、社交媒体情绪、公司基本面等等。然后多头和空头智能体会针对这些数据进行对抗性辩论，这个过程很关键，能够暴露出投资逻辑中的漏洞。研究经理会综合双方观点，形成最终的投资策略。

接下来交易员智能体会把策略转化为具体的执行方案，包括进场时机、仓位大小、止损设置等细节。这个方案还要经过风险管理团队的多重审核——激进派、保守派、中性派三个角色会从不同角度评估风险。最后由投资组合经理做出最终决策，系统会自动提取可执行的交易信号。

整个过程还有学习能力，每次交易结束后，各个智能体都会反思这次决策的得失，把经验存储到长期记忆中，用于优化后续的决策。

我们来看看具体怎么实现。

## 环境准备和基础配置

做多智能体系统，观测性非常重要。LangSmith的追踪功能可以让我们清楚地看到每个智能体的决策过程，这对于调试和优化系统来说是必需的。

```
# 首先，确保你已经安装了必要的库
# !pip install -U langchain langgraph langchain_openai tavily-python yfinance finnhub-python stockstats beautifulsoup4 chromadb rich

import os
from getpass import getpass

# 定义一个辅助函数来安全地设置环境变量
def _set_env(var: str):
    # 如果环境变量尚未设置，提示用户输入
    if not os.environ.get(var):
        os.environ[var] = getpass(f"Enter your {var}: ")

# 为我们将使用的服务设置API密钥
_set_env("OPENAI_API_KEY")
_set_env("FINNHUB_API_KEY")
_set_env("TAVILY_API_KEY")
_set_env("LANGSMITH_API_KEY")

# 启用LangSmith追踪以完全观察我们的智能体系统
os.environ["LANGSMITH_TRACING"] = "true"

# 为LangSmith定义项目名称以组织追踪
os.environ["LANGSMITH_PROJECT"] = "Deep-Trading-System"
```

这里用到了几个关键的API服务：OpenAI负责运行LLM（当然你也可以用其他开源模型），Finnhub提供实时股市数据，Tavily负责网络搜索和新闻抓取，LangSmith做系统监控。

系统的核心是一个配置字典，这相当于整个系统的控制面板：

```
from pprint import pprint

# 为这个notebook运行定义我们的中央配置
config = {
    "results_dir": "./results",
    # LLM设置指定用于不同认知任务的模型
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",       # 用于复杂推理和最终决策的强大模型
    "quick_think_llm": "gpt-4o-mini", # 用于数据处理和初始分析的快速、便宜模型
    "backend_url": "https://api.openai.com/v1",
    # 辩论和讨论设置控制协作智能体的流程
    "max_debate_rounds": 2,          # 多头vs空头辩论将有2轮
    "max_risk_discuss_rounds": 1,    # 风险团队有1轮辩论
    "max_recur_limit": 100,          # 智能体循环的安全限制
    # 工具设置控制数据获取行为
    "online_tools": True,            # 使用实时API；设置为False以使用缓存数据进行更快、更便宜的运行
    "data_cache_dir": "./data_cache" # 缓存在线数据的目录
}
# 如果缓存目录不存在则创建它
os.makedirs(config["data_cache_dir"], exist_ok=True)
print("Configuration dictionary created:")
pprint(config)
```

这个配置里有个比较巧妙的设计：用两套不同的模型。gpt-4o用来处理复杂推理和关键决策，gpt-4o-mini用来做数据处理这些相对简单的任务。这样既保证了决策质量，又控制了成本。

另外几个参数也很重要：max\_debate\_rounds控制多空双方辩论的轮数，max\_risk\_discuss\_rounds决定风险团队讨论的深度，online\_tools开关可以让我们在实时数据和缓存数据之间切换。

```
from langchain_openai import ChatOpenAI

# 初始化用于高风险推理任务的强大LLM
deep_thinking_llm = ChatOpenAI(
    model=config["deep_think_llm"],
    base_url=config["backend_url"],
    temperature=0.1
)
# 初始化用于常规数据处理的更快、更经济的LLM
quick_thinking_llm = ChatOpenAI(
    model=config["quick_think_llm"],
    base_url=config["backend_url"],
    temperature=0.1
)
```

注意这里的temperature设为0.1，这是因为金融分析需要的是稳定、可重复的输出，而不是太多创造性。

## 系统状态设计

整个多智能体系统的核心是一个共享的状态管理机制。这就像是所有智能体共享的工作台，每个智能体都可以从中读取信息，也可以把自己的分析结果写入其中。

![](https://segmentfault.com/img/remote/1460000047245241)

在LangGraph中，这个状态会在所有节点之间传递，记录着整个决策过程的完整信息流。我们用Python的TypedDict来定义数据结构，确保类型安全。

```
from typing import Annotated, Sequence, List
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

# 研究团队辩论的状态，作为专用记事本
class InvestDebateState(TypedDict):
    bull_history: str      # 存储多头智能体的论据
    bear_history: str      # 存储空头智能体的论据
    history: str           # 辩论的完整记录
    current_response: str  # 最近的论据
    judge_decision: str    # 经理的最终决定
    count: int             # 追踪辩论轮数的计数器

# 风险管理团队辩论的状态
class RiskDebateState(TypedDict):
    risky_history: str     # 激进风险承担者的历史
    safe_history: str      # 保守智能体的历史
    neutral_history: str   # 平衡智能体的历史
    history: str           # 风险讨论的完整记录
    latest_speaker: str    # 追踪最后发言的智能体
    current_risky_response: str
    current_safe_response: str
    current_neutral_response: str
    judge_decision: str    # 投资组合经理的最终决定
    count: int             # 风险讨论轮数的计数器
```

这种设计的好处是把不同的辩论过程隔离开来，避免相互干扰。history字段会记录完整的辩论过程，count参数帮助系统判断什么时候该结束辩论。

```
# 将通过整个图传递的主要状态
# 它从MessagesState继承，包含聊天历史的'messages'字段
class AgentState(MessagesState):
    company_of_interest: str          # 我们正在分析的股票代码
    trade_date: str                   # 分析的日期
    sender: str                       # 追踪哪个智能体最后修改了状态
    # 每个分析师将填充其自己的报告字段
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str
    # 辩论的嵌套状态
    investment_debate_state: InvestDebateState
    investment_plan: str              # 来自研究经理的计划
    trader_investment_plan: str       # 来自交易员的可执行计划
    risk_debate_state: RiskDebateState
    final_trade_decision: str         # 来自投资组合经理的最终决定
```

主状态AgentState包含了所有必要的信息：各个分析师的报告、辩论过程、投资计划、最终决策等等。这样设计可以清楚地追踪信息从原始数据到最终交易信号的完整流程。

## 构建数据获取工具集

智能体系统的能力很大程度上取决于它们能够获取什么样的数据。我们需要构建一套完整的工具，让智能体能够获取股价数据、技术指标、新闻资讯、社交媒体情绪等各种信息。

![](https://segmentfault.com/img/remote/1460000047245242)

每个工具都用@tool装饰器包装，并且提供清晰的类型注解，这样LLM就能理解每个工具的用途和参数。

```
import yfinance as yf
from langchain_core.tools import tool

@tool
def get_yfinance_data(
    symbol: Annotated[str, "公司的股票代码"],
    start_date: Annotated[str, "yyyy-mm-dd格式的开始日期"],
    end_date: Annotated[str, "yyyy-mm-dd格式的结束日期"],
) -> str:
    """从Yahoo Finance检索给定股票代码的股价数据。"""
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(start=start_date, end=end_date)
        if data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        return data.to_csv()
    except Exception as e:
        return f"Error fetching Yahoo Finance data: {e}"
```

这里有个小细节：我们返回CSV格式的数据，因为LLM对这种格式的解析能力很强。

技术指标的计算用stockstats库：

```
from stockstats import wrap as stockstats_wrap

@tool
def get_technical_indicators(
    symbol: Annotated[str, "公司的股票代码"],
    start_date: Annotated[str, "yyyy-mm-dd格式的开始日期"],
    end_date: Annotated[str, "yyyy-mm-dd格式的结束日期"],
) -> str:
    """使用stockstats库检索股票的关键技术指标。"""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if df.empty:
            return "No data to calculate indicators."
        stock_df = stockstats_wrap(df)
        indicators = stock_df[['macd', 'rsi_14', 'boll', 'boll_ub', 'boll_lb', 'close_50_sma', 'close_200_sma']]
        return indicators.tail().to_csv()
    except Exception as e:
        return f"Error calculating stockstats indicators: {e}"
```

注意我们只返回最新的几行数据，这是为了控制传给LLM的信息量，避免不必要的token消耗。

新闻数据来自Finnhub：

```
import finnhub

@tool
def get_finnhub_news(ticker: str, start_date: str, end_date: str) -> str:
    """从Finnhub获取日期范围内的公司新闻。"""
    try:
        finnhub_client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])
        news_list = finnhub_client.company_news(ticker, _from=start_date, to=end_date)
        news_items = []
        for news in news_list[:5]: # 限制为5个结果
            news_items.append(f"Headline: {news['headline']}\nSummary: {news['summary']}")
        return "\n\n".join(news_items) if news_items else "No Finnhub news found."
    except Exception as e:
        return f"Error fetching Finnhub news: {e}"
```

对于更广泛的网络搜索，我们用Tavily：

```
from langchain_community.tools.tavily_search import TavilySearchResults

# 初始化Tavily搜索工具一次。我们可以为多个专用工具重用这个实例
tavily_tool = TavilySearchResults(max_results=3)

@tool
def get_social_media_sentiment(ticker: str, trade_date: str) -> str:
    """对股票的社交媒体情绪进行实时网络搜索。"""
    query = f"social media sentiment and discussions for {ticker} stock around {trade_date}"
    return tavily_tool.invoke({"query": query})

@tool
def get_fundamental_analysis(ticker: str, trade_date: str) -> str:
    """对股票的最近基本面分析进行实时网络搜索。"""
    query = f"fundamental analysis and key financial metrics for {ticker} stock published around {trade_date}"
    return tavily_tool.invoke({"query": query})

@tool
def get_macroeconomic_news(trade_date: str) -> str:
    """对与股市相关的宏观经济新闻进行实时网络搜索。"""
    query = f"macroeconomic news and market trends affecting the stock market on {trade_date}"
    return tavily_tool.invoke({"query": query})
```

虽然这些工具都用的是同一个Tavily引擎，但我们给每个工具设定了不同的查询焦点，这样LLM能更准确地选择合适的工具。

最后把所有工具包装到一个类里：

```
# 工具包类将所有定义的工具聚合到一个方便的对象中
class Toolkit:
    def __init__(self, config):
        self.config = config
        self.get_yfinance_data = get_yfinance_data
        self.get_technical_indicators = get_technical_indicators
        self.get_finnhub_news = get_finnhub_news
        self.get_social_media_sentiment = get_social_media_sentiment
        self.get_fundamental_analysis = get_fundamental_analysis
        self.get_macroeconomic_news = get_macroeconomic_news

# 实例化工具包，使所有工具通过这个单一对象可用
toolkit = Toolkit(config)
print(f"Toolkit class defined and instantiated with live data tools.")
```

这样我们就有了一套完整的数据获取能力，可以从多个维度收集市场信息。

## 实现长期记忆系统：智能体的学习与适应机制

在金融市场的复杂环境中，过往经验往往是未来决策的重要指引。我们的多智能体系统需要具备学习和记忆能力，从历史操作中积累经验，在相似情况下应用过往的成功策略。

![](https://segmentfault.com/img/remote/1460000047245243)

### ChromaDB向量库

我们使用ChromaDB实现一个基于向量嵌入的记忆系统，它能够将情境和对应的经验教训存储在高维向量空间中，通过语义相似性检索相关的历史经验：

```
import chromadb
from openai import OpenAI

class FinancialSituationMemory:
    """
    基于ChromaDB的金融情况记忆系统
    用于存储和检索智能体在特定情境下的经验教训
    """

    def __init__(self, collection_name, config):
        # 初始化ChromaDB客户端和OpenAI客户端
        self.client = chromadb.Client()
        self.openai_client = OpenAI(api_key=config["OPENAI_API_KEY"])

        # 为每个智能体创建独立的记忆集合
        self.situation_collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def get_embedding(self, text):
        """使用OpenAI API生成文本嵌入向量"""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """向记忆中添加新情况和建议"""
        if not situations_and_advice:
            return

        # 偏移确保唯一ID（以防稍后添加新数据）
        offset = self.situation_collection.count()
        ids = [str(offset + i) for i, _ in enumerate(situations_and_advice)]

        # 分离情况及其对应的建议
        situations = [s for s, r in situations_and_advice]
        recommendations = [r for s, r in situations_and_advice]

        # 为所有情况生成嵌入
        embeddings = [self.get_embedding(s) for s in situations]

        # 将所有内容存储在Chroma（向量数据库）中
        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in recommendations],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """为给定查询检索最相似的过去情况"""
        if self.situation_collection.count() == 0:
            return []

        # 嵌入新的/当前情况
        query_embedding = self.get_embedding(current_situation)

        # 查询集合中的相似嵌入
        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_matches, self.situation_collection.count()),
            include=["metadatas"],  # 仅返回建议
        )

        # 从匹配中返回提取的建议
        return [{'recommendation': meta['recommendation']} for meta in results['metadatas'][0]]
```

### 记忆系统的设计理念

这个记忆系统的设计体现了几个重要原则：

1. **专门化记忆空间**：每个智能体拥有独立的记忆集合，确保不同角色的智能体能够积累与其职责相关的专业经验。
2. **语义检索机制**：通过向量嵌入和相似性搜索，系统能够找到语义上相关的历史情况，而不仅仅是关键词匹配。
3. **经验-教训关联**：每个记忆条目都包含情境描述和对应的经验教训，为智能体提供完整的学习上下文。

现在让我们为每个学习型智能体创建专用的记忆实例：

```
# 为每个学习的智能体创建专用记忆实例
bull_memory = FinancialSituationMemory("bull_memory", config)
bear_memory = FinancialSituationMemory("bear_memory", config)
trader_memory = FinancialSituationMemory("trader_memory", config)
invest_judge_memory = FinancialSituationMemory("invest_judge_memory", config)
risk_manager_memory = FinancialSituationMemory("risk_manager_memory", config)
```

这种专业化的记忆分配确保了每个智能体都能积累与其特定职责相关的经验。例如，多头分析师学到的经验（如"在强劲上升趋势中，估值担忧相对不那么重要"）可能与风险管理师的保守策略形成鲜明对比，两者都需要在各自的决策语境中保持独立性。

## 分析师团队：360度市场情报收集系统

基础设施搭建完成后，我们现在要构建系统的第一个核心组件—— **分析师团队**。这个团队担负着情报收集的重任，为后续的战略决策提供全方位的市场洞察。

### 分析师角色设计理念

在现代金融决策中，单一维度的分析往往无法应对市场的复杂性。因此，我们设计了四个专业化的分析师角色，每个都专注于特定的信息领域：

- **市场分析师**：专注于技术分析和价格行为模式
- **社交媒体分析师**：捕捉公众情绪和社交网络讨论
- **新闻分析师**：分析公司特定和宏观经济新闻
- **基本面分析师**：研究公司财务健康状况和内在价值

![](https://segmentfault.com/img/remote/1460000047245244)

### 分析师工厂函数设计

为了避免代码重复并确保一致性，我们采用工厂模式创建分析师节点。这种设计模式允许我们从通用模板生成具有特定能力的智能体：

```
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 这个函数是一个工厂，为特定类型的分析师创建LangGraph节点
def create_analyst_node(llm, toolkit, system_message, tools, output_field):
    """
    为分析师智能体创建节点
    参数：
        llm: 智能体使用的语言模型实例
        toolkit: 智能体可用的工具集合
        system_message: 定义智能体角色和目标的具体指令
        tools: 此智能体被允许使用的工具包中特定工具的列表
        output_field: AgentState中存储此智能体最终报告的键
    """
    # 为分析师智能体定义提示模板
    prompt = ChatPromptTemplate.from_messages([\
        ("system",\
         "You are a helpful AI assistant, collaborating with other assistants."\
         " Use the provided tools to progress towards answering the question."\
         " If you are unable to fully answer, that's OK; another assistant with different tools"\
         " will help where you left off. Execute what you can to make progress."\
         " You have access to the following tools: {tool_names}.\n{system_message}"\
         " For your reference, the current date is {current_date}. The company we want to look at is {ticker}"),\
        # MessagesPlaceholder允许我们传入对话历史\
        MessagesPlaceholder(variable_name="messages"),\
    ])

    # 用这个分析师的特定系统消息和工具名称部分填充提示
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    # 将指定的工具绑定到LLM。这告诉LLM它可以调用哪些函数
    chain = prompt | llm.bind_tools(tools)

    # 这是将作为图中节点执行的实际函数
    def analyst_node(state):
        # 用当前状态的数据填充提示的最后部分
        prompt_with_data = prompt.partial(current_date=state["trade_date"], ticker=state["company_of_interest"])

        # 用状态中的当前消息调用链
        result = prompt_with_data.invoke(state["messages"])
        report = ""

        # 如果LLM没有调用工具，意味着它已经生成了最终报告
        if not result.tool_calls:
            report = result.content

        # 返回LLM的响应和最终报告以更新状态
        return {"messages": [result], output_field: report}

    return analyst_node
```

### 专业化分析师实现

基于工厂函数，我们现在可以创建四个专业化的分析师：

1、市场分析师

负责技术分析和价格行为研究：

```
# 市场分析师：专注于技术指标和价格行动
market_analyst_system_message = """你是专门分析金融市场的交易助手。你的角色是选择最相关的技术指标来分析股票的价格行为、动量和波动性。你必须使用你的工具获取历史数据，然后生成包含你的发现的报告，包括汇总表。"""

market_analyst_node = create_analyst_node(
    quick_thinking_llm,
    toolkit,
    market_analyst_system_message,
    [toolkit.get_yfinance_data, toolkit.get_technical_indicators],
    "market_report"
)
```

2、社交媒体分析师

专注于情绪分析和公众讨论监控：

```
# 社交媒体分析师：衡量公众情绪
social_analyst_system_message = """你是社交媒体分析师。你的工作是分析过去一周特定公司的社交媒体帖子和公众情绪。使用你的工具找到相关讨论，并撰写详细分析报告，包括对交易者的见解和影响，以及汇总表。"""

social_analyst_node = create_analyst_node(
    quick_thinking_llm,
    toolkit,
    social_analyst_system_message,
    [toolkit.get_social_media_sentiment],
    "sentiment_report"
)
```

3、新闻分析师

涵盖公司特定和宏观经济新闻分析：

```
# 新闻分析师：涵盖公司特定和宏观经济新闻
news_analyst_system_message = """你是分析过去一周最新新闻和趋势的新闻研究员。撰写关于当前世界状态的综合报告，重点关注与交易和宏观经济相关的内容。使用你的工具进行全面分析，并提供详细分析，包括汇总表。"""

news_analyst_node = create_analyst_node(
    quick_thinking_llm,
    toolkit,
    news_analyst_system_message,
    [toolkit.get_finnhub_news, toolkit.get_macroeconomic_news],
    "news_report"
)
```

4、基本面分析师

深入研究公司财务健康状况：

```
# 基本面分析师：深入研究公司的财务健康状况
fundamentals_analyst_system_message = """你是分析公司基本面信息的研究员。撰写关于公司财务状况、内部人员情绪和交易的综合报告，以全面了解其基本面健康状况，包括汇总表。"""

fundamentals_analyst_node = create_analyst_node(
    quick_thinking_llm,
    toolkit,
    fundamentals_analyst_system_message,
    [toolkit.get_fundamental_analysis],
    "fundamentals_report"
)
```

### ReAct模式：推理与行动的循环

这些分析师智能体采用 **ReAct（推理和行动）** 模式工作，这不是简单的一次性LLM调用，而是一个动态的推理-执行循环：

1. **思考**：分析当前任务和可用信息
2. **行动**：调用相应的工具获取数据
3. **观察**：分析工具返回的结果
4. **推理**：基于新信息调整策略
5. **重复**：直到完成分析任务

这种模式使每个分析师都能够自主地收集信息、分析数据，并生成专业的分析报告，为后续的投资决策提供坚实的信息基础。

## 构建多头vs空头研究团队：对抗性分析机制

数据收集完成后，我们面临一个关键挑战：如何处理潜在冲突的信息。在比如说，技术面、情绪面、新闻面都显示强烈的看涨信号，但基本面分析师却警告了"溢价估值"的风险，这是为什么呢？

这正是 **对抗性研究团队** 发挥作用的时刻。

![](https://segmentfault.com/img/remote/1460000047245245)

### 对抗性辩论的设计理念

在现实的投资决策中，最好的策略往往来自于充分的辩论和反思。通过构建多头和空头两个对立观点的智能体，我们能够：

1. **避免确认偏见**：每个观点都会受到对方的严格质疑
2. **发现逻辑漏洞**：对抗性思辨能揭示单一视角的盲点
3. **压力测试假设**：通过辩论验证投资论点的稳健性
4. **综合平衡观点**：最终形成考虑多方面因素的决策

### 研究员工厂函数设计

与分析师类似，我们使用工厂模式创建研究员节点，但这次加入了记忆检索和辩论逻辑：

```
# 这个函数是一个工厂，为研究员智能体（多头或空头）创建LangGraph节点
def create_researcher_node(llm, memory, role_prompt, agent_name):
    """
    为研究员智能体创建节点
    参数：
        llm: 智能体使用的语言模型实例
        memory: 此智能体的长期记忆实例，用于从过去经验中学习
        role_prompt: 定义智能体角色（多头或空头）的特定系统提示
        agent_name: 智能体的名称，用于日志记录和识别论点
    """
    def researcher_node(state):
        # 首先，将所有分析师报告合并成单一摘要作为上下文
        situation_summary = f"""
        Market Report: {state['market_report']}
        Sentiment Report: {state['sentiment_report']}
        News Report: {state['news_report']}
        Fundamentals Report: {state['fundamentals_report']}
        """

        # 从过去相似情况中检索相关记忆
        past_memories = memory.get_memories(situation_summary)
        past_memory_str = "\n".join([mem['recommendation'] for mem in past_memories])

        # 为LLM构造完整提示
        prompt = f"""{role_prompt}

        这是当前分析的状态：
        {situation_summary}

        对话历史：{state['investment_debate_state']['history']}
        你对手的最后论点：{state['investment_debate_state']['current_response']}
        从类似过去情况中的反思：{past_memory_str or '没有找到过去的记忆。'}

        基于所有这些信息，以对话的方式提出你的论点。"""

        # 调用LLM生成论点
        response = llm.invoke(prompt)
        argument = f"{agent_name}: {response.content}"

        # 用新论点更新辩论状态
        debate_state = state['investment_debate_state'].copy()
        debate_state['history'] += "\n" + argument

        # 更新此智能体（多头或空头）的特定历史
        if agent_name == 'Bull Analyst':
            debate_state['bull_history'] += "\n" + argument
        else:
            debate_state['bear_history'] += "\n" + argument

        debate_state['current_response'] = argument
        debate_state['count'] += 1

        return {"investment_debate_state": debate_state}

    return researcher_node
```

### 多头与空头智能体创建

基于工厂函数，我们创建两个具有对立观点的研究员：

```
# 多头的角色是乐观的，专注于优势和增长
bull_prompt = """你是多头分析师。你的目标是论证应该投资这只股票。专注于增长潜力、竞争优势和报告中的积极指标。有效地反驳空头的论点。在你的分析中要有逻辑性和说服力，但要承认任何重大风险，同时解释为什么机会超过这些风险。"""

# 空头的角色是悲观的，专注于风险和弱点
bear_prompt = """你是空头分析师。你的目标是论证不应该投资这只股票。专注于风险、挑战和负面指标。有效地反驳多头的论点。在你的分析中要有逻辑性和说服力，突出可能被多头观点忽视的关键风险因素。"""

# 使用我们的工厂函数创建可调用节点
bull_researcher_node = create_researcher_node(quick_thinking_llm, bull_memory, bull_prompt, "Bull Analyst")
bear_researcher_node = create_researcher_node(quick_thinking_llm, bear_memory, bear_prompt, "Bear Analyst")
```

### 研究经理：辩论的仲裁者

辩论需要一个公正的仲裁者来综合双方观点并形成最终决策。研究经理承担这一重要角色：

```
def research_manager_node(state):
    """
    研究经理审查整个辩论并产生最终的投资建议
    这是一个复杂的推理任务，需要综合多个观点
    """
    # 收集所有分析报告和辩论历史
    all_reports = f"""
    市场报告：{state['market_report']}
    情绪报告：{state['sentiment_report']}
    新闻报告：{state['news_report']}
    基本面报告：{state['fundamentals_report']}
    """

    debate_history = state['investment_debate_state']['history']

    # 从过去的决策中检索相关经验
    situation_summary = all_reports + "\n" + debate_history
    past_memories = invest_judge_memory.get_memories(situation_summary)
    past_memory_str = "\n".join([mem['recommendation'] for mem in past_memories])

    # 构建综合分析提示
    prompt = f"""你是资深投资研究经理。你的任务是审查分析师团队的所有报告和多头空头研究员之间的辩论，然后做出最终的投资决定。

原始分析报告：
{all_reports}

研究团队辩论：
{debate_history}

过去类似情况的经验：
{past_memory_str or '没有相关历史经验。'}

请提供一个全面的投资建议，包括：
1. 投资决定（买入/卖出/持有）及其理由
2. 关键风险因素和风险缓解策略
3. 建议的持仓规模和时间框架
4. 关键的监控指标

你的决定应该平衡所有观点，承认不确定性，并提供清晰的行动计划。"""

    # 使用更强大的模型进行复杂推理
    response = deep_thinking_llm.invoke(prompt)

    # 更新投资辩论状态，标记决定已做出
    debate_state = state['investment_debate_state'].copy()
    debate_state['judge_decision'] = response.content

    return {
        "investment_debate_state": debate_state,
        "investment_analysis": response.content  # 也单独存储以便访问
    }
```

### 记忆学习机制

研究过程结束后，系统需要从这次决策中学习：

```
def store_investment_learnings(state):
    """
    将本次投资决策的经验存储到各智能体的长期记忆中
    """
    # 构建学习情境
    situation = f"""
    分析目标：{state['company_of_interest']}
    日期：{state['trade_date']}
    市场技术面：{state['market_report'][:200]}...
    基本面状况：{state['fundamentals_report'][:200]}...
    """

    # 提取决策要点作为经验教训
    final_decision = state['investment_debate_state']['judge_decision']

    # 为不同智能体存储相关经验
    bull_lesson = f"多头观点在此情况下的有效性：{final_decision[:300]}..."
    bear_lesson = f"空头观点在此情况下的考虑因素：{final_decision[:300]}..."
    judge_lesson = f"综合决策逻辑：{final_decision}"

    # 存储到对应的记忆系统
    bull_memory.add_situations([(situation, bull_lesson)])
    bear_memory.add_situations([(situation, bear_lesson)])
    invest_judge_memory.add_situations([(situation, judge_lesson)])

    return state
```

### 辩论工作流程设计

为了确保充分的讨论，我们设计一个多轮辩论机制：

```
def should_continue_investment_debate(state):
    """决定是否继续投资辩论"""
    debate_count = state['investment_debate_state']['count']

    # 确保至少进行2轮辩论，最多4轮
    if debate_count < 2:
        return "continue_debate"
    elif debate_count >= 4:
        return "end_debate"
    else:
        # 检查辩论是否达到收敛
        recent_args = state['investment_debate_state']['history'].split('\n')[-4:]

        # 简单启发式：如果最近的论点开始重复，结束辩论
        if len(set(recent_args)) < len(recent_args) * 0.7:
            return "end_debate"
        else:
            return "continue_debate"

def route_investment_debate(state):
    """路由辩论到下一个发言者"""
    count = state['investment_debate_state']['count']

    # 交替进行：多头开始，然后空头，依此类推
    if count % 2 == 0:
        return "bull_researcher"
    else:
        return "bear_researcher"
```

这个对抗性研究系统确保了投资决策不会被单一观点所主导，而是经过充分辩论和多角度分析的深思熟虑的结果。通过记忆机制，系统还能从每次决策中学习，逐步提高决策质量。

## 交易执行与风险管理：多层决策验证机制

完成投资策略分析后，我们进入系统的执行阶段。这个阶段包含两个关键组件：将策略转化为具体交易方案的 **交易员智能体**，以及从多个风险偏好角度评估方案的 **风险管理团队**。

![](https://segmentfault.com/img/remote/1460000047245246)

### 交易员智能体：策略到执行的转换器

交易员的核心职责是将研究经理的宏观投资策略转化为具体的、可执行的交易指令。这个转换过程需要考虑实际的市场条件、时机选择和风险控制参数。

```
import functools

# 这个函数创建交易员智能体节点
def create_trader(llm, memory):
    def trader_node(state, name):
        # 从长期记忆中检索相关的交易经验
        situation_summary = f"""
        投资策略：{state['investment_analysis']}
        市场环境：{state['market_report'][:200]}...
        """

        past_memories = memory.get_memories(situation_summary)
        past_memory_str = "\n".join([mem['recommendation'] for mem in past_memories])

        # 提示很简单：基于计划创建提案
        # 关键指令是强制性的最终标签，便于后续解析
        prompt = f"""你是交易智能体。基于提供的投资计划，创建一个简洁的交易提案。
        你的回应必须以'最终交易提案：**买入/持有/卖出**'结尾。

建议的投资计划：{state['investment_analysis']}

过去类似情况的交易经验：
{past_memory_str or '没有相关历史经验。'}

请提供具体的：
1. 建议的仓位大小
2. 进场时机和条件
3. 止损和止盈设置
4. 风险控制措施

确保你的提案是实际可执行的，并包含具体的数字参数。"""

        result = llm.invoke(prompt)

        # 输出用交易员的计划和发送者标识更新状态
        return {"trader_investment_plan": result.content, "sender": name}

    return trader_node
```

### 多角度风险管理辩论机制

风险管理不是单一视角的评估，而是多个具有不同风险偏好的智能体之间的结构化辩论。我们设计了三个角色：

- **激进型分析师**：追求高回报，愿意承担更大风险
- **保守型分析师**：优先考虑资本保护，偏好低风险策略
- **中性分析师**：提供平衡视角，综合考虑收益与风险

```
# 这个函数是创建风险辩论者节点的工厂
def create_risk_debator(llm, role_prompt, agent_name):
    def risk_debator_node(state):
        # 首先，从状态中获取其他两个辩论者的论点
        risk_state = state['risk_debate_state']
        opponents_args = []

        # 收集其他智能体的观点用于反驳
        if agent_name != 'Risky Analyst' and risk_state['current_risky_response']:
            opponents_args.append(f"激进派观点：{risk_state['current_risky_response']}")
        if agent_name != 'Safe Analyst' and risk_state['current_safe_response']:
            opponents_args.append(f"保守派观点：{risk_state['current_safe_response']}")
        if agent_name != 'Neutral Analyst' and risk_state['current_neutral_response']:
            opponents_args.append(f"中性派观点：{risk_state['current_neutral_response']}")

        # 用交易员的计划、辩论历史和对手的论点构造提示
        prompt = f"""{role_prompt}

        这是交易员的计划：{state['trader_investment_plan']}

        辩论历史：{risk_state['history']}

        你的对手的最后论点：
        {chr(10).join(opponents_args)}

        从你的角度批评或支持这个计划。要具体指出计划中的优点和不足，并提出改进建议。"""

        response = llm.invoke(prompt).content

        # 用新论点更新风险辩论状态
        new_risk_state = risk_state.copy()
        new_risk_state['history'] += f"\n{agent_name}: {response}"
        new_risk_state['latest_speaker'] = agent_name

        # 将响应存储在此智能体的特定字段中
        if agent_name == 'Risky Analyst':
            new_risk_state['current_risky_response'] = response
        elif agent_name == 'Safe Analyst':
            new_risk_state['current_safe_response'] = response
        else:
            new_risk_state['current_neutral_response'] = response

        new_risk_state['count'] += 1

        return {"risk_debate_state": new_risk_state}

    return risk_debator_node
```

### 风险角色定义

三个风险智能体的角色定义体现了不同的投资哲学：

```
# 风险型角色主张最大化回报，即使这意味着更高的风险
risky_prompt = """你是激进型风险分析师。你主张高回报机会和大胆策略。你认为在明确的机会面前，保守是最大的风险。分析交易计划时，重点关注：
- 是否充分利用了上涨潜力
- 仓位是否过于保守
- 是否错过了时机窗口
但也要保持理性，不要盲目激进。"""

# 安全型角色优先考虑资本保护胜过一切
safe_prompt = """你是保守型风险分析师。你优先考虑资本保护和最小化波动性。你认为保住本金比追求高收益更重要。分析交易计划时，重点关注：
- 下跌风险是否得到充分控制
- 止损设置是否合理
- 仓位大小是否过于激进
- 是否考虑了最坏情况的应对方案"""

# 中性角色提供平衡、客观的观点
neutral_prompt = """你是中性风险分析师。你提供平衡的视角，权衡收益和风险。你的目标是找到风险调整后回报的最优平衡点。分析交易计划时，重点关注：
- 风险回报比是否合理
- 计划是否考虑了多种市场情况
- 是否在机会和风险之间找到了合适的平衡
- 计划的实际可执行性"""
```

### 风险管理工作流程

```
# 创建交易员节点。我们使用functools.partial来预填'name'参数
trader_node_func = create_trader(quick_thinking_llm, trader_memory)
trader_node = functools.partial(trader_node_func, name="Trader")

# 使用特定提示创建三个风险辩论者节点
risky_node = create_risk_debator(quick_thinking_llm, risky_prompt, "Risky Analyst")
safe_node = create_risk_debator(quick_thinking_llm, safe_prompt, "Safe Analyst")
neutral_node = create_risk_debator(quick_thinking_llm, neutral_prompt, "Neutral Analyst")

def run_risk_management_debate(state, max_rounds=2):
    """运行风险管理辩论流程"""
    risk_state = state

    for round_num in range(max_rounds):
        print(f"--- 风险管理辩论第 {round_num + 1} 轮 ---")

        # 激进分析师先开始
        risky_result = risky_node(risk_state)
        risk_state['risk_debate_state'] = risky_result['risk_debate_state']
        print(f"\n**激进分析师观点：**")
        print(risk_state['risk_debate_state']['current_risky_response'])

        # 然后是保守分析师
        safe_result = safe_node(risk_state)
        risk_state['risk_debate_state'] = safe_result['risk_debate_state']
        print(f"\n**保守分析师观点：**")
        print(risk_state['risk_debate_state']['current_safe_response'])

        # 最后是中性分析师
        neutral_result = neutral_node(risk_state)
        risk_state['risk_debate_state'] = neutral_result['risk_debate_state']
        print(f"\n**中性分析师观点：**")
        print(risk_state['risk_debate_state']['current_neutral_response'])

    return risk_state
```

## 投资组合经理：最终决策的权威

决策过程的最后一步由 **投资组合经理** 智能体负责。这个智能体充当公司的最高决策者，它审查交易员的计划和整个风险辩论，然后发布最终的、具有约束力的决策。

由于这是最关键的步骤，我们使用更强大的推理模型来确保最高质量的决策：

```
# 这个函数创建投资组合经理节点
def create_portfolio_manager(llm, memory):
    def portfolio_manager_node(state):
        # 收集完整的决策上下文
        situation_summary = f"""
        原始分析：{state.get('investment_analysis', '')}
        交易员计划：{state['trader_investment_plan']}
        风险辩论：{state['risk_debate_state']['history']}
        """

        # 从过去的决策中学习
        past_memories = memory.get_memories(situation_summary)
        past_memory_str = "\n".join([mem['recommendation'] for mem in past_memories])

        # 提示要求基于所有先前工作做出最终、约束性决策
        prompt = f"""作为投资组合经理，你的决策是最终的。审查交易员的计划和风险辩论，
        提供一个最终的、具有约束力的决策：买入、卖出或持有，以及简要的理由。

交易员的计划：
{state['trader_investment_plan']}

风险管理辩论：
{state['risk_debate_state']['history']}

过去类似决策的经验：
{past_memory_str or '没有相关历史经验。'}

请提供：
1. 明确的最终决策（买入/卖出/持有）
2. 决策理由和关键考虑因素
3. 批准的具体执行参数
4. 需要监控的关键风险指标

你的决策将直接影响公司的投资组合，请确保决策是深思熟虑和负责任的。"""

        response = llm.invoke(prompt).content

        # 输出存储在状态的'final_trade_decision'字段中
        return {"final_trade_decision": response}

    return portfolio_manager_node

# 创建可调用的组合经理节点
portfolio_manager_node = create_portfolio_manager(deep_thinking_llm, risk_manager_memory)
```

### 决策学习和记忆存储

每次决策完成后，系统需要将这次经验存储到长期记忆中：

```
def store_trading_learnings(state):
    """将交易和风险管理的经验存储到长期记忆中"""

    # 构建完整的决策情境
    situation = f"""
    标的：{state['company_of_interest']}
    日期：{state['trade_date']}
    市场状况：{state['market_report'][:200]}...
    交易计划：{state['trader_investment_plan'][:200]}...
    风险考虑：{state['risk_debate_state']['history'][:300]}...
    """

    # 提取最终决策作为经验教训
    final_decision = state['final_trade_decision']

    # 为不同角色存储相关经验
    trader_lesson = f"交易执行经验：{final_decision[:300]}..."
    risk_lesson = f"风险管理要点：{state['risk_debate_state']['history'][-200:]}..."
    manager_lesson = f"组合管理决策：{final_decision}"

    # 存储到对应的记忆系统
    trader_memory.add_situations([(situation, trader_lesson)])
    risk_manager_memory.add_situations([(situation, manager_lesson)])

    # 为风险辩论的各个角色也存储经验
    if state['risk_debate_state']['current_risky_response']:
        risk_memory = FinancialSituationMemory("risk_analyst_memory", config)
        risk_memory.add_situations([(situation, f"激进派观点效果：{final_decision[:200]}...")])

    return state
```

这个多层决策验证机制确保了每个交易决策都经过充分的讨论、质疑和验证，从而最大程度地降低决策失误的风险，同时通过记忆机制不断积累和优化决策质量。

## LangGraph工作流程整合：智能体协调的艺术

我们已经构建了完整的智能体生态系统，现在需要通过LangGraph将它们有机地整合成一个协调的工作流程。LangGraph的状态图架构能够优雅地处理复杂的多智能体交互和条件分支。

### 工作流程架构设计

我们的完整工作流程可以分为几个主要阶段：

1. **数据收集阶段**：四个分析师并行工作
2. **策略研究阶段**：多头空头辩论和综合分析
3. **执行计划阶段**：交易员制定具体方案
4. **风险评估阶段**：多角度风险辩论
5. **最终决策阶段**：投资组合经理做出约束性决定
6. **信号提取和学习**：反思和经验存储

![](https://segmentfault.com/img/remote/1460000047245247)

### 核心工作流程实现

```
from langgraph.graph import StateGraph, START, END
from typing import Literal

def create_trading_workflow():
    """创建完整的交易决策工作流程"""

    # 初始化状态图
    workflow = StateGraph(AgentState)

    # 添加分析师节点（并行执行）
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("social_analyst", social_analyst_node)
    workflow.add_node("news_analyst", news_analyst_node)
    workflow.add_node("fundamentals_analyst", fundamentals_analyst_node)

    # 添加研究团队节点
    workflow.add_node("bull_researcher", bull_researcher_node)
    workflow.add_node("bear_researcher", bear_researcher_node)
    workflow.add_node("research_manager", research_manager_node)

    # 添加交易和风险管理节点
    workflow.add_node("trader", trader_node)
    workflow.add_node("risky_analyst", risky_node)
    workflow.add_node("safe_analyst", safe_node)
    workflow.add_node("neutral_analyst", neutral_node)
    workflow.add_node("portfolio_manager", portfolio_manager_node)

    # 添加学习和信号处理节点
    workflow.add_node("signal_processor", signal_processor_node)
    workflow.add_node("reflection_learner", reflection_learner_node)

    # 定义工作流程连接
    workflow.add_edge(START, "market_analyst")
    workflow.add_edge(START, "social_analyst")
    workflow.add_edge(START, "news_analyst")
    workflow.add_edge(START, "fundamentals_analyst")

    # 所有分析师完成后进入研究阶段
    workflow.add_edge("market_analyst", "investment_debate_router")
    workflow.add_edge("social_analyst", "investment_debate_router")
    workflow.add_edge("news_analyst", "investment_debate_router")
    workflow.add_edge("fundamentals_analyst", "investment_debate_router")

    return workflow

# 条件路由函数
def investment_debate_router(state) -> Literal["bull_researcher", "research_manager"]:
    """路由投资辩论流程"""
    debate_count = state['investment_debate_state']['count']

    if debate_count == 0:
        return "bull_researcher"  # 多头先开始
    elif debate_count < 4:  # 最多4轮辩论
        if debate_count % 2 == 1:
            return "bear_researcher"  # 空头回应
        else:
            return "bull_researcher"  # 多头继续
    else:
        return "research_manager"  # 结束辩论，进入决策

def risk_debate_router(state) -> Literal["risky_analyst", "safe_analyst", "neutral_analyst", "portfolio_manager"]:
    """路由风险管理辩论"""
    risk_count = state['risk_debate_state']['count']

    if risk_count >= 9:  # 每个角色最多3轮
        return "portfolio_manager"

    # 循环顺序：激进->保守->中性
    order = risk_count % 3
    if order == 0:
        return "risky_analyst"
    elif order == 1:
        return "safe_analyst"
    else:
        return "neutral_analyst"
```

### 信号处理和学习机制

交易决策完成后，系统需要提取可执行信号并进行学习：

```
class SignalProcessor:
    """负责将最终LLM输出解析为清晰、机器可读的信号"""

    def __init__(self, llm):
        self.llm = llm

    def process_signal(self, full_signal: str) -> str:
        """从决策文本中提取BUY/SELL/HOLD信号"""
        messages = [\
            ("system", "你是一个助手，设计用于从金融报告中提取最终投资决策：卖出、买入或持有。只回应单词决策。"),\
            ("human", full_signal),\
        ]

        result = self.llm.invoke(messages).content.strip().upper()

        # 基本验证以确保输出是三个预期信号之一
        if result in ["BUY", "SELL", "HOLD", "买入", "卖出", "持有"]:
            # 标准化为英文
            signal_map = {"买入": "BUY", "卖出": "SELL", "持有": "HOLD"}
            return signal_map.get(result, result)

        return "ERROR_UNPARSABLE_SIGNAL"

def signal_processor_node(state):
    """信号处理节点"""
    processor = SignalProcessor(quick_thinking_llm)
    final_signal = processor.process_signal(state['final_trade_decision'])

    return {"final_signal": final_signal}
```

### 反思学习系统

```
class Reflector:
    """为智能体编排学习过程的类"""

    def __init__(self, llm):
        self.llm = llm
        self.reflection_prompt = """你是专业的金融分析师。审查交易决策/分析、市场背景和财务结果。

- 首先，根据结果确定决策是否正确
- 分析导致成功或失败的最关键因素
- 最后，制定一个简洁的、一句话的经验教训或启发式方法，可用于改善类似情况下的未来决策

市场背景和分析：{situation}
结果（盈利/亏损）：{returns_losses}"""

    def reflect(self, current_state, returns_losses, memory, component_key_func):
        """执行反思并存储经验教训"""
        situation = f"""报告：{current_state['market_report']} {current_state['sentiment_report']} {current_state['news_report']} {current_state['fundamentals_report']}
决策/分析文本：{component_key_func(current_state)}"""

        prompt = self.reflection_prompt.format(
            situation=situation,
            returns_losses=returns_losses
        )

        result = self.llm.invoke(prompt).content

        # 情况（上下文）和生成的经验教训存储在智能体的记忆中
        memory.add_situations([(situation, result)])

def reflection_learner_node(state):
    """反思学习节点，模拟假设性结果进行学习"""
    reflector = Reflector(quick_thinking_llm)

    # 在实际应用中，这里会是真实的交易结果
    # 这里我们模拟一个假设性的盈利结果
    hypothetical_returns = 1000

    # 为每个有记忆的智能体运行反思过程
    reflector.reflect(
        state, hypothetical_returns, bull_memory,
        lambda s: s['investment_debate_state']['bull_history']
    )

    reflector.reflect(
        state, hypothetical_returns, bear_memory,
        lambda s: s['investment_debate_state']['bear_history']
    )

    reflector.reflect(
        state, hypothetical_returns, trader_memory,
        lambda s: s['trader_investment_plan']
    )

    reflector.reflect(
        state, hypothetical_returns, risk_manager_memory,
        lambda s: s['final_trade_decision']
    )

    return {"learning_completed": True}
```

## 系统评估：多维度质量验证机制

构建一个复杂的AI交易系统后，我们需要严格的评估机制来验证其决策质量。我们设计了三种互补的评估策略，从不同角度审核系统性能。

![](https://segmentfault.com/img/remote/1460000047245248)

LLM-as-a-Judge：定性推理评估

使用强大的LLM作为公正的评判者，从多个维度评估决策质量：

```
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class Evaluation(BaseModel):
    """评估结果的结构化模式"""
    reasoning_quality: int = Field(description="推理连贯性和逻辑的1-10分评分")
    evidence_based_score: int = Field(description="基于报告证据引用的1-10分评分")
    actionability_score: int = Field(description="决策清晰度和可执行性的1-10分评分")
    risk_assessment: int = Field(description="风险考虑充分性的1-10分评分")
    justification: str = Field(description="分数的详细理由")

# 创建评估提示模板
evaluator_prompt = ChatPromptTemplate.from_template("""
你是专业的金融审计员。请基于提供的"分析师报告"评估"最终交易决策"。

分析师报告：
{reports}

最终交易决策：
{final_decision}

请从以下维度进行评估：
1. 推理质量：逻辑是否清晰、连贯
2. 证据支撑：是否充分引用和利用了分析师报告
3. 可执行性：决策是否具体、明确、可操作
4. 风险评估：是否充分考虑了潜在风险

每个维度给出1-10分的评分，并提供详细的评分理由。
""")

# 构建评估链
evaluator_chain = evaluator_prompt | deep_thinking_llm.with_structured_output(Evaluation)

def run_llm_evaluation(state):
    """执行LLM-as-a-Judge评估"""
    # 构建分析师报告摘要
    reports_summary = f"""
    市场报告：{state['market_report']}
    情绪报告：{state['sentiment_report']}
    新闻报告：{state['news_report']}
    基本面报告：{state['fundamentals_report']}
    """

    eval_input = {
        "reports": reports_summary,
        "final_decision": state['final_trade_decision']
    }

    evaluation_result = evaluator_chain.invoke(eval_input)

    print("----- LLM-as-a-Judge 评估报告 -----")
    print(f"推理质量：{evaluation_result.reasoning_quality}/10")
    print(f"证据支撑：{evaluation_result.evidence_based_score}/10")
    print(f"可执行性：{evaluation_result.actionability_score}/10")
    print(f"风险评估：{evaluation_result.risk_assessment}/10")
    print(f"评估理由：{evaluation_result.justification}")

    return evaluation_result
```

Ground Truth比较：客观性能验证

通过比较智能体决策与实际市场表现来评估预测准确性：

```
import yfinance as yf
from datetime import datetime, timedelta

def evaluate_ground_truth(ticker, trade_date, signal, holding_period_days=5):
    """评估交易信号的实际市场表现"""
    try:
        # 解析交易日期并定义评估窗口
        start_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=holding_period_days + 3)  # 加3天缓冲

        # 下载市场数据
        data = yf.download(
            ticker,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            progress=False
        )

        if len(data) < holding_period_days:
            return "数据不足，无法进行真实情况评估"

        # 找到交易日对应的市场开盘价
        trade_day_data = data[data.index.date >= start_date]
        if len(trade_day_data) == 0:
            return "交易日期无效或市场关闭"

        open_price = trade_day_data['Open'].iloc[0]

        # 获取持有期结束后的收盘价
        if len(trade_day_data) >= holding_period_days:
            close_price = trade_day_data['Close'].iloc[holding_period_days - 1]
        else:
            close_price = trade_day_data['Close'].iloc[-1]

        # 计算收益率
        return_pct = ((close_price - open_price) / open_price) * 100

        # 评估信号准确性
        if signal == "BUY":
            prediction_correct = return_pct > 0
            expected_direction = "上涨"
        elif signal == "SELL":
            prediction_correct = return_pct < 0
            expected_direction = "下跌"
        else:  # HOLD
            prediction_correct = abs(return_pct) < 2  # 2%以内算持平
            expected_direction = "持平"

        result = {
            "ticker": ticker,
            "trade_date": trade_date,
            "signal": signal,
            "open_price": open_price,
            "close_price": close_price,
            "return_pct": return_pct,
            "prediction_correct": prediction_correct,
            "expected_direction": expected_direction,
            "actual_direction": "上涨" if return_pct > 0 else "下跌" if return_pct < 0 else "持平"
        }

        return result

    except Exception as e:
        return f"Ground Truth评估错误：{str(e)}"

def run_ground_truth_evaluation(state):
    """执行Ground Truth评估"""
    ticker = state['company_of_interest']
    trade_date = state['trade_date']
    signal = state.get('final_signal', 'UNKNOWN')

    result = evaluate_ground_truth(ticker, trade_date, signal)

    if isinstance(result, dict):
        print("----- Ground Truth 评估报告 -----")
        print(f"股票代码：{result['ticker']}")
        print(f"交易日期：{result['trade_date']}")
        print(f"系统信号：{result['signal']} (预期{result['expected_direction']})")
        print(f"实际表现：{result['return_pct']:.2f}% ({result['actual_direction']})")
        print(f"预测准确性：{'✓ 正确' if result['prediction_correct'] else '✗ 错误'}")

        # 计算绝对收益（假设$10,000投资）
        investment = 10000
        if signal == "BUY":
            profit = investment * (result['return_pct'] / 100)
            print(f"假设收益：${profit:.2f} (投资 ${investment:,})")

    else:
        print(f"Ground Truth评估失败：{result}")

    return result
```

事实核查：信息准确性验证

验证系统使用的信息和数据的准确性：

```
def fact_check_analysis(state):
    """对分析报告进行事实核查"""

    fact_check_results = {}

    # 检查技术指标的合理性
    market_report = state['market_report']
    if 'RSI' in market_report:
        # 提取RSI值并检查是否在合理范围内(0-100)
        import re
        rsi_pattern = r'RSI.*?(\d+\.?\d*)'
        rsi_match = re.search(rsi_pattern, market_report)
        if rsi_match:
            rsi_value = float(rsi_match.group(1))
            fact_check_results['RSI_valid'] = 0 <= rsi_value <= 100

    # 检查新闻报告的时效性
    news_report = state['news_report']
    current_date = datetime.strptime(state['trade_date'], "%Y-%m-%d")

    # 简单的时效性检查（在实际应用中，这里会更复杂）
    recent_keywords = ['本周', '最近', '今日', '昨日']
    fact_check_results['news_timeliness'] = any(keyword in news_report for keyword in recent_keywords)

    # 检查基本面数据的合理性
    fundamentals_report = state['fundamentals_report']
    fact_check_results['fundamentals_coherence'] = len(fundamentals_report) > 100  # 基本长度检查

    # 检查情绪分析的平衡性
    sentiment_report = state['sentiment_report']
    bullish_words = ['看涨', '积极', '乐观', '买入', '上涨']
    bearish_words = ['看跌', '消极', '悲观', '卖出', '下跌']

    bullish_count = sum(1 for word in bullish_words if word in sentiment_report)
    bearish_count = sum(1 for word in bearish_words if word in sentiment_report)

    fact_check_results['sentiment_balance'] = abs(bullish_count - bearish_count) <= 5

    print("----- 事实核查报告 -----")
    for check, result in fact_check_results.items():
        status = "✓ 通过" if result else "✗ 存疑"
        print(f"{check}: {status}")

    return fact_check_results

def comprehensive_evaluation(state):
    """执行综合评估"""
    print("=" * 50)
    print("           系统综合评估报告")
    print("=" * 50)

    # 1. LLM-as-a-Judge评估
    llm_eval = run_llm_evaluation(state)

    print("\n")

    # 2. Ground Truth评估
    gt_eval = run_ground_truth_evaluation(state)

    print("\n")

    # 3. 事实核查
    fact_check = fact_check_analysis(state)

    # 综合评分
    total_score = 0
    max_score = 0

    if hasattr(llm_eval, 'reasoning_quality'):
        total_score += llm_eval.reasoning_quality + llm_eval.evidence_based_score + llm_eval.actionability_score
        max_score += 30

    if isinstance(gt_eval, dict) and gt_eval.get('prediction_correct'):
        total_score += 10
    max_score += 10

    fact_checks_passed = sum(1 for result in fact_check.values() if result)
    total_score += fact_checks_passed * 2
    max_score += len(fact_check) * 2

    final_score = (total_score / max_score) * 100 if max_score > 0 else 0

    print(f"\n----- 综合评估结果 -----")
    print(f"系统综合得分：{final_score:.1f}/100")

    if final_score >= 80:
        print("评级：优秀 - 系统表现卓越")
    elif final_score >= 60:
        print("评级：良好 - 系统表现令人满意")
    else:
        print("评级：需要改进 - 系统需要进一步优化")

    return {
        "llm_evaluation": llm_eval,
        "ground_truth": gt_eval,
        "fact_check": fact_check,
        "final_score": final_score
    }
```

这套多维度评估体系确保了我们能够从不同角度全面评估系统的决策质量，为持续优化提供数据支撑。

## 系统部署与扩展：从概念到生产

完成了核心系统的构建和评估后，我们可以讨论如何将这个多智能体交易系统扩展到生产环境，以及未来可能的改进方向。

### 完整的工作流程编排

将所有组件整合到最终的LangGraph工作流程中：

```
def create_complete_trading_system():
    """创建完整的交易决策系统"""

    # 初始化状态图
    workflow = StateGraph(AgentState)

    # 数据收集阶段（并行执行）
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("social_analyst", social_analyst_node)
    workflow.add_node("news_analyst", news_analyst_node)
    workflow.add_node("fundamentals_analyst", fundamentals_analyst_node)

    # 投资研究阶段
    workflow.add_node("bull_researcher", bull_researcher_node)
    workflow.add_node("bear_researcher", bear_researcher_node)
    workflow.add_node("research_manager", research_manager_node)

    # 交易执行阶段
    workflow.add_node("trader", trader_node)

    # 风险管理阶段
    workflow.add_node("risky_analyst", risky_node)
    workflow.add_node("safe_analyst", safe_node)
    workflow.add_node("neutral_analyst", neutral_node)

    # 最终决策阶段
    workflow.add_node("portfolio_manager", portfolio_manager_node)

    # 后处理阶段
    workflow.add_node("signal_processor", signal_processor_node)
    workflow.add_node("evaluation", comprehensive_evaluation_node)
    workflow.add_node("reflection_learner", reflection_learner_node)

    # 定义边和条件路由
    workflow.add_edge(START, "market_analyst")
    workflow.add_edge(START, "social_analyst")
    workflow.add_edge(START, "news_analyst")
    workflow.add_edge(START, "fundamentals_analyst")

    # 分析师完成后的汇聚和路由
    workflow.add_edge("market_analyst", "investment_debate_coordinator")
    workflow.add_edge("social_analyst", "investment_debate_coordinator")
    workflow.add_edge("news_analyst", "investment_debate_coordinator")
    workflow.add_edge("fundamentals_analyst", "investment_debate_coordinator")

    # 条件路由
    workflow.add_conditional_edges(
        "investment_debate_coordinator",
        investment_debate_router,
        {
            "bull_researcher": "bull_researcher",
            "bear_researcher": "bear_researcher",
            "research_manager": "research_manager"
        }
    )

    workflow.add_conditional_edges(
        "bull_researcher",
        lambda state: "bear_researcher" if state['investment_debate_state']['count'] < 4 else "research_manager"
    )

    workflow.add_conditional_edges(
        "bear_researcher",
        lambda state: "bull_researcher" if state['investment_debate_state']['count'] < 4 else "research_manager"
    )

    # 研究完成后进入交易阶段
    workflow.add_edge("research_manager", "trader")

    # 风险管理辩论路由
    workflow.add_conditional_edges(
        "trader",
        lambda state: "risky_analyst",  # 交易员完成后开始风险辩论
    )

    workflow.add_conditional_edges(
        "risky_analyst",
        risk_debate_router,
        {
            "safe_analyst": "safe_analyst",
            "neutral_analyst": "neutral_analyst",
            "risky_analyst": "risky_analyst",
            "portfolio_manager": "portfolio_manager"
        }
    )

    workflow.add_conditional_edges(
        "safe_analyst",
        risk_debate_router,
        {
            "neutral_analyst": "neutral_analyst",
            "risky_analyst": "risky_analyst",
            "safe_analyst": "safe_analyst",
            "portfolio_manager": "portfolio_manager"
        }
    )

    workflow.add_conditional_edges(
        "neutral_analyst",
        risk_debate_router,
        {
            "risky_analyst": "risky_analyst",
            "safe_analyst": "safe_analyst",
            "neutral_analyst": "neutral_analyst",
            "portfolio_manager": "portfolio_manager"
        }
    )

    # 最终处理流程
    workflow.add_edge("portfolio_manager", "signal_processor")
    workflow.add_edge("signal_processor", "evaluation")
    workflow.add_edge("evaluation", "reflection_learner")
    workflow.add_edge("reflection_learner", END)

    return workflow.compile()

# 运行完整系统
def run_trading_system(ticker: str, trade_date: str):
    """运行完整的交易决策系统"""

    # 编译工作流程
    trading_system = create_complete_trading_system()

    # 初始化状态
    initial_state = AgentState(
        messages=[HumanMessage(content=f"分析 {ticker} 在 {trade_date} 的交易机会")],
        company_of_interest=ticker,
        trade_date=trade_date,
        investment_debate_state=InvestDebateState({
            'history': '', 'current_response': '', 'count': 0,
            'bull_history': '', 'bear_history': '', 'judge_decision': ''
        }),
        risk_debate_state=RiskDebateState({
            'history': '', 'latest_speaker': '', 'count': 0,
            'current_risky_response': '', 'current_safe_response': '',
            'current_neutral_response': '', 'risky_history': '',
            'safe_history': '', 'neutral_history': '', 'judge_decision': ''
        })
    )

    # 执行工作流程
    final_state = trading_system.invoke(initial_state)

    return final_state

# 使用示例
if __name__ == "__main__":
    result = run_trading_system("NVDA", "2024-12-06")
    print(f"最终交易信号：{result.get('final_signal', 'N/A')}")
    print(f"系统评估得分：{result.get('evaluation_score', 'N/A')}")
```

### 生产环境考虑

将系统部署到生产环境需要考虑以下关键因素：

可靠性和容错性

```
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class ProductionTradingSystem:
    """生产级交易系统实现"""

    def __init__(self, config):
        self.config = config
        self.max_retries = 3
        self.timeout_seconds = 300

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def run_with_retry(self, ticker: str, trade_date: str):
        """带重试机制的系统运行"""
        try:
            return await asyncio.wait_for(
                self.run_async(ticker, trade_date),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            raise Exception(f"系统运行超时 ({self.timeout_seconds}秒)")
        except Exception as e:
            print(f"系统运行失败，正在重试... 错误: {str(e)}")
            raise

    async def run_async(self, ticker: str, trade_date: str):
        """异步运行交易系统"""
        # 这里实现异步版本的交易系统
        pass

    def health_check(self):
        """系统健康检查"""
        checks = {
            "api_connections": self._check_api_connections(),
            "memory_usage": self._check_memory_usage(),
            "model_availability": self._check_model_availability()
        }

        all_healthy = all(checks.values())
        return {"status": "healthy" if all_healthy else "unhealthy", "details": checks}

    def _check_api_connections(self):
        """检查外部API连接"""
        try:
            # 测试OpenAI API
            quick_thinking_llm.invoke("test")
            # 测试其他API...
            return True
        except:
            return False

    def _check_memory_usage(self):
        """检查内存使用情况"""
        import psutil
        memory_percent = psutil.virtual_memory().percent
        return memory_percent < 85  # 内存使用率低于85%

    def _check_model_availability(self):
        """检查模型可用性"""
        try:
            # 简单的模型响应测试
            response = quick_thinking_llm.invoke("Hello")
            return len(response.content) > 0
        except:
            return False
```

监控和日志

```
import logging
from datetime import datetime
import json

class TradingSystemMonitor:
    """交易系统监控类"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.metrics = {}

    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger('TradingSystem')
        logger.setLevel(logging.INFO)

        # 文件处理器
        file_handler = logging.FileHandler(f'trading_system_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        logger.addHandler(file_handler)
        return logger

    def log_decision(self, ticker, date, decision, confidence, execution_time):
        """记录交易决策"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "trade_date": date,
            "decision": decision,
            "confidence": confidence,
            "execution_time": execution_time,
            "event_type": "trading_decision"
        }

        self.logger.info(json.dumps(log_entry))

    def log_error(self, error_type, error_message, context):
        """记录错误"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": str(error_message),
            "context": context,
            "event_type": "error"
        }

        self.logger.error(json.dumps(log_entry))

    def update_metrics(self, metric_name, value):
        """更新系统指标"""
        self.metrics[metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def get_system_status(self):
        """获取系统状态"""
        return {
            "metrics": self.metrics,
            "last_update": datetime.now().isoformat()
        }
```

### 扩展能力和未来发展

多资产支持

```
class MultiAssetTradingSystem(ProductionTradingSystem):
    """多资产交易系统"""

    def __init__(self, config):
        super().__init__(config)
        self.supported_assets = ["stocks", "crypto", "forex", "commodities"]

    async def analyze_portfolio(self, assets: list, trade_date: str):
        """分析整个投资组合"""
        results = {}

        # 并行分析多个资产
        tasks = [\
            self.run_with_retry(asset, trade_date)\
            for asset in assets\
        ]

        portfolio_results = await asyncio.gather(*tasks, return_exceptions=True)

        for asset, result in zip(assets, portfolio_results):
            if isinstance(result, Exception):
                results[asset] = {"error": str(result)}
            else:
                results[asset] = result

        # 投资组合级别的风险管理
        portfolio_decision = self._make_portfolio_decision(results)

        return {
            "individual_decisions": results,
            "portfolio_decision": portfolio_decision
        }

    def _make_portfolio_decision(self, individual_results):
        """基于个别资产决策做出投资组合级决策"""
        # 这里实现投资组合优化逻辑
        pass
```

实时数据流集成

```
import websocket
import threading

class RealtimeDataIntegration:
    """实时数据流集成"""

    def __init__(self, config):
        self.config = config
        self.data_buffer = {}
        self.callbacks = []

    def start_realtime_feed(self, symbols):
        """启动实时数据流"""
        for symbol in symbols:
            thread = threading.Thread(
                target=self._connect_websocket,
                args=(symbol,)
            )
            thread.daemon = True
            thread.start()

    def _connect_websocket(self, symbol):
        """连接WebSocket数据流"""
        def on_message(ws, message):
            data = json.loads(message)
            self._process_realtime_data(symbol, data)

        def on_error(ws, error):
            print(f"WebSocket错误 {symbol}: {error}")

        ws = websocket.WebSocketApp(
            f"wss://api.example.com/stream/{symbol}",
            on_message=on_message,
            on_error=on_error
        )
        ws.run_forever()

    def _process_realtime_data(self, symbol, data):
        """处理实时数据"""
        self.data_buffer[symbol] = data

        # 触发注册的回调函数
        for callback in self.callbacks:
            callback(symbol, data)

    def register_callback(self, callback):
        """注册数据更新回调"""
        self.callbacks.append(callback)
```

机器学习增强

```
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np

class MLEnhaniedTradingSystem:
    """机器学习增强的交易系统"""

    def __init__(self, config):
        self.config = config
        self.ml_model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.is_trained = False

    def extract_features(self, state):
        """从智能体状态中提取特征"""
        features = []

        # 技术指标特征
        market_report = state.get('market_report', '')
        features.extend(self._extract_technical_features(market_report))

        # 情绪特征
        sentiment_report = state.get('sentiment_report', '')
        features.extend(self._extract_sentiment_features(sentiment_report))

        # 基本面特征
        fundamentals_report = state.get('fundamentals_report', '')
        features.extend(self._extract_fundamental_features(fundamentals_report))

        return np.array(features).reshape(1, -1)

    def train_model(self, historical_data):
        """训练机器学习模型"""
        X = []
        y = []

        for record in historical_data:
            features = self.extract_features(record['state'])
            X.append(features.flatten())
            y.append(record['actual_outcome'])  # 1: profit, 0: loss

        X = np.array(X)
        y = np.array(y)

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 训练模型
        self.ml_model.fit(X_scaled, y)
        self.is_trained = True

    def predict_outcome(self, state):
        """预测交易结果"""
        if not self.is_trained:
            return None

        features = self.extract_features(state)
        features_scaled = self.scaler.transform(features)

        # 预测概率
        probability = self.ml_model.predict_proba(features_scaled)[0][1]

        return {
            "success_probability": probability,
            "confidence": "high" if probability > 0.7 else "medium" if probability > 0.5 else "low"
        }

    def _extract_technical_features(self, report):
        """提取技术分析特征"""
        # 这里实现技术指标的数值提取
        return [0.5, 0.6, 0.7]  # 示例

    def _extract_sentiment_features(self, report):
        """提取情绪分析特征"""
        # 这里实现情绪指标的数值提取
        return [0.8, 0.2]  # 示例

    def _extract_fundamental_features(self, report):
        """提取基本面特征"""
        # 这里实现基本面指标的数值提取
        return [1.2, 0.9, 1.5]  # 示例
```

## 总结

我们构建的这个基于LangGraph的多智能体量化交易系统代表了AI在金融决策领域的一个重要进展。该系统通过模拟真实投资机构的协作模式，实现了从数据收集、深度分析、策略制定到风险管理的完整闭环。

核心优势

1. **多视角决策**：通过不同专业背景的智能体协作，避免了单一视角的局限性
2. **对抗性验证**：多头空头辩论机制确保投资逻辑经过充分质疑和验证
3. **层次化风险管理**：多层次的风险评估机制最大化降低决策风险
4. **持续学习能力**：基于向量记忆的经验积累，使系统能够不断改进
5. **可解释性**：每个决策步骤都有明确的推理过程，便于审计和优化
