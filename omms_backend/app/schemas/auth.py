from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="手机号")
    realName: Optional[str] = Field(default=None, description="真实姓名")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "patient001",
                    "password": "omms123",
                    "email": "patient001@omms",
                    "phone": "13800000001",
                    "realName": "张患者"
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    username: str = Field(description="用户名或邮箱")
    password: str = Field(description="密码")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"username": "admin@omms", "password": "admin123"}
            ]
        }
    }


class UserOut(BaseModel):
    userId: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    realName: Optional[str]
    roleId: Optional[int]


class LoginData(BaseModel):
    accessToken: str
    tokenType: str
    expiresIn: int
    user: UserOut


class RegisterResponse(BaseModel):
    code: int
    message: str
    data: UserOut


class LoginResponse(BaseModel):
    code: int
    message: str
    data: LoginData
