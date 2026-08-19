from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, RedirectResponse  
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document import DocumentService
import mimetypes 

from app.core.dependencies import get_document_service, get_current_user, get_project_service
from app.services.project import ProjectService
import logging
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

document_router= APIRouter(
    tags=["documents"]
)



# #GET /document/<document_id> - Download document, if the user has access to the corresponding project
# @app.get("/document/{document_id}")
# async def download_document(document_id: int):
#     # Check if the user has access to the project associated with the document
#     # If access is granted, return the document file for download
#     pass
@document_router.get("/document/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        file_source, original_filename = await document_service.get_document_path_for_download(
            document_id=document_id,
            current_user=current_user
        )
        if file_source.startswith("http://") or file_source.startswith("https://"):
            return RedirectResponse(url=file_source)

        
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            mime_type = "application/octet-stream"


        
        return FileResponse(    
            path=file_source,
            filename=original_filename,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}"'
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error downloading document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while downloading the file."
        )



# #PUT /document/<document_id> - Update document
# @app.put("/document/{document_id}")
# async def update_document(document_id: int):
#     # Check if the user has access to the project associated with the document
#     # If access is granted, update the document details (e.g., file name, file type)
#     pass

@document_router.put("/document/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_document(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(..., description="File to upload"),

    ):
    try:
        return await document_service.update_project_for_authorized_user(
            document_id=document_id,  
            current_user=current_user,
            file=file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
          
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
          
    except Exception as e:
        logger.error(f"Unexpected error updating document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while updating the document."
        )
    

# #DELETE /document/<document_id> - Delete document and remove it from the corresponding project
# @app.delete("/document/{document_id}")
# async def delete_document(document_id: int):
#     # Check if the user has access to the project associated with the document
#     # If access is granted, delete the document and remove it from the project
#     pass

@document_router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
    

    ):
    try:
        return await document_service.delete_project_for_authorized_user(
            document_id=document_id,  
            current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
          
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
          
    except Exception as e:
        logger.error(f"Unexpected error updating document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while updating the document."
        )
    