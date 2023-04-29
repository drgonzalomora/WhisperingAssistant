import time

from gptcache import Config
from langchain import LLMMathChain, OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.callbacks import get_openai_callback
import os
import langchain

from whispering_assistant.configs.config import openai_key
from whispering_assistant.utils.performance import print_time_profile
from langchain.cache import SQLiteCache

os.environ["OPENAI_API_KEY"] = openai_key

with get_openai_callback() as cb:
    langchain.llm_cache = SQLiteCache(database_path=".langchain.db")
    llm = OpenAI(temperature=0.5, cache=True)

    start_time = time.time()
    result = llm("Tell me a joke")
    print(cb)
    print(result)
    print_time_profile(start_time, "1st")

    search = DuckDuckGoSearchRun()
    llm_math_chain = LLMMathChain(llm=llm, verbose=True)

    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions"
        ),
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math"
        )
    ]

    mrkl = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, cache=True)

    start_time = time.time()
    mrkl.run("number of working hours for april 2023? considering the holidays in PH. Please give the answer in hours")
    print(cb)
    print_time_profile(start_time, "1st")
