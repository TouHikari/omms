from fastapi.responses import JSONResponse

def ok(data=None, message="success"):
    return {"code": 200, "message": message, "data": data}

def err(code: int, message: str, data=None):
    return {"code": code, "message": message, "data": data}
