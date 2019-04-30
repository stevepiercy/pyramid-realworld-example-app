"""HTTP operations on Article resource."""

from conduit.article.models import Article
from conduit.openapi import object_or_404
from mypy_extensions import TypedDict
from pyramid.request import Request
from pyramid.view import view_config
from slugify import slugify
from sqlalchemy import desc

import typing as t

# Python implementation of openapi.yaml's MultipleArticlesResponse schema
MultipleArticlesResponse = TypedDict(
    "MultipleArticlesResponse", {"articles": t.List[Article], "articlesCount": int}
)

# Python implementation of openapi.yaml's SingleArticleResponse schema
SingleArticleResponse = TypedDict("SingleArticleResponse", {"article": Article})


@view_config(route_name="articles", renderer="json", request_method="GET", openapi=True)
def articles(request: Request) -> MultipleArticlesResponse:
    """Get recent articles globally."""
    articles = request.db.query(Article).order_by(desc("created")).all()
    count = request.db.query(Article).count()
    return {"articles": articles, "articlesCount": count}


@view_config(route_name="article", renderer="json", request_method="GET", openapi=True)
def article(request: Request) -> SingleArticleResponse:
    """Get an article."""
    article = object_or_404(
        Article.by_slug(
            request.openapi_validated.parameters["path"]["slug"], db=request.db
        )
    )
    return {"article": article}


@view_config(
    route_name="articles", renderer="json", request_method="POST", openapi=True
)
def create(request: Request) -> SingleArticleResponse:
    """Get an article."""
    body = request.openapi_validated.body
    article = Article(
        slug=slugify(body.article.title),
        title=body.article.title,
        description=body.article.description,
        body=body.article.body,
        author=request.user,
    )
    request.db.add(article)
    request.db.flush()
    request.response.status_code = 201
    return {"article": article}
