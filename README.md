# Descriptions

**extract_saml** is a powerful tool designed to extract SAML-based URLs from a list of URLs efficiently. It offers various features that simplify the identification of potential security issues in applications that utilize SAML for authentication.

## Features

- **Efficient SAML URL Extraction**: Quickly identify SAML-based URLs from a list, saving time in the vulnerability assessment process.
- **Customizable Headers**: Use custom HTTP headers for requests to adapt to different environments.
- **Timeout Settings**: Control request timeouts to optimize performance during large-scale scans.
- **Flexible Output Formats**: Export results in JSON or CSV format for easy reporting and analysis.

## Benefits

This tool is particularly beneficial for:

- **Bug Hunters**: **First come first Serve**> it  locates SAML URLs that may be vulnerable or for further testing.
- **Red Teamers**: Identify misconfigurations in SAML implementations to exploit potential security weaknesses.
- **Developers**: Analyze SAML configurations in your applications to ensure best practices and security compliance.

## Installation

```bash
git clone https://github.com/noob6t5/extract_saml.git

cd extract_saml

python3 extract.py -h

usage: extract.py [-h] [-u URL] [-f FILE] [--headers HEADERS]
                  [--timeout TIMEOUT] [--output {json,csv}]

SAML URL Extractor

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Single URL
  -f FILE, --file FILE  File with URLs
  --headers HEADERS     Custom headers in JSON format
  --timeout TIMEOUT     Request timeout (default: 10 seconds)
  --output {json,csv}   Output format (json or csv)
```
# Example
**python3 extract.py -u domain.com**

**python3 extract.py -f /path/to/your/urls.txt**

**python3 extract.py -f /path/to/your/urls.txt --headers '{"User-Agent": "Mozilla/5.0", "Authorization": "Bearer your_token"}' --timeout 15 --output csv**

**ETC**


# Feel free to update the code according to your need.

