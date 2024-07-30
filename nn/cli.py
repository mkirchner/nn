import click
import nn.db
import nn.srl
import nn.pocket
import nn.crawl
import os.path
from tabulate import tabulate
# this will need to go into a separate file
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape()
)

@click.group()
def cli():
    pass

@cli.command()
#@click.option("--db-url", envvar="NN_DB_URL")
@click.argument("url")
def crawl(url):
    """Crawl an URL"""
    u, title, preview, text = nn.crawl.crawl([url])[0]
    print(f"{url}\n\t{title}")

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
@click.option("--status", default=False, is_flag=True)
def autocomplete(db_url, status):
    """Autocomplete bookmarks"""
    db =  nn.db.create_linkstore(db_url)
    urls = [l[1] for l in db.get_links_with_incomplete_title()]
    print(f"Found {len(urls)} incomplete bookmarks")
    if not status:
        with click.progressbar(urls) as bar:
            for url in bar:
                # print(f"\n\t{url}")
                completed = nn.crawl.crawl([url])
                if not completed:
                    continue
                new_title = completed[0][1]
                if new_title is None:
                    continue
                db.update_title(url, new_title)

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
@click.option("--target", "-t", required=True, help="Target directory")
def render_site(db_url, target):
    """Render the site"""
    archive_years = list(range(2016, 2025))
    archive_years.reverse()

    db =  nn.db.create_linkstore(db_url)
    links = db.get_links(last=50)
    bookmarks = [dict(ts=l[0], url=l[1], title=l[2], preview=l[3]) for l in links]
    template = env.get_template("nn.html")
    html = template.render(years=archive_years, bookmarks=bookmarks)
    with open(os.path.join(target, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    for year in archive_years:
        links = db.get_links(for_year=year)
        bookmarks = [dict(ts=l[0], url=l[1], title=l[2], preview=l[3]) for l in links]
        #bookmarks.reverse()  # prefer asc time order
        bookmarks.reverse()  # or don't
        template = env.get_template("archive.html")
        html = template.render(years=archive_years, year=year, bookmarks=bookmarks)
        with open(os.path.join(target, f"{year}.html"), "w", encoding="utf-8") as f:
            f.write(html)

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
def import_readinglist(db_url):
    """Import Safari reading list"""
    db =  nn.db.create_linkstore(db_url)
    srl = nn.srl.SafariReadingList()
    rows = [(str(ts), str(ts), url, t, pre) for (ts, url, t, pre) in srl.get()]
    db.add_links(rows)

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
@click.option("--source", "-s", required=True, help="Path to source file")
def import_pocket(db_url, source):
    """Import GetPocket export"""
    db =  nn.db.create_linkstore(db_url)
    pe = nn.pocket.PocketExport(source)
    rows = [(str(ts), str(ts), url, t, pre) for (ts, url, t, pre) in pe.get()]
    db.add_links(rows)

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
@click.option("--limit", "-l", type=int, help="Number of links to list")
def list_recent(db_url, limit):
    """List recent entries"""
    db =  nn.db.create_linkstore(db_url)
    links = db.get_links(limit)
    for l in links:
        print(f"{l[0]}\n\t{l[2]}\n\t{l[1]}")


if __name__ == "__main__":
    cli()
