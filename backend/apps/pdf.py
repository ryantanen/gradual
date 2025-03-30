from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from bson import ObjectId
from .db import pdfs
from .auth import get_current_user
import pdfplumber
import io
from datetime import datetime

router = APIRouter(
    prefix="/pdfs",
    tags=["pdfs"]
)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a PDF file and save its content to MongoDB"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read the file content
        content = await file.read()
        # Extract text and metadata from PDF using pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text_content = ""
            for page in pdf.pages:
                text_content += page.extract_text()
            
            # Get creation date from metadata
            metadata = pdf.metadata
            creation_date = metadata.get('ModDate') if metadata else None
            
            # If no creation date in metadata, use current time
            if not creation_date:
                creation_date = datetime.now()
            else:
                # Parse the PDF date format (usually D:YYYYMMDDHHmmSS)
                try:
                    # Remove 'D:' prefix if present and parse the date
                    date_str = creation_date.replace('D:', '')
                    creation_date = datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
                except:
                    creation_date = datetime.now()
        
        # Create PDF document
        pdf_doc = {
            "filename": file.filename,
            "title": file.filename.rsplit('.', 1)[0],  # Use filename without extension as title
            "content": text_content,
            "user_id": str(current_user["_id"]),
            "datetime": creation_date
        }
        
        # Save to MongoDB
        result = await pdfs.insert_one(pdf_doc)
        
        return {
            "message": "PDF uploaded successfully",
            "pdf_id": str(result.inserted_id),
            "filename": file.filename,
            "creation_date": creation_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

async def get_user_pdfs(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """Get user's PDFs with pagination"""
    user_id = str(current_user["_id"])
    
    # Get total count
    total = await pdfs.count_documents({"user_id": user_id})
    
    # Get PDFs with pagination
    cursor = pdfs.find({"user_id": user_id})
    cursor = cursor.sort("filename", 1)  # Sort by filename ascending
    cursor = cursor.skip(skip).limit(limit)
    
    pdf_list = await cursor.to_list(None)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "pdfs": pdf_list
    }

@router.get("/count")
async def count_pdfs(current_user: dict = Depends(get_current_user)):
    """Get total count of PDFs for the user"""
    user_id = str(current_user["_id"])
    
    count = await pdfs.count_documents({"user_id": user_id})
    
    return {"total": count}

@router.get("/{pdf_id}")
async def get_pdf(
    pdf_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific PDF by ID"""
    user_id = current_user["_id"]
    
    pdf = await pdfs.find_one({
        "_id": ObjectId(pdf_id),
        "user_id": user_id
    })
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Convert ObjectId to string before returning
    pdf["_id"] = str(pdf["_id"])
    
    return pdf