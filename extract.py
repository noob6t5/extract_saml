import argparse,requests,re


# Change Normal URL


def normalize_url(url):
    if not re.match(r"^https?://", url):
        return "http://" + url  # Assume http if no scheme
    return url


##Inputs
def single_url(url,headers,timeout,retries):
    print("Please Wait .......")


##Usuage
def main():
    parser=argparse.ArgumentParser(description="SAML URL Extractor")
    
    parser.add_argument("-u", "--url", help="Single URL ")
    parser.add_argument("-f", "--file", help=" for urls.txt")
    parser.add_argument("--headers", help="Custom headers in JSON format")
    parser.add_argument("--timeout", type=int, default=10, help="(default: 10)")
    parser.add_argument("--retries", type=int, default=3, help="(default: 3)")

    args=parser.parse_args()

    if not args.url and not args.file:
        parser.print_help()
        exit(1)

    print("Please Wait .....")     


if __name__=="__main__":
    main()
