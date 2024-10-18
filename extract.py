import argparse,requests,re,asyncio,json,csv,aiohttp


# Change Normal URL
def normalize_url(url):
    if not re.match(r"^https?://", url):
        return "http://" + url  # Assume http if no scheme
    return url

async def fetch_url(session,url,headers,timeout):
    try:
        async with session.get(url,headers=headers,timeout=timeout) as response:
            return await response.text()
    except Exception as e:
        print("URL Error {url}: {e}")
        return None    

# regex and beautifulsoup for SAML pattern filter



##Usuage
def arg_parser():
    parser=argparse.ArgumentParser(description="SAML URL Extractor")
    
    parser.add_argument("-u", "--url", help="Single URL ")
    parser.add_argument("-f", "--file", help=" for urls.txt")
    parser.add_argument("--headers", help="Custom headers in JSON format")
    parser.add_argument("--timeout", type=int, default=10, help="(default: 10)")
    parser.add_argument("--retries", type=int, default=3, help="(default: 3)")

    args=parser.parse_args()

    if not args.url and not args.file:
        parser.error("Please run  python3 extract.py -h ")  

    return args    


if __name__=="__main__":
     
