from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message:str = "success",data = None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # 任何Fastapi pydantic orm对象 都要正常响应
    return JSONResponse(content=jsonable_encoder(content))


