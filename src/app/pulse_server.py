"""Lightweight server for the product-pulse workflow.

The full FAQ app also mounts these routes. Use this module when the
embedding stack is not installed.
"""

from fastapi import FastAPI

from src.app.pulse_routes import router

app = FastAPI(title="Groww Review Pulse", version="0.1.0")
app.include_router(router)
