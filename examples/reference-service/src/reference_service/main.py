"""Composition root: the only module that wires settings, adapters and routers (STR-012, ARC-008).

Nothing may import this module (contract `main-is-root`).
"""

import uvicorn
from fastapi import FastAPI

from reference_service.api.errors import install_error_handlers
from reference_service.api.middleware import RequestIdMiddleware
from reference_service.api.routers import health, premium_estimates
from reference_service.config import Settings, get_settings
from reference_service.observability import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application. Pass settings in tests; defaults come from the environment."""
    settings = settings if settings is not None else get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.service_name, version="0.1.0")
    app.add_middleware(RequestIdMiddleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(premium_estimates.router)
    return app


def main() -> None:
    """Run the service (make run)."""
    settings = get_settings()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
