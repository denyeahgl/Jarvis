# tools/web/safeguard.py
"""
联网工具专属安全层

普通 Tool 不需要，但 fetch 类工具必须防止模型
被诱导访问内网地址（169.254.169.254 云元数据接口尤其危险）。
"""
import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_NETS = [
    ipaddress.ip_network(n)
    for n in (
        "127.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "::1/128",
        "fc00::/7",
    )
]

_ALLOWED_SCHEMES = {"http", "https"}


def assert_safe_url(url: str) -> None:

    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"不支持的协议: {parsed.scheme}")

    host = parsed.hostname

    if not host:
        raise ValueError(f"无效 URL: {url}")

    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        raise ValueError(f"域名解析失败: {host}")

    addr = ipaddress.ip_address(ip)

    if any(addr in net for net in _BLOCKED_NETS):
        raise ValueError(f"禁止访问内网/保留地址: {url}")