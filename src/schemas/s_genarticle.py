from typing import Optional
from pydantic import BaseModel

class GenArticle(BaseModel):
    keyword: str
    url_auth : str
    tag_name : Optional[str] = None