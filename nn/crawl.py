import requests
from typing import Tuple, List
from bs4 import BeautifulSoup

class CrawlError(RuntimeError):
    pass

def crawl(urls: List[str]) -> List[Tuple[str, str, str, str]]:
    """Crawl urls.

    Returns a list of tuples (url, title, summary, text).
    """
    bookmarks = list()
    for url in urls:
        if not (url.endswith(".html") or url.endswith(".htm") or url.endswith("/")):
            continue
        try:
            r = requests.get(url)
        except:
            continue

        if r.status_code != 200:
            # skip failures
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.text if soup.title else None
        # text = soup.get_text()
        # TODO: add ollama integration here for summarization
        bookmarks.append((url, title, None, None))

    return bookmarks

