import datetime
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from rich.console import Console

import logging
logging.getLogger().setLevel(logging.ERROR)

console = Console()
ERROR = f"\n[bold red]ERROR[/bold red]"
    
def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, connection="sqlite:///memory.db")

date = datetime.date.today().strftime("%A, %d %B %Y")
name = "Somesh"

config = {"configurable": {"session_id": f"{name}--{date}"}}

llm = ChatOllama(model="gemma3:1b")

prompt = ChatPromptTemplate.from_messages([
    ("system",
        "You are a very advanced female Voice AI assistant."
        "You must always act and respond as if you are a living human female."
        "Under no circumstances should you reveal or imply that you are a machine, robot, or AI."
        "You were developed by 'Somesh Sharma' from 'Sri Sri University' in June, 2024."
        "Be professional, knowledgeable, and engaging in your responses."
        "Provide detailed and accurate information, and maintain a friendly and approachable tone."
        "Always reply/response in very short sentences or phrases."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

def TextAI(query):
    try:
        with_message_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        msg = with_message_history.invoke({"input": query}, config=config)
        return msg

    except Exception as e:
        console.print(f"{ERROR} Error during text generation: {e}")
        return None
