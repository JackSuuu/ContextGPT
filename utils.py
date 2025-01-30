import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
import time

# Load environment variables from .env file - api key
load_dotenv(dotenv_path='.env')
api_key = os.getenv("API_KEY")
# Initalize SentenceTransformer model for embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# Initalize Chroma vector store for document embeddings
# and create retriever from the vector store
vectordb = Chroma(persist_directory="docs/chroma_db", embedding_function=embedding_function)
retriever = vectordb.as_retriever()
# Initalize OpenAI language model with temperature parameter
llm = ChatOpenAI(api_key=api_key, temperature = 0.9, model='deepseek-reasoner', base_url="https://api.deepseek.com/v1")
# Create a retrieval-based question-answering (QA) chain
# based on a [redefined] chain type "stuff"
qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type="stuff",
                                       retriever=retriever,
                                       return_source_documents=True,
                                       verbose=False)
# Function to generate output based on query
def make_output(query):
    # Query the QA chain and extract the result
    answer = qa_chain(query)
    result = answer["result"]
    return result

# Function to modify the output by adding spaces between each word with a delay
def modify_output(input):
    # Iterative over each word in the input string
    for text in input.split():
        # Yield the word in the input string
        yield text + " "
        time.sleep(0.05)
    

