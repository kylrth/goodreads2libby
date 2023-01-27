import csv
import sys

from bs4 import BeautifulSoup
import requests


def yield_results(url: str):
    page = 1
    count = 0

    while True:
        req = requests.get(url, params={"page": page})
        soup = BeautifulSoup(req.text, "html.parser")

        rows = soup.select("td[class='field title']")
        if len(rows) == 0:
            # When we go past the last page, GoodReads returns an empty page.
            break

        for row in rows:
            item = row.select("a")[0]

            yield {
                "title": item.attrs["title"],
                "link": item.attrs["href"],
            }
            count += 1

        print(f"finished page {page} with {count} books so far", file=sys.stderr)
        page += 1


if __name__ == "__main__":
    url = sys.argv[1]

    writer = csv.writer(sys.stdout)

    # header
    writer.writerow(["title", "link"])

    for result in yield_results(url):
        writer.writerow([result["title"], result["link"]])
