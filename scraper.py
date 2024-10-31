import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


unique_urls = set() #Tracks Unique URLS with no duplicates
word_count = {} #Tracks word counts for each URL

# Michael Armijo, Anthony
def scraper(url, resp):

    if resp.status != 200 or not resp.raw_response.content:
        print(f"Skipping {url} due to non-200 status or empty content.")
        return []

    # Check the text-to-HTML ratio for content filtering
    text_ratio = get_text_html_ratio(resp.raw_response.content)
    if text_ratio < 0.05:  # Lowering the threshold temporarily for testing
        print(f"Skipping {url} due to low text-to-HTML ratio: {text_ratio}")
        return []

    # Extract and filter links
    links = extract_next_links(url, resp)
    if is_valid(url):
        current_word_count = count_words(resp.raw_response.content)
        word_count[url] = current_word_count  # Track word count for reporting
        unique_urls.add(url)

    # Gather valid links
    valid_links = []
    for link in links:
        if is_valid(link):
            valid_links.append(link)
        else:
            print(f"Invalid link filtered out: {link}")

    print(f"Valid links to return for {url}: {valid_links}")  # Log valid links
    return valid_links


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


    links = []
    if resp.raw_response and resp.raw_response.content:
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])  # Use urljoin to handle relative URLs
            links.append(full_url)
            print("Discovered URL:", full_url)
    return links

def count_words(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()  # Extracts text from HTML, ignoring markup
    words = re.findall(r'\w+', text)  # Finds all word-like strings
    return len(words)

def get_text_html_ratio(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    return len(text) / len(content) if len(content) > 0 else 0

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            print(f"Excluded {url} due to invalid scheme.")
            return False

        if "www" not in parsed.netloc:
            print(f"Excluded {url} because it does not conatain 'www'.")
            return False
        
        # Restrict to specified domains and paths
        valid_domains = (".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "today.uci.edu")
        
        if not any(parsed.netloc.endswith(domain) for domain in valid_domains):
            print(f"Excluded {url} due to invalid domain.")
            return False

        # Exclude unwanted file types
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            r"|png|tiff?|mid|mp2|mp3|mp4"
            r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            r"|epub|dll|cnf|tgz|sha1"
            r"|thmx|mso|arff|rtf|jar|csv"
            r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            print(f"Excluded {url} due to file type")
            return False
        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise
