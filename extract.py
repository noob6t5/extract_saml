import argparse,re,asyncio,json,aiohttp
from bs4 import BeautifulSoup
from colorama import Fore, Style
import sys


# Normalize URL
def normalize_url(url):
    if not re.match(r"^https?://", url):
        return "http://" + url
    return url


async def fetch_url(session, url, headers, timeout):
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            return await response.text()
    except Exception:
        return None


# Regex and BeautifulSoup for SAML pattern filter
def filter_saml(html_content):
    patterns = [r"SAMLRequest", r"SAMLResponse", r"acsUrl", r"SSO", r"/sso/", r"saml"]
    for pattern in patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            return True
    return False


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

# Main Process 
async def process_url_queue(queue, headers, timeout):
    async with aiohttp.ClientSession() as session:
        while not queue.empty():
            url = await queue.get()  
            print(f"\r{' ' * 80}", end="")  
            print(f"\rChecking SAML in  {url}", end="")  

            saml_urls = await extract_saml(session, url, headers, timeout)
            if saml_urls:
                print(f"\n{Fore.GREEN}Found SAML in URL: {url}!{Style.RESET_ALL}")
            await asyncio.sleep(0.1)  

#MENu help
async def main():
    parser = argparse.ArgumentParser(description="SAML URL Extractor")
    parser.add_argument("-u", "--url", help="Single URL ")
    parser.add_argument("-f", "--file", help="File with URLs")
    parser.add_argument("--headers", help="Custom headers in JSON format")
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout (default: 10 seconds)"
    )
    parser.add_argument(
        "--output", help="Output format (json or csv)", choices=["json", "csv"]
    )

    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(normalize_url(args.url))
    if args.file:
        urls += [normalize_url(url.strip()) for url in open(args.file, "r").readlines()]

    headers = {}
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError:
            print("Error: Please enter headers in JSON format.")
            sys.exit(1)

    url_queue = asyncio.Queue()
    for url in urls:
        await url_queue.put(url)

    await process_url_queue(url_queue, headers, args.timeout)


if __name__ == "__main__":
    asyncio.run(main())
