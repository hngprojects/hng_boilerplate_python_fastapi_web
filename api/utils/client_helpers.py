# All helper functions relating to user clients


def get_ip_address(request):
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip is None or client_ip == "":
        client_ip = request.client.host
    return client_ip