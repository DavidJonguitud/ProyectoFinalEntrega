from pydantic import BaseModel, EmailStr, model_validator, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self

class UserResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: str
    exp: int