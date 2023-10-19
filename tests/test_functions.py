from ReconRaccoon.src.framework.functions import (
    process_single_url, process_file
)

def test_process_single_url():
    url_with_common_ports = process_single_url("http://example.com", True)
    assert "http://example.com:80" in url_with_common_ports
    assert "http://example.com:443" in url_with_common_ports

    url_without_common_ports = process_single_url("https://example.com", False)
    assert "https://example.com" in url_without_common_ports

    url_with_common_ports_no_prefix = process_single_url("example.com", True)

    assert "http://example.com:80" in url_with_common_ports_no_prefix
    assert "http://example.com:443" in url_with_common_ports_no_prefix

    url_without_common_ports_no_prefix = process_single_url("example.com", False)
    assert "http://example.com" in url_without_common_ports_no_prefix
    assert "https://example.com" in url_without_common_ports_no_prefix

def test_process_file():
    test_file = "resources/sample_urllist.txt"
    urls = process_file(test_file, True)

    expected_urls = [
        "http://example1.com:80", "http://example1.com:443",
        "https://example2.com:80", "https://example2.com:443",
        "http://example3.com:80", "http://example3.com:443"
    ]

    assert all(url in urls for url in expected_urls)
