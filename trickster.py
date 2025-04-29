
  import requests
import argparse
import time
import random
from urllib.parse import urlparse
from colorama import Fore, Style, init
from difflib import SequenceMatcher
import concurrent.futures
import json
from requests.exceptions import RequestException

init()

BANNER = r"""
{Fore.RED}
 _______ _______  _______  _______  _        _______ _________ _______  _______ 
\__   __/(  ____ )(  ___  )(  ____ \| \    /\(  ____ \\__   __/(  ____ \(  ____ )
   ) (   | (    )|| (   ) || (    \/|  \  / /| (    \/   ) (   | (    \/| (    )|
   | |   | (____)|| (___) || |      |  (_/ / | (_____    | |   | (__    | (____)|
   | |   |     __)|  ___  || |      |   _ (  (_____  )   | |   |  __)   |     __)
   | |   | (\ (   | (   ) || |      |  ( \ \       ) |   | |   | (      | (\ (   
   | |   | ) \ \__| )   ( || (____/\|  /  \ \/\____) |   | |   | (____/\| ) \ \__
   )_(   |/   \__/|/     \|(_______/|_/    \/\_______)   )_(   (_______/|/   \__/
                                                                                                                                
{Style.RESET_ALL}
{Fore.RED}🚀 Web Cache Deception (WCD) Scanner | Trickster v1.2{Style.RESET_ALL}
"""

INTERESTING_HEADERS = [
    'Cache-Control', 'X-Cache', 'Age',
    'X-Cache-Hits', 'Via', 'CDN-Cache',
    'Fastly-Cache', 'Cloudflare-Cache', 'Akamai-Cache'
]

DEFAULT_EXTENSIONS = ['.css', '.js', '.png', '.jpg', '.html', '.php', '.json', '.aspx']

def print_banner():
    print(BANNER)

def construct_test_url(url, ext):
    parsed = urlparse(url)
    path = parsed.path
    test_path = path.rstrip('/') + "/wcd-test" + ext
    return parsed._replace(path=test_path).geturl()

def similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def test_wcd(url, cookies=None, headers=None, extensions=DEFAULT_EXTENSIONS, delay=1, silent=False, verbose=False, proxies=None, verify=True, output=None, json_output=False):
    results = []

    if not silent:
        print(f"\n{Fore.CYAN}[🔍] Testing: {url}{Style.RESET_ALL}")

    try:
        original_resp = requests.get(
            url,
            cookies=cookies,
            headers=headers,
            timeout=5,
            allow_redirects=False,
            proxies=proxies,
            verify=verify
        )
        original_text = original_resp.text
        original_length = len(original_text)

        if verbose:
            print(f"{Fore.GREEN}[Original Request Headers]{Style.RESET_ALL}")
            for k, v in original_resp.headers.items():
                print(f"    {k}: {v}")

        if not silent:
            print(f"{Fore.GREEN}[Original] Status: {original_resp.status_code}, Size: {original_length} bytes{Style.RESET_ALL}")
    except RequestException as e:
        print(f"{Fore.RED}[❌] Failed to fetch original URL: {e}{Style.RESET_ALL}")
        return None

    for ext in extensions:
        test_url = construct_test_url(url, ext)
        time.sleep(delay + random.uniform(0.1, 0.5))

        try:
            resp = requests.get(
                test_url,
                cookies=cookies,
                headers=headers,
                timeout=5,
                allow_redirects=False,
                proxies=proxies,
                verify=verify
            )
            status = resp.status_code
            test_text = resp.text
            test_size = len(test_text)

            if status != 200:
                if not silent:
                    print(f"\n{Fore.BLUE}[→] Testing: {test_url}{Style.RESET_ALL}")
                    print(f"    Status: {status}, Size: {test_size} bytes — Skipping similarity check.")
                continue

            sim = similarity_ratio(original_text.strip(), test_text.strip())

            result = {
                "url": test_url,
                "status": status,
                "size": test_size,
                "similarity": sim,
                "headers": {k: v for k, v in resp.headers.items() if k in INTERESTING_HEADERS}
            }
            results.append(result)

            if not silent:
                print(f"\n{Fore.BLUE}[→] Testing: {test_url}{Style.RESET_ALL}")
                print(f"    Status: {status}, Size: {test_size} bytes, Similarity: {sim:.2f}")

            if sim > 0.95:
                warning = f"{Fore.YELLOW}[⚠️ POTENTIAL WCD] Response is {sim:.2f} similar to original!{Style.RESET_ALL}"
                print(f"    {warning}")
                if output:
                    with open(output, 'a') as f:
                        f.write(f"{test_url} | Similarity: {sim:.2f}\n")

            if verbose:
                for header in INTERESTING_HEADERS:
                    if header in resp.headers:
                        print(f"    {Fore.MAGENTA}{header}: {resp.headers[header]}{Style.RESET_ALL}")
        except RequestException as e:
            if not silent:
                print(f"    {Fore.RED}[❌] Error: {e}{Style.RESET_ALL}")

    return results if json_output else None

def read_urls_from_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Trickster - Web Cache Deception Scanner")
    print_banner()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--urls", nargs="+", help="Target URLs (e.g., -u https://example.com/profile)")
    group.add_argument("-l", "--list", help="File with URLs")

    parser.add_argument("-e", "--extensions", nargs="+", default=DEFAULT_EXTENSIONS, help="Extensions to test")
    parser.add_argument("--proxy", help="HTTP/HTTPS proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL cert verification")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--silent", action="store_true", help="Silent mode (no verbose output)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode (show headers)")
    parser.add_argument("-o", "--output", help="Output file for vulnerable URLs")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--threads", type=int, default=5, help="Number of threads (default: 5)")

    args = parser.parse_args()

    urls = read_urls_from_file(args.list) if args.list else args.urls
    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    verify = not args.insecure

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    if args.json:
        all_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for url in urls:
            futures.append(
                executor.submit(
                    test_wcd,
                    url,
                    headers=headers,
                    extensions=args.extensions,
                    delay=args.delay,
                    silent=args.silent,
                    verbose=args.verbose,
                    proxies=proxies,
                    verify=verify,
                    output=args.output,
                    json_output=args.json
                )
            )

        for future in concurrent.futures.as_completed(futures):
            if args.json:
                result = future.result()
                if result:
                    all_results.extend(result)

    if args.json:
        print(json.dumps(all_results, indent=2))
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(all_results, f, indent=2)

if __name__ == "__main__":
    main()
              i
