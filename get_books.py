import csv
import sys

from bs4 import BeautifulSoup
import requests


def get_books(url: str):
    page = 1
    count = 0

    while True:
        req = requests.get(url, params={"page": page})
        soup = BeautifulSoup(req.text, "html.parser")

        rows = soup.select("tr[class='bookalike review']")
        if len(rows) == 0:
            # When we go past the last page, GoodReads returns an empty page.
            break

        for row in rows:
            title = row.select("td[class='field title']")[0].select("a")[0]
            author = row.select("td[class='field author']")[0].select("a")[0]

            yield {
                "author": author.string,
                "title": title.attrs["title"],
                "link": title.attrs["href"],
            }
            count += 1

        print(f"finished page {page} with {count} books so far", file=sys.stderr)
        page += 1


fields = ["author", "title", "link"]


if __name__ == "__main__":
    url = sys.argv[1]

    writer = csv.writer(sys.stdout)

    # header
    writer.writerow(fields)

    for result in get_books(url):
        writer.writerow([result[key] for key in fields])
