from pydantic import BaseModel

class DjaggerConfig(BaseModel):
    """Djagger configuration schema"""
    global_prefix = ""