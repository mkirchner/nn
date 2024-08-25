import requests
from bs4 import BeautifulSoup
import pprint as pp
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from tqdm import tqdm
from functools import lru_cache
import os


class Event(BaseModel):
    key: str | None  # external unique identifier (think FK)
    title: str
    description: str | None
    start: datetime
    end: datetime
    venue: None | str
    address: None | str
    ref: str | None


class AuthError(RuntimeError):
    pass


class Eventbrite:
    def __init__(self, auth_token=None):
        if not auth_token:
            auth_token = os.environ.get("EVENTBRITE_AUTH_TOKEN", None)
            if not auth_token:
                raise AuthError(
                    "No eventbrite auth token and EVENTBRITE_AUTH_TOKEN not set"
                )
        self.s = requests.session()
        headers = {"Authorization": f"Bearer {auth_token}"}
        self.s.headers = headers

    @lru_cache
    def _get_venue(self, venue_id):
        url = f"https://www.eventbriteapi.com/v3/venues/{venue_id}/"
        response = self.s.get(url)
        data = response.json()
        venue = data.get("name")
        address = data.get("address")
        if address:
            address = address.get("localized_address_display")
        return venue, address

    def get_event(self, event_id):
        # event
        url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
        response = self.s.get(url)
        data = response.json()
        ref = data.get("url")
        key = str(data.get("id"))
        title = data.get("name").get("text")
        description = data.get("description").get("text")
        timeformat = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.strptime(data.get("start").get("utc"), timeformat)
        end = datetime.strptime(data.get("end").get("utc"), timeformat)
        # venue
        venue_id = data.get("venue_id")
        if venue_id:
            venue, address = self._get_venue(venue_id)
        else:
            venue, address = None, None

        event = Event(
            key=key,
            title=title,
            description=description,
            start=start,
            end=end,
            venue=venue,
            address=address,
            ref=ref,
        )
        return event


def scrape_campusfounders():
    eventbrite = Eventbrite()
    URL = "https://campusfounders.de/community/events/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    event_containers = soup.find_all("div", class_="event-container")
    events = []
    for e in tqdm(event_containers):
        title = e.find("a", class_="eventtitle")
        # print(f'--- [{title.text.strip()}]')
        href = title["href"]
        if "eventbrite.com" in href:
            event_id = int(href.split("-")[-1])
            event = eventbrite.get_event(event_id)
            events.append(event)
        else:
            # this probably should not happen
            monthday = e.find("div", class_="monthday-column")
            eventtime = e.find("span", class_="eventtime")
            print("Umanaged event for Campusfounders:")
            print(f"    {title.text.strip()}")
            print(f"    {monthday.text.strip()} | {eventtime.text.strip()}")

    return events


def main():
    eventbrite_auth_token = "JG3HHWT37QO6CJDKFLQ2"
    eb_client = Eventbrite(eventbrite_auth_token)

    events = scrape_campusfounders(eb_client)
    # next: scrape more

    for e in events:
        start = e.start.strftime("%m/%d %H:%M (%Z)")
        print(f"{start}: {e.title}")
    # next: store events in sqlite (remove duplicates and add review status)


if __name__ == "__main__":
    main()
