import os
from langchain import OpenAI, LLMMathChain
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.tools import DuckDuckGoSearchRun
from tts_test import tts_chunk_by_chunk

os.environ["OPENAI_API_KEY"] = "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"

llm_chatgpt = ChatOpenAI(temperature=0)
search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions"
    )
]

memory = ConversationBufferMemory(memory_key="chat_history")
# memory.load_buffer('memory.pkl')
# print("memory", memory)

mrkl = initialize_agent(tools, llm=llm_chatgpt, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True,
                        memory=memory)

while True:
    input_string = input("Please enter the string to pass to the function: ")
    if input_string.lower() == 'exit':
        break
    else:
        result = mrkl.run(input_string)
        memory.save_buffer('memory.pkl')
        print("result", result)
        tts_chunk_by_chunk(result)

# mrkl.run("who is joshua's gf?")
# memory.save_buffer('memory.pkl')
