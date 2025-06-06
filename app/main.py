from .config.settings import settings
from .config.logging import setup_logging
from .mcp.server import create_app


app = create_app()


def main() -> None:
    setup_logging(settings.mcp_log_level)
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        log_level=settings.mcp_log_level.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
