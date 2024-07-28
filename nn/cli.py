import click
import nn.db
import nn.srl

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
@click.option("--db-url", envvar="NN_DB_URL")
def render_site(db_url):
    db =  nn.db.create_linkstore(db_url)
    links = db.get_links(last=30)
    bookmarks = [dict(ts=l[0], url=l[1], title=l[2], preview=l[3]) for l in links]
    template = env.get_template("nn.html")
    html = template.render(bookmarks=bookmarks)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
def import_rl(db_url):
    db =  nn.db.create_linkstore(db_url)
    srl = nn.srl.SafariReadingList()
    rows = [(str(ts), str(ts), url, t, pre) for (ts, url, t, pre) in srl.get()]
    db.add_links(rows)

@cli.command()
@click.option("--db-url", envvar="NN_DB_URL")
@click.option("--limit", "-l", type=int, help="Number of links to list")
def list_recent(db_url, limit):
    db =  nn.db.create_linkstore(db_url)
    links = db.get_links(limit)
    for l in links:
        print(f"{l[0]}\n\t{l[2]}\n\t{l[1]}")


if __name__ == "__main__":
    cli()
