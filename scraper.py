import re
from collections import Counter

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


unique_urls = set() #Tracks Unique URLS with no duplicates
#word_count = {} #Tracks word counts for each URL # combined with frequencies
# content_fingerprints = set()  # Tracks fingerprints to avoid duplicate content

# Reporting Data
#url_count = 0  # Total count of unique pages
longest_page = {'url': None, 'word_count': 0}  # Track the longest page by word count
word_frequencies = Counter() # To find the 50 most common words
#subdomain_counts = {}  # Count unique pages per subdomain in uci.edu

# Michael Armijo, Anthony
def scraper(url, resp):

    if resp.status != 200 or not resp.raw_response.content:
        print(f"Skipping {url} due to non-200 status or empty content.")
        return []

    ## Fingerprinting when needed
    # # Generate fingerprint of the page's content
    # content_fingerprint = generate_fingerprint(resp.raw_response.content)
    # if content_fingerprint in content_fingerprints:
    #     print(f"Skipping {url} due to duplicate content.")
    #     return []
    # content_fingerprints.add(content_fingerprint)  # Add fingerprint to the set

    # Check the text-to-HTML ratio for content filtering
    text_ratio = get_text_html_ratio(resp.raw_response.content)
    if text_ratio < 0.05:  # Lowering the threshold temporarily for testing
        print(f"Skipping {url} due to low text-to-HTML ratio: {text_ratio}")
        return []

    # Extract and filter links
    links = extract_next_links(url, resp)
    if is_valid(url):
        current_word_count = count_words_and_update_frequencies(resp.raw_response.content)
        update_longest_page(url, current_word_count)
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
## fingerprinting when needed
# def generate_fingerprint(content):
#     """
#     Generate a hash (fingerprint) of the page content.
#     """
#     soup = BeautifulSoup(content, 'html.parser')
#     text = soup.get_text()  # Extract text from HTML
#     return hashlib.md5(text.encode('utf-8')).hexdigest()  # Return an MD5 hash

def count_words_and_update_frequencies(content):
     #Counts words on the page for determining the longest page and simultaneously
    #updates the word frequencies for reporting.
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    words = re.findall(r'\w+', text.lower())
    stop_words = {
         "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
         "aren't", "as", "at",
         "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
         "can't", "cannot", "could",
         "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
         "each", "few", "for",
         "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he",
         "he'd", "he'll", "he's",
         "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
         "i'd", "i'll", "i'm",
         "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
         "more", "most", "mustn't",
         "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
         "ought", "our", "ours",
         "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
         "should", "shouldn't", "so",
         "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
         "then", "there", "there's",
         "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through",
         "to", "too", "under",
         "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
         "weren't", "what", "what's",
         "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
         "why's", "with", "won't",
         "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
         "yourself", "yourselves"
     }  # stop words from the list given on assignment description used a list maker for hardcoding list( idk how else)
    filtered_words = [word for word in words if word not in stop_words]

    # Update the word frequencies counter
    word_frequencies.update(filtered_words)

    # Return the total word count for the page
    return len(filtered_words)

def update_longest_page(url, word_count):
    if word_count > longest_page['word_count']:
        longest_page['url'] = url
        longest_page['word_count'] = word_count

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

        if "www" not in parsed.netloc: # Filters domains for "www"
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
