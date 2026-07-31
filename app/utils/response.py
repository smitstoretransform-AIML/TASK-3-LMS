from fastapi.responses import JSONResponse


def api_response(
    code: int,
    status: str,
    message: str,
    data=None
):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "status": status,
            "message": message,
            "data": data
        }
    )