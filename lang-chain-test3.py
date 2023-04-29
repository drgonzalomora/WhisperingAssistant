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
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex

os.environ["OPENAI_API_KEY"] = openai_key


class SQLAlchemyCustomCache(SQLAlchemyCache):
    """Cache that uses SQAlchemy as a backend."""

    EMBEDDING_DIM = 384
    EMBEDDING_INDEX_FILENAME = 'embedding_index2.ann'

    def __init__(self, engine):
        super().__init__(engine)
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
        self.embedding_index = AnnoyIndex(self.EMBEDDING_DIM, 'angular')

        if os.path.exists(self.EMBEDDING_INDEX_FILENAME):
            self.embedding_index = AnnoyIndex(self.EMBEDDING_DIM, 'angular')
            self.embedding_index.load(self.EMBEDDING_INDEX_FILENAME)
        else:
            self.embedding_index = self._build_embedding_index()

    def _build_embedding_index(self):
        embedding_index = AnnoyIndex(self.EMBEDDING_DIM, 'angular')

        with Session(self.engine) as session:
            stmt = select(self.cache_schema.prompt)
            rows = session.execute(stmt).fetchall()
            prompts = [row[0] for row in rows]

        embeddings = self.embedding_model.encode(prompts)
        for i, embedding in enumerate(embeddings):
            embedding_index.add_item(i, embedding)

        embedding_index.build(10)
        embedding_index.save(self.EMBEDDING_INDEX_FILENAME)

        return embedding_index

    def lookup(self, prompt: str, llm_string: str) -> Optional[RETURN_VAL_TYPE]:
        """Look up based on prompt and llm_string."""
        stmt = (
            select(self.cache_schema.response)
            .where(self.cache_schema.prompt == prompt)
            .where(self.cache_schema.llm == llm_string)
            .order_by(self.cache_schema.idx)
        )

        # 📌 TODO: look for the top results in terms of similarity, checking the similar prompts from the vector database.
        prompt_embedding = self.embedding_model.encode(prompt)
        similar_prompt_indices = self.embedding_index.get_nns_by_vector(prompt_embedding,
                                                                        10)  # Adjust the number of similar prompts as needed
        print("similar_prompt_indices", similar_prompt_indices)

        stmt = (
            select(self.cache_schema.response)
            .where(self.cache_schema.prompt == prompt)
            .where(self.cache_schema.llm == llm_string)
            .order_by(self.cache_schema.idx)
        )

        with Session(self.engine) as session:
            rows = session.execute(stmt).fetchall()
            if rows:
                return [Generation(text=row[0]) for row in rows]
        return None

    def update(self, prompt: str, llm_string: str, return_val: RETURN_VAL_TYPE) -> None:
        """Update based on prompt and llm_string."""
        items = [
            self.cache_schema(prompt=prompt, llm=llm_string, response=gen.text, idx=i)
            for i, gen in enumerate(return_val)
        ]

        print("itemsitems", items)

        # 📌 TODO: Create an embedding for these items and save those in a vector database.
        prompt_embedding = self.embedding_model.encode(prompt)
        idx = self.embedding_index.get_n_items()

        # Create a new index and add the new item
        updated_embedding_index = AnnoyIndex(self.EMBEDDING_DIM, 'angular')
        for i in range(idx):
            existing_embedding = self.embedding_index.get_item_vector(i)
            updated_embedding_index.add_item(i, existing_embedding)
        updated_embedding_index.add_item(idx, prompt_embedding)
        updated_embedding_index.build(10)
        updated_embedding_index.save(self.EMBEDDING_INDEX_FILENAME)

        # Replace the current index with the updated one
        self.embedding_index = updated_embedding_index

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
