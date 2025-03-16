from fastapi import APIRouter

from api.v1 import admin_roles, admin_users

router = APIRouter()


router.include_router(admin_users.router, prefix="/users", tags=["admin"])
router.include_router(admin_roles.router, prefix="/roles", tags=["admin"])
