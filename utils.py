import os
import time
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize SentenceTransformer model for embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Chroma vector store for document embeddings
vectordb = Chroma(persist_directory="docs/chroma_db", embedding_function=embedding_function)
retriever = vectordb.as_retriever()

# Initialize Ollama language model with DeepSeek-R1 (1.5B)
llm = Ollama(model="deepseek-r1:1.5b")

# Create a retrieval-based question-answering (QA) chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=False
)

# Function to generate output based on query
def make_output(query):
    answer = qa_chain.invoke(query)
    result = answer["result"]
    return result

# Function to modify the output by adding spaces between each word with a delay
def modify_output(input_text):
    for text in input_text.split():
        yield text + " "
        time.sleep(0.05)

# # Example query (optional test)
# if __name__ == "__main__":
#     query = "Explain the theory of relativity."
#     response = make_output(query)
#     print(response)
