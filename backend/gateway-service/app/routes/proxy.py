"""Reverse proxy routes for the API Gateway."""
from typing import Optional
import structlog
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from app.config import settings
from app.main import http_client


logger = structlog.get_logger(__name__)

router = APIRouter()


# Service URL mapping based on path prefixes
SERVICE_ROUTES = {
    "/api/v1/auth": settings.user_service_url,
    "/api/v1/users": settings.user_service_url,
    "/api/v1/movies": settings.catalog_service_url,
    "/api/v1/theaters": settings.catalog_service_url,
    "/api/v1/shows": settings.catalog_service_url,
    "/api/v1/cities": settings.catalog_service_url,
    "/api/v1/bookings": settings.booking_service_url,
    "/api/v1/payments": settings.payment_service_url,
    "/api/v1/notifications": settings.notification_service_url,
}


def get_target_service(path: str) -> Optional[str]:
    """
    Determine the target service URL based on the request path.

    Args:
        path: The request path

    Returns:
        Target service URL or None if no match found
    """
    for prefix, service_url in SERVICE_ROUTES.items():
        if path.startswith(prefix):
            return service_url
    return None


async def proxy_request(
    request: Request,
    target_url: str,
) -> Response:
    """
    Proxy the request to the target backend service.

    Args:
        request: The incoming FastAPI request
        target_url: The target service URL

    Returns:
        Response from the backend service

    Raises:
        HTTPException: If the backend service is unreachable or returns an error
    """
    # Build the full target URL
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    full_url = f"{target_url}{path}"
    if query:
        full_url = f"{full_url}?{query}"

    # Prepare headers
    headers = dict(request.headers)

    # Remove hop-by-hop headers
    hop_by_hop_headers = [
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",  # Will be set by httpx
    ]
    for header in hop_by_hop_headers:
        headers.pop(header, None)

    # Add authentication headers if available (set by auth middleware)
    if hasattr(request.state, "auth_headers"):
        headers.update(request.state.auth_headers)

    # Get request body
    body = await request.body()

    logger.debug(
        "Proxying request",
        method=request.method,
        path=path,
        target_url=full_url,
        has_body=len(body) > 0,
    )

    try:
        # Make the proxied request
        response = await http_client.request(
            method=request.method,
            url=full_url,
            headers=headers,
            content=body,
        )

        # Prepare response headers
        response_headers = dict(response.headers)

        # Remove hop-by-hop headers from response
        for header in hop_by_hop_headers:
            response_headers.pop(header, None)

        logger.debug(
            "Proxy response received",
            status_code=response.status_code,
            content_length=len(response.content),
        )

        # Return the response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type"),
        )

    except httpx.TimeoutException as e:
        logger.error(
            "Backend service timeout",
            target_url=full_url,
            error=str(e),
        )
        raise HTTPException(
            status_code=504,
            detail={
                "error": {
                    "code": "GATEWAY_TIMEOUT",
                    "message": f"Backend service timeout: {target_url}",
                }
            },
        )
    except httpx.ConnectError as e:
        logger.error(
            "Backend service connection error",
            target_url=full_url,
            error=str(e),
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": f"Backend service unavailable: {target_url}",
                }
            },
        )
    except Exception as e:
        logger.error(
            "Proxy request failed",
            target_url=full_url,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=502,
            detail={
                "error": {
                    "code": "BAD_GATEWAY",
                    "message": "Failed to proxy request to backend service",
                }
            },
        )


# Proxy all API routes
@router.api_route(
    "/api/v1/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    tags=["Proxy"],
)
async def proxy_api_v1(request: Request, path: str):
    """
    Proxy all /api/v1/* requests to the appropriate backend service.

    This is the main reverse proxy endpoint that routes requests based on path prefixes.
    """
    full_path = f"/api/v1/{path}"
    target_service = get_target_service(full_path)

    if not target_service:
        logger.warning("No service found for path", path=full_path)
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SERVICE_NOT_FOUND",
                    "message": f"No backend service configured for path: {full_path}",
                }
            },
        )

    return await proxy_request(request, target_service)


# Legacy /api/* routes (without /v1) - for backward compatibility
@router.api_route(
    "/api/users/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def proxy_users_legacy(request: Request, path: str):
    """Proxy legacy /api/users/* requests to user service."""
    return await proxy_request(request, settings.user_service_url)


@router.api_route(
    "/api/catalog/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def proxy_catalog_legacy(request: Request, path: str):
    """Proxy legacy /api/catalog/* requests to catalog service."""
    return await proxy_request(request, settings.catalog_service_url)


@router.api_route(
    "/api/bookings/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def proxy_bookings_legacy(request: Request, path: str):
    """Proxy legacy /api/bookings/* requests to booking service."""
    return await proxy_request(request, settings.booking_service_url)


@router.api_route(
    "/api/payments/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def proxy_payments_legacy(request: Request, path: str):
    """Proxy legacy /api/payments/* requests to payment service."""
    return await proxy_request(request, settings.payment_service_url)
