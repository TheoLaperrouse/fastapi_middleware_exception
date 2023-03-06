from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


app = FastAPI()


class BadException(Exception):
    def __init__(self, message: str):
        self.message = message


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


@app.exception_handler(BadException)
async def size_limit_exception_handler(request: Request, exc: BadException):
    return JSONResponse(status_code=404, content={"message": exc.message})


@app.get("/items/{id}")
async def get_item(id: int):
    if id == 1:
        raise BadException(message='Mauvais ID')
    return {'name': "Brosse à dents", 'price': "1.50€"}


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
