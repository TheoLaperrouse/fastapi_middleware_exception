from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SizeLimitException(Exception):
    def __init__(self, message: str):
        self.message = message


class SizeLimitMiddleware:
    def __init__(self, app: FastAPI, max_size: int):
        self.app = app
        self.max_size = max_size

    async def __call__(self, request: Request, response: Response):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_size:
            raise SizeLimitException(
                f"La taille de la requête dépasse la limite autorisée : {self.max_size} octets.")
        else:
            return await self.app(request, response)


app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.exception_handler(SizeLimitException)
async def size_limit_exception_handler(request: Request, exc: SizeLimitException):
    return JSONResponse(status_code=418, content={"message": exc.message})

app.add_middleware(SizeLimitMiddleware, max_size=1024)
