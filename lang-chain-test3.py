import time
from typing import Any, Optional

from langchain import LLMMathChain, OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.callbacks import get_openai_callback
import os
import langchain
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from whispering_assistant.configs.config import openai_key
from whispering_assistant.utils.performance import print_time_profile
from langchain.cache import SQLAlchemyCache, RETURN_VAL_TYPE
from langchain.schema import Generation

os.environ["OPENAI_API_KEY"] = openai_key


class SQLAlchemyCustomCache(SQLAlchemyCache):
    """Cache that uses SQAlchemy as a backend."""

    def __init__(self, engine):
        super().__init__(engine)

    def lookup(self, prompt: str, llm_string: str) -> Optional[RETURN_VAL_TYPE]:
        """Look up based on prompt and llm_string."""
        stmt = (
            select(self.cache_schema.response)
            .where(self.cache_schema.prompt == prompt)
            .where(self.cache_schema.llm == llm_string)
            .order_by(self.cache_schema.idx)
        )
        with Session(self.engine) as session:
            rows = session.execute(stmt).fetchall()
            print("rows", rows)

            if rows:
                return [Generation(text=row[0]) for row in rows]
        return None

    def update(self, prompt: str, llm_string: str, return_val: RETURN_VAL_TYPE) -> None:
        """Update based on prompt and llm_string."""
        items = [
            self.cache_schema(prompt=prompt, llm=llm_string, response=gen.text, idx=i)
            for i, gen in enumerate(return_val)
        ]
        with Session(self.engine) as session, session.begin():
            for item in items:
                session.merge(item)

    def clear(self, **kwargs: Any) -> None:
        """Clear cache."""
        with Session(self.engine) as session:
            session.execute(self.cache_schema.delete())


class SQLiteCustomCache(SQLAlchemyCustomCache):
    """Cache that uses SQLite as a backend."""

    def __init__(self, database_path: str = ".langchain.db"):
        """Initialize by creating the engine and all tables."""
        engine = create_engine(f"sqlite:///{database_path}")
        super().__init__(engine)


with get_openai_callback() as cb:
    langchain.llm_cache = SQLiteCustomCache(database_path=".langchain.db")
    llm = ChatOpenAI(temperature=0, cache=True)
    llm1 = OpenAI(model_name="text-davinci-003", temperature=0, cache=True)

    # start_time = time.time()
    # result = llm("Tell me a joke")
    # print(cb)
    # print(result)
    # print_time_profile(start_time, "1st")

    search = DuckDuckGoSearchRun()
    llm_math_chain = LLMMathChain(llm=llm1, verbose=True)

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

    mrkl = initialize_agent(tools, llm=llm1, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, cache=True)

    start_time = time.time()
    # mrkl.run("number of working hours for april 2023? considering the holidays in PH. Please give the answer in hours")
    mrkl.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?")
    print(cb)
    print_time_profile(start_time, "1st")
