from fastapi import APIRouter, Depends, Body
from src.schemas.s_genarticle import GenArticle
from src.controllers.c_genarticle import generate_and_post_article
from src.controllers.c_auth import check_authentication
from typing import Optional, List

router = APIRouter()

router = APIRouter(
	prefix="/generate_article",
	tags=["Generate Article"],
	dependencies=[Depends(check_authentication)],
	responses={404: {"description": "Not found"}},
)

@router.post('')
def generate_for_article(
        keyword: str,
        url_wp : str,
        tags_name : Optional[str] = None,
        category : Optional[str] = None
    ):
    keyword = keyword
    url_wp = url_wp

    tags_name = tags_name.split(',') if tags_name else list()
    result = generate_and_post_article(
        keyword, tags_name,category, url_wp
    )
    return {'result': result}


