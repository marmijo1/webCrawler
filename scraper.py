import re 
import os # Imported to write report in txt file
import PartA # Used as a tokenizer
from collections import Counter # Used to find top 50 common words

from bs4 import BeautifulSoup # Used to pull data out of HTML Files. 
from urllib.parse import urlparse, urljoin, urlunparse



unique_urls = set() #Tracks Unique URLS with no duplicates

# Data used for Report
longest_page = {'url': None, 'word_count': 0}  # Track the longest page by word count
word_frequencies = Counter() # To find the 50 most common words
subdomain_counts = {}  # Count unique pages per subdomain in uci.edu

# Michael Armijo, Anthony Gutierrez

def scraper(url, resp):
    if resp.status != 200 or not resp.raw_response.content: #If resp is not 200 (OK) or not raw content 
        print(f"Skipping {url} due to non-200 status or empty content.")
        return [] #Skip and return empty list 

    text_ratio = get_text_html_ratio(resp.raw_response.content) # Check the text-to-HTML ratio for content filtering

    if text_ratio < 0.05:  # Lowering the threshold temporarily for testing (discussed through peers and testing)
        print(f"Skipping {url} due to low text-to-HTML ratio: {text_ratio}")
        return [] #Returns an empty list if content ratio is too low 

    links = extract_next_links(url, resp)# Extract and filter links using extract_next_links(). 
    if is_valid(url): #Calls is_valid to make sure url is valid for report tracking

        #Report tracking: words, longest page, unique URLS
        current_word_count = count_words_and_update_frequencies(resp.raw_response.content)
        update_longest_page(url, current_word_count)
        track_unique_urls(url) # add this function to include the subdomain counter function

    valid_links = [] # Gather valid links
    for link in links:
        if is_valid(link): # Calls is_valid for link to append to valid_links
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


    links = [] # Gather links 
    if resp.raw_response and resp.raw_response.content: 
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        for link in soup.find_all('a', href=True): # Finding all links in page 
            full_url = urljoin(url, link['href'])  # Use urljoin to handle relative URLs
            links.append(full_url) # Store links
            print("Discovered URL:", full_url)
    return links # Returns the links found

def count_words_and_update_frequencies(content):
    #Counts words on the page for determining the longest page and simultaneously
    #updates the word frequencies for reporting.
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    tokens = PartA.tokenize(text) # Uses tokenizer from A1 to look for words.

    #List of stop words (could have been global, but kept it to avoid scrolling)
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
     }  


    filtered_words = [word for word in tokens if word not in stop_words] # Makes list of words that are not stop words

    word_frequencies.update(filtered_words) # Update the word frequencies counter

    return len(filtered_words) # Return the total word count for the page

def track_unique_urls(url):
    #Looks for unique urls based on the assignment definition of unique

    parsed_url = urlparse(url) # Parse the URL to remove the fragment
    url_without_fragment = urlunparse(parsed_url._replace(fragment="")) #removes fragments

    if url_without_fragment not in unique_urls: # Check if the URL without fragment is already tracked
        unique_urls.add(url_without_fragment)
        track_subdomain(parsed_url.netloc)
        return True  # Indicates that this was a new unique URL
    else:
        return False  # Indicates it was already in the set


def track_subdomain(domain):
    # Checks if subdomain is tracked or not 

    if domain.endswith(".uci.edu"): # Checks if it's in UCI domain and tracks new and old suddomains
        if domain in subdomain_counts:
            subdomain_counts[domain] += 1
        else:
            subdomain_counts[domain] = 1

def update_longest_page(url, word_count):
    #Updates Longest Page for records 

    if word_count > longest_page['word_count']: # Tracks the page with the longest word count 
        longest_page['url'] = url
        longest_page['word_count'] = word_count

def get_text_html_ratio(content):
    # Gets text to HTML ration of a page 

    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    return len(text) / len(content) if len(content) > 0 else 0 #Returns ratio if above 0. 

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]): #filters schemes to match http/https 
            print(f"Excluded {url} due to invalid scheme.")
            return False

        if "www" not in parsed.netloc: # Filters domains for "www"
            print(f"Excluded {url} because it does not conatain 'www'.")
            return False
        
        # Restrict to specified domains and paths
        valid_domains = (".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "today.uci.edu")
        
        
        if not any(parsed.netloc.endswith(domain) for domain in valid_domains): # Checks to see if url is in a valid domain
            
            if not(parsed.netloc == "today.uci.edu" and parsed.path.startswith("/department/information_computer_sciences")): #Checks if it's part of today.uci.edu/department/information_computer_sciences
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
        
        #Trap catcher for urls
        trap_patterns = [r'/sort=', r'/search']
        for pattern in trap_patterns: # Excludes URLs that may be traps 
            if re.search(pattern, parsed.path):
                print(f"Excluded {url} due to trap pattern: {pattern}")
                return False

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise

def write_report():
    #Writes report for crawler
    
    report_filename = "crawl_report.txt"
    with open(report_filename, "w") as report_file:
        # Unique pages found
        report_file.write(f"Total unique pages: {len(unique_urls)}\n\n")

        # Longest page information
        report_file.write("Longest page:\n")
        report_file.write(f"URL: {longest_page['url']}\n")
        report_file.write(f"Word Count: {longest_page['word_count']}\n\n")

        # Most common words
        report_file.write("50 Most Common Words:\n")
        for word, frequency in word_frequencies.most_common(50):
            report_file.write(f"{word}: {frequency}\n")
        report_file.write("\n")

        # Subdomain information
        report_file.write("Subdomains in uci.edu:\n")
        for subdomain_info in sorted(subdomain_counts.items()):
            report_file.write(f"{subdomain_info[0]}, {subdomain_info[1]}\n")