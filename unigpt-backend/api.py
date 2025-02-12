from fastapi import FastAPI, UploadFile, File
import os
import shutil
from pathlib import Path
from pdf_parsing import process_pdf  # Import your existing function
from utils import make_output, modify_output  # Import the functions from utils.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
import uvicorn
# import psutil

app = FastAPI()

# Allow cross-origin requests from Next.js
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/memory")
# def get_memory_usage():
#     process = psutil.Process()
#     mem_info = process.memory_info()
#     return {"rss": mem_info.rss / (1024 * 1024), "vms": mem_info.vms / (1024 * 1024)}


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class PDFResponse(BaseModel):
    summary: str

@app.post("/api/upload_pdf/", response_model=PDFResponse)
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=422, 
            detail="Only PDF files are allowed"
        )

    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=422,
            detail="File size exceeds 10MB limit"
        )
    
    # Reset file cursor after reading
    await file.seek(0)
    
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        summary = process_pdf(str(file_path))
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"PDF processing failed: {str(e)}"
        )

class QueryRequest(BaseModel):
    query: str
    use_groq: bool = True

@app.post("/api/generate_output/")
async def generate_output(request: QueryRequest):
    try:
        response = make_output(request.query, request.use_groq)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Hello, Cloud Run!"}

# if __name__ == "__main__":
#     import os
#     port = int(os.getenv("PORT", 8080))  # Ensure it uses PORT 8080
#     uvicorn.run(app, host="0.0.0.0", port=port)