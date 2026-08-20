import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_user_service
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.user import UserService

logger = logging.getLogger(__name__)

user_router = APIRouter(tags=["Authentication"])


@user_router.post(
    "/auth", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )


@user_router.post(
    "/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def login_user(
    user_data: UserLogin,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await user_service.login_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        logger.exception("Unexpected error occurred while processing user request")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later."
        )
