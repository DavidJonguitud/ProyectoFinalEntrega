import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import (
    get_current_user,
    get_document_service,
    get_project_service,
)
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectInviteRequest,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.document import DocumentService
from app.services.project import ProjectService

logger = logging.getLogger(__name__)

project_router = APIRouter(tags=["projects"])

# # POST /projects - Create project from details (name, description). Automatically gives access to created project to user, making him the owner (admin of the project).
# @app.post("/projects")
# async def create_project():
#     # Create a new project with the provided details (name, description)
#     # Automatically assign the user as the owner of the project
#     pass

# Al injectar deberemos obtener y el usuario


@project_router.post(
    "/projects", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
async def create_project(
    project_data: ProjectCreate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await project_service.create_project(project_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # GET /projects - Get all projects, accessible for a user. Returns list of projects full info(details + documents).
# @app.get("/projects")
# async def get_projects():
#     # Retrieve all projects that the user has access to
#     # Return a list of projects with full information (details + documents)
#     pass


@project_router.get("/projects", status_code=status.HTTP_200_OK)
async def show_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
):
    try:
        return await project_service.get_projects_by_user(current_user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )
    # TODO ADD DOCUMENT RELATIONS


# # GET /project/<project_id>/info - Return project’s details, if user has access
# @app.get("/project/{project_id}/info")
# async def get_project_info(project_id: int):
#     # Retrieve the details of the specified project if the user has access
#     # Return the project's details (name, description)
#     pass
@project_router.get(
    "/project/{project_id}/info",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def show_project_details(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
):
    try:
        return await project_service.get_project_by_id_for_authorized_user(
            project_id, current_user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # PUT /project/<project_id>/info - Update projects details - name, description. Returns the updated project’s info
# @app.put("/project/{project_id}/info")
# async def update_project_info(project_id: int):
#     # Update the details of the specified project (name, description) if the user has access
#     # Return the updated project's information
#     pass
@project_router.put(
    "/project/{project_id}/info",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project_info(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
):
    try:
        return await project_service.update_project_for_authorized_user(
            project_id, project_data, current_user
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # DELETE /project/<project_id>- Delete project, can only be performed by the projects’ owner. Deletes the corresponding  documents
# @app.delete("/project/{project_id}")
# async def delete_project(project_id: int):
#     # Delete the specified project if the user is the owner
#     # Also delete all corresponding documents associated with the project
#     pass
@project_router.delete("/project/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        await project_service.delete_project_for_authorized_owner(
            project_id, current_user
        )
        return f"Project with id '{project_id}' successfully deleted"

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # GET /project/<project_id>/documents- Return all of the project's documents
# @app.get("/project/{project_id}/documents")
# async def get_project_documents(project_id: int):
#     # Retrieve all documents associated with the specified project if the user has access
#     # Return a list of documents for the project
#     pass


@project_router.get(
    "/project/{project_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_project_documents(
    project_id: int,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await document_service.get_project_documents(
            project_id, current_user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # POST /project/<project_id>/documents - Upload document/documents for a specific project
# @app.post("/project/{project_id}/documents")
# async def upload_project_documents(project_id: int):
#     # Upload one or more documents for the specified project if the user has access
#     # Return a success response after uploading the documents
#     pass


@project_router.post(
    "/project/{project_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_documents(
    project_id: int,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(..., description="File to upload")],
):
    try:
        return await document_service.upload_document_for_project(
            project_id=project_id, file=file, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # POST /project/<project_id>/invite?user=<login> - Grant access to the project for a specific user. If the request is not coming from the owner of the project, results in error.
# # Granting access gives participant permissions to receiving user
# @app.post("/project/{project_id}/invite")
# async def invite_user_to_project(project_id: int, user_email: str):
#     # Grant access to the specified user for the project if the request is coming from the owner
#     # If the request is not from the owner, return an error response
#     pass
@project_router.post("/project/{project_id}/invite")
async def invite_user_to_project(
    project_id: int,
    invite_data: ProjectInviteRequest,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await project_service.invite_user_to_project(
            project_id=project_id,
            owner=current_user,
            invited_user=invite_data.user_invited,
            role=invite_data.user_role,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


# # Optional:
# # GET /project/<project_id>/share?with=<email> - send a GET /join link with correct hashed token for the requested project to specified email, that can be opened
# # by a different user in a browser


# @project_router.get("/project/{project_id}/share")
# async def share_project_by_email(
#     self,
#     project_id: int,
#     email: str = Query(..., alias="with", description="Email of the user to invite"),
#     project_service: ProjectService = Depends(get_project_service),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         return await project_service.invite_user_to_project_by_email()

#     except ValueError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

#     except PermissionError as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

#     except Exception as e:
#         logger.error(f"Error uploading document: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred while inviting the user.",
#         )
# changes to test precommit
# changes to test pr to develop
