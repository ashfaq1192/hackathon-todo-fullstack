import jwt
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate JWT from Authorization header and
    attach user_id to request.state.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        public_paths = ["/health", "/docs", "/openapi.json"] # Paths that don't require auth

        # Check if the path is public
        if request.url.path in public_paths or request.url.path.startswith("/api/mcp"):
            response = await call_next(request)
            return response

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("user_id")

            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: user_id missing")

            request.state.user_id = user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        response = await call_next(request)
        return response

auth_middleware = AuthMiddleware # Export the middleware for use in main.py
