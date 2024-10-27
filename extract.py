import argparse, re, asyncio, json, aiohttp, csv
from bs4 import BeautifulSoup
from colorama import Fore, Style
import sys

# Normalize URL to prioritize HTTPS
def normalize_url(url):
    if not re.match(r"^https?://", url):
        return "https://" + url
    return url

async def fetch_url(session, url, headers, timeout):
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                return await response.text()
    except Exception:
        return None

# SAML detection in HTML content
def filter_saml(html_content):
    patterns = [r"SAMLRequest", r"SAMLResponse", r"acsUrl", r"SSO", r"/sso/", r"saml"]
    form_content_patterns = [r"SAMLRequest", r"SAMLResponse", r"acsUrl"]
    
    found_patterns = [pattern for pattern in patterns if re.search(pattern, html_content, re.IGNORECASE)]
    
    soup = BeautifulSoup(html_content, "html.parser")
    forms = soup.find_all("form", method="post")
    for form in forms:
        form_content = form.decode()
        if any(re.search(pat, form_content, re.IGNORECASE) for pat in form_content_patterns):
            return True
    return False

# Extract SAML form actions
async def extract_saml(session, url, headers, timeout):
    html_content = await fetch_url(session, url, headers, timeout)
    if html_content and filter_saml(html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        forms = soup.find_all("form", method="post")
        saml_urls = []

        for form in forms:
            action_url = form.get("action")
            if action_url and "saml" in action_url.lower():
                saml_urls.append(action_url)

        if saml_urls:
            return saml_urls
    return None

# Process each URL and handle output formatting
async def process_url_queue(queue, headers, timeout, output_format):
    results = []
    total_urls = 0
    saml_count = 0

    async with aiohttp.ClientSession() as session:
        while not queue.empty():
            url = await queue.get()  
            total_urls += 1

            saml_urls = await extract_saml(session, url, headers, timeout)
            if saml_urls:
                saml_count += 1
                print(f"{Fore.GREEN}SAML found in {url}!{Style.RESET_ALL}")
                results.append({"url": url, "saml_urls": saml_urls})

    # Output results in chosen format
    if output_format == "json":
        with open("saml_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\nResults saved to saml_results.json")
    elif output_format == "csv":
        with open("saml_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "SAML URLs"])
            for result in results:
                writer.writerow([result["url"], ", ".join(result["saml_urls"])])
        print("\nResults saved to saml_results.csv")

    # Summary display
    print(f"\nChecked {total_urls} URLs in total.")
    print(f"{Fore.GREEN}{saml_count} URLs had SAML detected.{Style.RESET_ALL}")
    print(f"{Fore.RED}{total_urls - saml_count} URLs had no SAML.{Style.RESET_ALL}")

# Main function to parse arguments and initiate checks
async def main():
    parser = argparse.ArgumentParser(description="SAML URL Extractor")
    parser.add_argument("-u", "--url", help="Single URL ")
    parser.add_argument("-f", "--file", help="File with URLs")
    parser.add_argument("--headers", help="Custom headers in JSON format")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout (default: 10 seconds)")
    parser.add_argument("--output", help="Output format (json or csv)", choices=["json", "csv"])

    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(normalize_url(args.url))
    if args.file:
        urls += [normalize_url(url.strip()) for url in open(args.file, "r").readlines()]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }
    if args.headers:
        try:
            headers.update(json.loads(args.headers))
        except json.JSONDecodeError:
            print("Error: Please enter headers in JSON format.")
            sys.exit(1)

    url_queue = asyncio.Queue()
    for url in urls:
        await url_queue.put(url)

    await process_url_queue(url_queue, headers, args.timeout, args.output)

if __name__ == "__main__":
    asyncio.run(main())
