from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login_id: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponseData(BaseModel):
    access_token: str
    user_id: str
    name: str
    role: str


class LoginResponse(BaseModel):
    status: str = "success"
    data: LoginResponseData