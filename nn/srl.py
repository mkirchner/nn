from typing import Tuple, List
import os
import plistlib
import datetime

class SafariReadingList:
    def __init__(self, rl: str = None):
        self.rl = rl or os.path.join(os.environ['HOME'], 'Library/Safari/Bookmarks.plist') 
        self.data = list()
        self._load()

    def _find_dicts_with_rlist_keys_in_dict(self, base_dict):
        # https://medium.com/practical-coding/export-safari-reading-list-using-python-dc36992766e4
        ret = []

        for key,val in base_dict.items():
            if key == "Children":
                # Recurse down
                for child_dict in val:
                    ret += self._find_dicts_with_rlist_keys_in_dict(child_dict)
            elif key == "ReadingList":
                ret.append(base_dict)
                break

        return ret

    def _load(self):
        with open(self.rl, 'rb') as f:
            pl = plistlib.load(f)

        rl = self._find_dicts_with_rlist_keys_in_dict(pl)

        for bookmark in rl:
             url = bookmark['URLString']
             try:
                 preview = bookmark['ReadingList']['PreviewText']
             except:
                 preview = ""
             title = bookmark['URIDictionary']['title']
             try:
                 date_added = bookmark['ReadingList']['DateAdded']
             except:
                 date_added = datetime.now()

             self.data.append((date_added, url, title, preview))

    def get(self, since: datetime.datetime = None) -> List[Tuple[datetime.datetime, str, str, str]]:
        if since:
            return [d for d in self.data if d[0] >= since]
        else:
            return self.data

def main():
    srl = SafariReadingList()
    for (ts, url, t, pre) in srl.get():
        print(type(ts))
        print(str(ts))
        print(f"{ts}:\n\t{url}\n\t{t}\n\t{pre}")

if __name__ == "__main__":
    main()
