from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


class Item(BaseModel):
    name: str
    price: float


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.middleware("http")
async def add_middleware_here(request: Request, call_next):
    content_length = await get_body(request)
    if content_length and len(content_length) > 1024:
        return JSONResponse(status_code=413, content='Le content est trop long')
    else:
        response = await call_next(request)
        return response
