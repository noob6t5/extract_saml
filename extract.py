import argparse,requests,re,asyncio,json,csv,aiohttp
from bs4 import BeautifulSoup
from queue import Queue

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
def filter_saml(html_content):
    patterns=[r'SAMLRequest',
              r'SAMLResponse',
              r'acsUrl',  
              r'SSO',
              r'/sso/',
              r'saml', ]
    for pattern in patterns:
        if re.search(pattern,html_content,re.IGNORECASE):
            return True
    return False    

async def extract_saml(session,url,headers,timeout):
    html_content=await fetch_url(session,url,headers,timeout)
    if html_content and filter_saml(html_content):
        soup=BeautifulSoup(html_content,'html.parser')
        forms = soup.find_all('form', method='post')
        saml_urls = []

        for form in forms:
            action_url = form.get('action')
            if action_url and 'saml' in action_url.lower():
                saml_urls.append(action_url)

        if saml_urls:
            return saml_urls

    return None
# Little Misconfig finding
async def find_saml_misconfig(session, url, headers, timeout):
    html_content = await fetch_url(session, url, headers, timeout)
    if html_content and filter_saml(html_content):
        if "urn:oasis:names:tc:SAML" in html_content:
            issues = []
            if "ds:SignatureMethod Algorithm=\"http://www.w3.org/2000/09/xmldsig#rsa-sha1\"" in html_content:
                issues.append("Weak Signature Algorithm (SHA-1) detected.")
            if "<saml:Assertion" in html_content and "Signature" not in html_content:
                issues.append("Unsigned SAML Assertion detected.")
            if "EncryptionMethod Algorithm=\"http://www.w3.org/2001/04/xmlenc#aes128-cbc\"" in html_content:
                issues.append("Weak Encryption Algorithm (AES-128) detected.")
            if "Redirect" in html_content and "http://" in html_content:
                issues.append("Insecure redirect URL (HTTP) detected.")
            if "<saml:Issuer>" not in html_content:
                issues.append("Missing required <saml:Issuer> element.")
            if issues:
                return f"Misconfigurations detected on {url}: " + "; ".join(issues)
            else:
                return f"SAML metadata found on {url} but no misconfig found."
    
    return None
# queue Ma
async def url_queue(queue,headers,timeout):
    async with aiohttp.ClientSession() as session:
        result=[]
        while not queue.empty():
            url=queue.get()
            print(f"Please wait........")

            saml_urls=await extract_saml(session,url,headers,timeout)
            if saml_urls:
                result.append((url,"SAML based URLS",saml_urls))
            else:
                print(f"No SAML Based URL detected!!!")    

            saml_misconfig=await find_saml_misconfig(session, url, headers, timeout)
            if saml_misconfig:
                result.append((url, "SAML Misconfig", saml_misconfig))  

        return result        


# File & URL handlings(json,csv)
def from_file(path):
    try:
        with open(path,'r') as f:
            return [queue.strip() for queue in f.readqueues()]
    except FileNotFoundError:
        print(f"No {path} found!!!.........")
        exit(1)   

def to_file(result,output_format):
    if output_format=='json':
        with open('results.json','w') as f:
            json.dumps(result,f,indent=3)
    elif output_format == 'csv':
        with open('results.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Vulnerability", "Details"])
            for result in result:
                writer.writerow(result)                

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
        parser.error("Please run  python3 extract.py -h  for full descriptions")  

    return args    
# Main
async def main():
    args=arg_parser()
    urls=[]
    if args.url:
        urls.append(normalize_url(args.url))
    if args.file:
        urls += [normalize_url(url) for url in from_file(args.file)]

    headers={}
    if args.headers:
        try:
            headers=json.loads(args.headers)
        except json.JSONDecodeError:
            print('Error.Please enter in JSON format. like { "User-Agent": Hackerone } ')
            exit(1)    

    url_queue=Queue()
    for url in urls:
        url_queue.put(url)

    results = await url_queue(url_queue, headers, args.timeout)

    if args.output:
        to_file(results, args.output)
    else:
        for result in results:
            print(f"{result[1]} at {result[0]}: {result[2]}")


if __name__=="__main__":
    asyncio.run(main())
