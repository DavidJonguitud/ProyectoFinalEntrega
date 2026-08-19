from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin
from app.services.user import UserService

from app.core.dependencies import get_user_service

import logging


logger = logging.getLogger(__name__)

user_router = APIRouter(
        tags=["Authentication"]
)
@user_router.post("/auth", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)

        ):
    try:
        return await user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error {e}")
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(
    user_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.login_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error {e}")
        raise HTTPException(status_code=500, detail=str(e))
 