def ok(data=None, message="success"):
    return {"code": 200, "message": message, "data": data}

def err(code: int, message: str):
    return {"code": code, "message": message}
