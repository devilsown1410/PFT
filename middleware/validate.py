import jwt
from fastapi import Depends, HTTPException, Request
import sys
import os
import dotenv


dotenv.load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_token(token: str, request: Request):
    try:
        print("Validating token:", token)
        decode_token = jwt.decode(token, os.environ["secret_key"], algorithms=["HS256"])
        print("Decoded token:", decode_token)
        user_id = decode_token['user_id']
        request.state.current_user = user_id 
        print("Current user set in request state:", user_id)
        return decode_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def validate_jwt_middleware(request: Request, call_next):
    if("/auth" in request.url.path):
        print("Skipping JWT validation for auth route:", request.url.path)
        return await call_next(request)
    token = request.headers.get("Authorization").split(" ")[1]
    print("Authorization header:", token)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        validate_token(token, request)
        print("Token is valid, proceeding with request")
        print("Request state after validation:", request.state.current_user)
        response = await call_next(request)
        return response
    except HTTPException as e:
        return e
    except Exception as e:
        print(f"Error in JWT validation middleware: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
