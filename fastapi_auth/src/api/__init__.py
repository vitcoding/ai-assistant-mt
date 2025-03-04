from fastapi import APIRouter

from api.v1 import admin, auth, user, oauth

router = APIRouter()

router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
router.include_router(user.router, prefix="/v1/user", tags=["user"])
router.include_router(admin.router, prefix="/v1/admin", tags=["admin"])

router.include_router(oauth.router, prefix="/v1/oauth", tags=["oauth"])
