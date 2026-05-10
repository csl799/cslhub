from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    return JSONResponse(
        content=jsonable_encoder({"code": 200, "message": message, "data": data})
    )
