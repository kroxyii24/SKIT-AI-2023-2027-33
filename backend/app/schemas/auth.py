from pydantic import BaseModel, Field, EmailStr


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone_number: str = Field(min_length=10, max_length=15)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    preferred_language: str | None = "en"


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


class ResendOTPRequest(BaseModel):
    email: EmailStr


class UserLogin(BaseModel):
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class OTPResponse(BaseModel):
    message: str