from langchain.document_loaders import WebBaseLoader

from utils.config_reader import read_config


config = read_config()
OPEN_API_KEY = config.get("API_Key","OpenAI")

loader = WebBaseLoader("https://sites.google.com/view/dialogrobotcompe3/schedule?authuser=0")
data = loader.load()

for sp in data:
    print(sp)
    print("-"*100)
print(type(data[0]))
print(data[0]["page_content"])
print("="*100)
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationSummaryMemory

for sp in all_splits:
    print(sp)
    print("-"*100)
# embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
# vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)

# from langchain.chat_models import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain


# llm = ChatOpenAI(openai_api_key=OPEN_API_KEY,model="gpt-4")
# retriever = vectorstore.as_retriever()

# memory = ConversationSummaryMemory(llm=llm,memory_key="chat_history",return_messages=True)
# qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

# print(qa("スケジュールを教えて"))
