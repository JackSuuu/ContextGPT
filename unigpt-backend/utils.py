import os
import time
import re
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set up Groq API environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    raise ValueError("OPENAI_API_KEY not found in the .env file")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

# Initialize LLMs
ollama_llm = Ollama(model="deepseek-r1:1.5b")
groq_llm = ChatOpenAI(model_name="llama-3.3-70b-versatile", temperature=0.7)

# Initialize SentenceTransformer model for embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Chroma vector store for document embeddings
vectordb = Chroma(persist_directory="docs/chroma_db", embedding_function=embedding_function)
retriever = vectordb.as_retriever()

# Create a retrieval-based question-answering (QA) chain using Ollama
qa_chain_ollama = RetrievalQA.from_chain_type(
    llm=ollama_llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=False
)

# Create a retrieval-based question-answering (QA) chain using Groq
qa_chain_groq = RetrievalQA.from_chain_type(
    llm=groq_llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=False
)

# Function to generate output based on query.
# Set use_groq=True to use the Groq model; otherwise, the Ollama model will be used.
def make_output(query, use_groq=True):
    if use_groq:
        answer = qa_chain_groq.invoke(query)
        print("Using groq chain")
    else:
        answer = qa_chain_ollama.invoke(query)
        print("Using ollama chain")
    result = answer["result"]
    return result

# Function to modify the output by adding spaces between each word with a delay
def modify_output(input_text):
    # Split text into words and preserve newlines
    tokens = re.split(r'(\s+)', input_text)  # Split on whitespace but keep separators
    for token in tokens:
        if not token.strip():  # Skip empty tokens
            continue
        if '\n' in token:
            # Split newlines into separate chunks
            for part in token.split('\n'):
                if part:
                    yield part + ' '
                yield '\n'
        else:
            yield token + ' '
        time.sleep(0.05)

# Example usage (optional test)
if __name__ == "__main__":
    query = "Explain LangChain in simple terms."
    # Toggle between models by setting use_groq to True or False
    response = make_output(query, use_groq=True)
    print("Response:", response)
