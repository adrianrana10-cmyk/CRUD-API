from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import supabase
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/auth", tags=["auth"])
public_router = APIRouter(tags=["public/protected demo"])


class AuthRequest(BaseModel):
    email: str = ""
    password: str = ""


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

@public_router.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@public_router.get("/protected/profile")
def protected_profile_unverified(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer ") or len(auth_header.split(" ", 1)[1].strip()) == 0:
        raise HTTPException(status_code=401, detail="Access token required")

    token = auth_header.split(" ", 1)[1].strip()
    return {"note": "token received but not yet verified", "token_preview": token[:12] + "..."}