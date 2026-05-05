from pydantic import BaseModel, Field
from typing import Literal

class LoginRequest(BaseModel):
    login_id: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    name: str
    role: str


class LoginResponse(BaseModel):
    status: str = "success"
    data: LoginResponseData


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class RefreshTokenResponseData(BaseModel):
    access_token: str


class RefreshTokenResponse(BaseModel):
    status: Literal["success"] = "success"
    data: RefreshTokenResponseData