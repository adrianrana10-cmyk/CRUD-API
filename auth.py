from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import supabase
from fastapi import APIRouter, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])
public_router = APIRouter(tags=["public/protected demo"])
bearer_scheme = HTTPBearer(auto_error=False)

class AuthRequest(BaseModel):
    email: str = ""
    password: str = ""

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials.strip()

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return result.user

@router.post("/signup", status_code=201)
def signup(payload: AuthRequest):
    if not payload.email.strip() or not payload.password.strip():
        raise HTTPException(status_code=400, detail="email and password are required")

    try:
        result = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"user": result.user}


@router.post("/login", status_code=200)
def login(payload: AuthRequest):
    if not payload.email.strip() or not payload.password.strip():
        raise HTTPException(status_code=400, detail="email and password are required")

    try:
        result = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
    }

@router.post("/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return

@public_router.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@public_router.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }

@public_router.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {user.email}"}