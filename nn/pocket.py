import sys
import datetime
from typing import List, Tuple
from bs4 import BeautifulSoup, SoupStrainer

class PocketExport:
    def __init__(self, path:str):
        self.data = list()
        self._load(path)

    def _load(self, path:str) -> None:
        only_li_tags = SoupStrainer("li")
        with open(path, "r") as fp:
            soup = BeautifulSoup(fp, "html.parser", parse_only=only_li_tags)

        for s in soup:
            url = s.a["href"]
            title = s.a.text
            # if title == url:
            #    title = None
            date_added = datetime.datetime.fromtimestamp(int(s.a["time_added"]))
            preview = None
            self.data.append((date_added, url, title, preview))

    def get(self, since: datetime.datetime = None) -> List[Tuple[datetime.datetime, str, str, str]]:
        if since:
            return [d for d in self.data if d[0] >= since]
        else:
            return self.data

def main():
    print(sys.argv)
    pe = PocketExport(sys.argv[1])
    for (ts, url, t, pre) in pe.get():
        print(f"{ts}:\n\t{url}\n\t{t}\n\t{pre}")

if __name__ == "__main__":
    main()

