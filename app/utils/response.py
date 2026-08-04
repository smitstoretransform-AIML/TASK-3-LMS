from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def api_response(
    code: int,
    status: str,
    message: str,
    data=None
):
    return JSONResponse(
        status_code=code,
        content=jsonable_encoder(
            {
                "code": code,
                "status": status,
                "message": message,
                "data": data
            }
        )
    )