import ipaddress
import logging

from django.conf import settings
from django.http import HttpResponseBadRequest


class CIDRHostValidationMiddleware:
    """
    Middleware that allows CIDR ranges (e.g., 10.0.0.0/8) in ALLOWED_HOSTS.
    Must be placed BEFORE django.middleware.common.CommonMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_header = request.META.get("HTTP_HOST")
        if host_header:
            host_only = host_header.split(":")[0]

            allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])

            for entry in allowed_hosts:
                if entry.startswith("."):
                    if host_only.endswith(entry) or host_only == entry[1:]:
                        return self.get_response(request)
                else:
                    if host_only == entry:
                        return self.get_response(request)

                try:
                    network = ipaddress.ip_network(entry, strict=False)
                    if ipaddress.ip_address(host_only) in network:

                        def custom_get_host():
                            return host_header

                        request.get_host = custom_get_host
                        return self.get_response(request)
                except ValueError:
                    continue

            msg = (
                f"Invalid HTTP_HOST header: '{host_header}'. "
                f"You may need to add '{host_only}' to ALLOWED_HOSTS."
            )
            return HttpResponseBadRequest(msg, content_type="text/plain")

        return self.get_response(request)


logger = logging.getLogger("incoming.requests")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Gather URL & method
        url = request.build_absolute_uri()
        method = request.method

        # Gather headers (exclude sensitive ones if needed)
        headers = dict(request.headers)
        # Optional: mask Authorization or Cookie if you prefer
        if "Authorization" in headers:
            headers["Authorization"] = "***"
        if "Cookie" in headers:
            headers["Cookie"] = "***"

        # Gather body – note: this reads the raw bytes
        raw_body = request.body
        body = raw_body.decode("utf-8", errors="replace") if raw_body else "<empty>"

        logger.info(
            "Incoming request: %s %s\nHeaders: %s\nBody: %s", method, url, headers, body
        )

        response = self.get_response(request)
        return response
