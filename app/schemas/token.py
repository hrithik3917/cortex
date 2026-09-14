from pydantic import BaseModel, field_validator


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    @field_validator("access_token", mode="before")
    @classmethod
    def coerce_bytes_to_str(cls, v):
        # Layer 2: catch bytes at schema validation level
        if isinstance(v, bytes):
            return v.decode("utf-8")
        return v
