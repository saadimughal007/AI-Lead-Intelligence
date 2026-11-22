
import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


MAX_CONTENT_SIZE = 1_000_000
MAX_TEXT_LENGTH = 12_000
MAX_REDIRECTS = 5

REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}

HEADERS = {
    "User-Agent": "LeadIntelligenceBot/2.0"
}


def validate_website_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("A valid website URL is required.")

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise ValueError("Invalid website URL.") from error

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS websites are allowed.")

    if not hostname:
        raise ValueError("Invalid website hostname.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    if port is not None:
        allowed_ports = {
            "http": 80,
            "https": 443,
        }

        if port != allowed_ports[parsed.scheme]:
            raise ValueError("Non-standard website ports are not allowed.")

    hostname = hostname.rstrip(".").lower()

    if hostname in {"localhost"} or hostname.endswith(
        (".localhost", ".local", ".internal")
    ):
        raise ValueError("Local and internal hostnames are blocked.")

    try:
        ipaddress.ip_address(hostname)
        addresses = [hostname]

    except ValueError:
        try:
            addresses = list({
                result[4][0]
                for result in socket.getaddrinfo(
                    hostname,
                    None,
                    type=socket.SOCK_STREAM,
                )
            })

        except (socket.gaierror, OSError) as error:
            raise ValueError(
                "Website domain could not be resolved."
            ) from error

    if not addresses:
        raise ValueError("Website has no valid IP address.")

    for address in addresses:
        ip = ipaddress.ip_address(address)

        if not ip.is_global:
            raise ValueError(
                "Private, local, or reserved IP addresses are blocked."
            )

    return url


def extract_website_content(url: str) -> dict:
    safe_url = validate_website_url(url)

    try:
        timeout = httpx.Timeout(
            12.0,
            connect=5.0,
        )

        with httpx.Client(
            timeout=timeout,
            follow_redirects=False,
            headers=HEADERS,
            trust_env=False,
        ) as client:

            visited_urls = set()
            current_url = safe_url
            html = None
            final_url = safe_url
            encoding = "utf-8"

            for redirect_count in range(MAX_REDIRECTS + 1):

                current_url = validate_website_url(current_url)

                if current_url in visited_urls:
                    raise ValueError("Website redirect loop detected.")

                visited_urls.add(current_url)

                with client.stream("GET", current_url) as response:

                    if response.status_code in REDIRECT_STATUS_CODES:

                        if redirect_count >= MAX_REDIRECTS:
                            raise ValueError(
                                "Website exceeded the maximum redirect limit."
                            )

                        redirect_location = response.headers.get("location")

                        if not redirect_location:
                            raise ValueError(
                                "Website returned a redirect without a destination."
                            )

                        next_url = urljoin(
                            current_url,
                            redirect_location,
                        )

                        parsed_current = urlparse(current_url)
                        parsed_next = urlparse(next_url)

                        if (
                            parsed_current.scheme == "https"
                            and parsed_next.scheme == "http"
                        ):
                            raise ValueError(
                                "HTTPS to HTTP redirects are not allowed."
                            )

                        current_url = validate_website_url(next_url)
                        continue

                    response.raise_for_status()

                    content_type = response.headers.get(
                        "content-type", ""
                    ).lower()

                    if "text/html" not in content_type:
                        raise ValueError(
                            "Website did not return an HTML page."
                        )

                    content_length = response.headers.get("content-length")

                    if content_length:
                        try:
                            if int(content_length) > MAX_CONTENT_SIZE:
                                raise ValueError(
                                    "Website content is too large."
                                )
                        except ValueError as error:
                            if "too large" in str(error):
                                raise
                            raise ValueError(
                                "Invalid website content length."
                            ) from error

                    chunks = []
                    total_size = 0

                    for chunk in response.iter_bytes():
                        total_size += len(chunk)

                        if total_size > MAX_CONTENT_SIZE:
                            raise ValueError(
                                "Website content exceeds the size limit."
                            )

                        chunks.append(chunk)

                    html = b"".join(chunks)
                    encoding = response.encoding or "utf-8"
                    final_url = current_url

                    break

            if html is None:
                raise ValueError(
                    "Unable to retrieve website content."
                )

        decoded_html = html.decode(
            encoding,
            errors="replace",
        )

        soup = BeautifulSoup(decoded_html, "html.parser")

        for element in soup([
            "script",
            "style",
            "noscript",
            "svg",
            "nav",
            "footer",
            "header",
            "iframe",
            "form",
        ]):
            element.decompose()

        title = (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else ""
        )

        meta_description = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        description = (
            meta_description.get("content", "").strip()
            if meta_description
            else ""
        )

        main_content = soup.find("main") or soup.body or soup

        page_text = " ".join(main_content.stripped_strings)
        page_text = page_text[:MAX_TEXT_LENGTH]

        return {
            "source_url": final_url,
            "title": title,
            "meta_description": description,
            "page_text": page_text,
            "status": (
                "success" if page_text else "insufficient_content"
            ),
        }

    except httpx.TimeoutException as error:
        raise ValueError("Website request timed out.") from error

    except httpx.HTTPStatusError as error:
        raise ValueError(
            f"Website returned HTTP status {error.response.status_code}."
        ) from error

    except httpx.HTTPError as error:
        raise ValueError(
            f"Website request failed: {type(error).__name__}"
        ) from error
