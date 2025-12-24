from urllib.parse import parse_qs

def _parse_params(environ):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    query_string = environ.get("QUERY_STRING", "")
    get_params = parse_qs(query_string, keep_blank_values=True)

    post_params = {}
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH") or 0)
        except (TypeError, ValueError):
            content_length = 0

        body_bytes = environ.get("wsgi.input").read(content_length) if content_length > 0 else b""
        content_type = environ.get("CONTENT_TYPE", "")

        if "application/x-www-form-urlencoded" in content_type:
            post_params = parse_qs(body_bytes.decode("utf-8", errors="replace"), keep_blank_values=True)
        elif content_length > 0:
            post_params = {"_raw": [body_bytes.decode("utf-8", errors="replace")]}

    return method, get_params, post_params


def _echo_body(method, get_params, post_params):
    lines = [f"Method: {method}", "GET params:"]
    if get_params:
        for key in sorted(get_params):
            values = ", ".join(get_params[key])
            lines.append(f"  {key} = {values}")
    else:
        lines.append("  (none)")

    lines.append("POST params:")
    if post_params:
        for key in sorted(post_params):
            val = post_params[key]
            values = ", ".join(val) if isinstance(val, list) else str(val)
            lines.append(f"  {key} = {values}")
    else:
        lines.append("  (none)")

    return "\n".join(lines) + "\n"


BENCH_BODY = (
    "Benchmark payload\n"
    + ("1234567890abcdef\n" * 5)
    + "Payload end.\n"
)


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/bench":
        body = BENCH_BODY
    else:
        method, get_params, post_params = _parse_params(environ)
        body = _echo_body(method, get_params, post_params)

    status = "200 OK"
    headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body.encode("utf-8"))))
    ]
    start_response(status, headers)
    return [body.encode("utf-8")]
