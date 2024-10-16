from aiogram import Router

from .commands import router as commands_router
from .orders import router as orders_router
from .callbacks import router as callbacks_router

__all__ = ["commands_router", "orders_router", "callbacks_router"]
