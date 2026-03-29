import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List

# Custom model loader and response generator using local models
from model_loader import load_model, generate_response

# Custom RAG implementation for retrieving relevant document chunks based on user queries
from rag import build_vectorstore

# Custom database manager for storing chat contexts and histories
from db_manager import save_chat, get_chat_data

# Custom file reader using PyPDF2 for PDFs and easyocr for images
from file_reader import file_read

# FastAPI for building the backend API, handling file uploads, and managing chat interactions
app = FastAPI()

# CORS middleware for allowing cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the frontend URL instead of "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local model with 4-bit quantization for efficient inference

# Tested models:
# Qwen/Qwen2.5-3B-Instruct
# Qwen/Qwen3-4B-Instruct-2507
# ibm-granite/granite-3.1-2b-instruct, 
# microsoft/Phi-4-mini-instruct
# iFaz/llama32_3B_en_emo_2000_stp
load_model('Qwen/Qwen3-4B-Instruct-2507') 


#print("--------------------------Model loaded successfully--------------------------")


# Read uploaded files, extract text, and return combined text 
@app.post("/process-files")
async def process_files(chat_id: str = Form(...), files: List[UploadFile] = File(...)):
    combined_text = ""
    for file in files:
        combined_text += await file_read(file) + "\n"
    
    # Save the extracted text in the database 
    save_chat(chat_id, context=combined_text)
    # Build the RAG vectorstore with the extracted text for later retrieval during chat interactions
    build_vectorstore(chat_id, combined_text)  
    
    return {"status": "success"}

@app.post("/chat")
async def chat_response(chat_id: str = Form(...), message: str = Form(...)):
    # Save the extracted text in the database and retrieve the context and history for the given chat_id
    context, history = get_chat_data(chat_id)
    
    if not context:
        return {"response": "Error: Please upload documents first."}

    response = generate_response(chat_id=chat_id, context=context, message=message, chat_history=history)
    
    # Update and save the chat history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    save_chat(chat_id, history=history)
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)