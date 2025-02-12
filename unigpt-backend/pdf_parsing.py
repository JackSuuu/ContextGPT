import os
import json
import logging
import shutil

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
# Removed Ollama import
from langchain.chat_models import ChatOpenAI  # Import ChatOpenAI for Groq

import chromadb.api.client

# Set up logging to the console
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def process_pdf(pdf_file_path: str) -> str:
    logger.info("Starting PDF processing")
    
    # --- Read PDF content ---
    try:
        loader = PdfReader(pdf_file_path)
    except Exception as e:
        logger.error("Error reading PDF: %s", e)
        st.error("Error reading PDF file.")
        raise e

    raw_text = ""
    num_pages = len(loader.pages)
    logger.info(f"PDF has {num_pages} pages")
    
    for i, page in enumerate(loader.pages):
        try:
            content = page.extract_text()
            if content:
                raw_text += content
            else:
                logger.warning(f"Page {i+1} has no content.")
        except Exception as e:
            logger.error("Error extracting text from page %d: %s", i+1, e)
    
    logger.info("Extracted raw text length: %d characters", len(raw_text))
    
    # --- Split text into chunks ---
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=10,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    logger.info("Split text into %d chunks", len(chunks))
    
    # --- Initialize embeddings and vectorstore ---
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Clear the system cache to refresh the database content.
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        chroma_client.reset()  # This will clear the database
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        persist_directory = "docs/chroma_db"
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
            logger.info("Removed existing Chroma database content.")
        logger.info("Chroma system cache cleared.")
    except Exception as e:
        logger.warning("Failed to clear Chroma cache: %s", e)
    
    persist_directory = "docs/chroma_db"
    if os.path.exists(persist_directory):
        logger.info("Persist directory exists at: %s", persist_directory)
    else:
        logger.info("Persist directory does not exist and will be created: %s", persist_directory)
    
    try:
        # Create the vector store from texts
        vectordb = Chroma.from_texts(chunks, embedding_function, persist_directory=persist_directory)
        logger.info("Created Chroma vectorstore from texts.")
        vectordb.persist()
        logger.info("Persisted vectorstore to disk.")
    except Exception as e:
        logger.error("Error creating or persisting vectorstore: %s", e)
        raise e

    try:
        # Reload the vector store to ensure we're using the latest persisted data
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
        logger.info("Reloaded vectorstore from persist directory.")
    except Exception as e:
        logger.error("Error reloading vectorstore: %s", e)
        raise e

    # --- Initialize the LLM and QA chain using Groq model ---
    try:
        # Set up Groq API environment variables
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
            print(api_key)
        else:
            raise ValueError("OPENAI_API_KEY not found in the .env file")
        llm = ChatOpenAI(model_name="llama-3.3-70b-versatile", temperature=0.7)
        logger.info("Initialized Groq LLM using ChatOpenAI.")
    except Exception as e:
        logger.error("Error initializing Groq LLM: %s", e)
        raise e
    
    try:
        retriever = vectordb.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=False
        )
        logger.info("Initialized RetrievalQA chain.")
    except Exception as e:
        logger.error("Error initializing QA chain: %s", e)
        raise e

    # --- Get summary from the QA chain using a prompt ---
    try:
        chain_result = qa_chain("Can you give me a summary of the context I gave, be super clear and explicit?")
        answer = chain_result["result"]
        logger.info("Obtained summary from QA chain.")
    except Exception as e:
        logger.error("Error obtaining summary from QA chain: %s", e)
        raise e

    # --- Save summary to JSON ---
    try:
        summary_path = "docs/summaries.json"
        all_summaries = {"summary": answer}
        with open(summary_path, "w") as f:
            json.dump(all_summaries, f)
        logger.info("Saved summary to %s", summary_path)
    except Exception as e:
        logger.error("Error saving summary to JSON: %s", e)
    
    return answer
