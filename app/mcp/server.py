"""MCP server implementing JSON-RPC 2.0."""

from typing import Any, Callable, Dict

from fastapi import Depends, FastAPI, HTTPException, Request

from ..config.settings import settings
from ..config.logging import get_logger
from ..services.payment_service import PaymentService
from ..services.wallet_service import WalletService
from ..services.auth_service import AuthService
from ..services.audit_service import AuditService
from ..repositories.payment_repository import PaymentRepository
from ..repositories.wallet_repository import WalletRepository
from ..repositories.user_repository import UserRepository
from ..repositories.audit_repository import AuditRepository
from ..integrations.stripe_client import StripeClient
from ..integrations.razorpay_client import RazorpayClient
from ..utils.auth import JWTBearer
from ..utils.rate_limit import rate_limit_dependency
from .tools import TOOL_REGISTRY


logger = get_logger(__name__)


class ToolContext:
    """Context passed to tools."""

    def __init__(self) -> None:
        # In a real implementation these would be singleton instances
        session = None  # Placeholder for DB session
        self.payment_service = PaymentService(
            PaymentRepository(session),
            StripeClient(),
            RazorpayClient(),
        )
        self.wallet_service = WalletService(WalletRepository(session))
        self.auth_service = AuthService(UserRepository(session))
        self.audit_service = AuditService(AuditRepository(session))


def create_app() -> FastAPI:
    """Application factory."""

    app = FastAPI(title="MCP Payments Server", version="1.0.0")

    bearer = JWTBearer()

    @app.get("/health")
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    async def dispatch_rpc(request: Request, payload: Dict[str, Any]) -> Any:
        if payload.get("jsonrpc") != "2.0":
            raise HTTPException(status_code=400, detail="invalid jsonrpc version")
        method = payload.get("method")
        params = payload.get("params", {})
        if method != "tools/call":
            raise HTTPException(status_code=404, detail="method not found")
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        func: Callable[[ToolContext, Any], Any] | None = TOOL_REGISTRY.get(tool_name)
        if not func:
            raise HTTPException(status_code=404, detail="tool not found")
        ctx = ToolContext()
        model = func.__annotations__.get("params")
        parsed = model(**tool_args) if model else tool_args
        result = await func(ctx, parsed)
        return {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}

    @app.post("/rpc", dependencies=[Depends(rate_limit_dependency), Depends(bearer)])
    async def rpc_endpoint(payload: Dict[str, Any], request: Request) -> Any:
        return await dispatch_rpc(request, payload)

    return app


app = create_app()
