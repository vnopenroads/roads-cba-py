from pydantic import BaseModel


class ConfigModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
