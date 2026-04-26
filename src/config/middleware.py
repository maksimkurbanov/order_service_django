import ipaddress
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
            # Extract host part (without port) for CIDR matching
            host_only = host_header.split(":")[0]

            allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])

            for entry in allowed_hosts:
                # 1. Exact match or wildcard domain (already handled by Django, but we can shortcut)
                if entry.startswith("."):
                    # Domain wildcard: e.g., '.python-labs.ru'
                    if host_only.endswith(entry) or host_only == entry[1:]:
                        return self.get_response(request)
                else:
                    # Exact host match
                    if host_only == entry:
                        return self.get_response(request)

                # 2. CIDR check (using ipaddress module)
                try:
                    network = ipaddress.ip_network(entry, strict=False)
                    if ipaddress.ip_address(host_only) in network:
                        # Override request.get_host to return the original host_header
                        # This prevents CommonMiddleware from raising DisallowedHost
                        def custom_get_host():
                            return host_header

                        request.get_host = custom_get_host
                        return self.get_response(request)
                except ValueError:
                    # entry is not a valid CIDR – ignore
                    continue

            # If no pattern matched, return a 400 response (mimicking Django's behavior)
            msg = (
                f"Invalid HTTP_HOST header: '{host_header}'. "
                f"You may need to add '{host_only}' to ALLOWED_HOSTS."
            )
            return HttpResponseBadRequest(msg, content_type="text/plain")

        # No HTTP_HOST header – let request pass (Django will handle it)
        return self.get_response(request)
