from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    # Validate URL format
    if not url or not isinstance(url, str):
        return f"Error: Invalid URL provided: {url}"
    
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return f"Error: Invalid URL format: {url}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""
        return (title + "\n\n" + text)[:2_000]
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        # Check for DNS resolution errors
        if "nodename nor servname provided" in error_msg or "Failed to resolve" in error_msg or "NameResolutionError" in error_msg:
            return f"Error: Could not resolve domain for {url}. The website may be down or the URL may be incorrect."
        return f"Error: Connection failed for {url}: {error_msg}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching {url}: {str(e)}"


def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]
        return [link for link in links if link]
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if "nodename nor servname provided" in error_msg or "Failed to resolve" in error_msg or "NameResolutionError" in error_msg:
            print(f"Warning: Could not resolve domain for {url}. Skipping.")
        else:
            print(f"Warning: Connection failed for {url}: {error_msg}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Warning: Error fetching links from {url}: {str(e)}")
        return []
