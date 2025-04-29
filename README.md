# 🔥 Trickster - Web Cache Deception Scanner
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)


Trickster is a fast and extensible tool written in Python to detect **Web Cache Deception (WCD)** vulnerabilities. It simulates different file extensions and observes caching behavior to find misconfigured caching systems.

## 🚀 Features

- Fast multi-threaded scanning
- Supports custom file extensions
- Detects similarity with original content
- Useful header inspection (Cache-Control, X-Cache, etc.)
- JSON output support
- Proxy and SSL options

## 🛠️ Usage

```bash
python3 trickster.py -u https://example.com/profile

Options

Option  	      Description
-u	           Single URL or multiple URLs
-l	           Load URLs from file
-e	           Custom extensions (default: .css, .js, ...)
--proxy	           Use proxy (e.g., http://127.0.0.1:8080)
--insecure         Disable SSL verification
--delay	           Delay between requests (default: 1 sec)
-v / --verbose	   Show response headers
--json	           Output results in JSON
--threads	   Number of concurrent threads
-o	           Output file for vulnerable results
