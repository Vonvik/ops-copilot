from fastapi import APIRouter, Query

router = APIRouter(prefix="", tags=["examples"])


@router.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!"}


@router.get("/search")
def search(q: str = Query(..., min_length=1)):
    return {"q": q, "results": []}
