from fastapi import APIRouter, HTTPException

from app.models import Item, ItemOut

router = APIRouter(prefix="/items", tags=["items"])

# almacenamiento en memoria para los ejemplos iniciales
DB: dict[int, ItemOut] = {}
SEQ = [1]  # Use a list to hold the sequence number


@router.get("/", response_model=list[ItemOut])
def list_items():
    return list(DB.values())


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: Item):
    obj = ItemOut(id=SEQ[0], **payload.model_dump())
    DB[SEQ[0]] = obj
    SEQ[0] += 1
    return obj


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    return DB[item_id]


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    del DB[item_id]
