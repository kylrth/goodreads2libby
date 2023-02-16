import csv
import html
import random
import sys
from typing import Dict, List, Set
import unicodedata

from bs4 import BeautifulSoup, Tag
from selenium.webdriver.firefox.webdriver import WebDriver

from get_books import fields as gr_fields
import sel


def normalize(s: str) -> str:
    """Unescape and normalize the string.

    Two&nbsp;words -> Two words
    """
    s = html.unescape(s)
    s = unicodedata.normalize("NFKC", s)

    return s


def unreverse_author(author: str) -> str:
    """Unreverse the author name.

    Schur, Michael -> Michael Schur
    Plato -> Plato
    King Jr., Martin Luther -> Martin Luther King Jr.
    """
    comma = author.find(", ")
    if comma == -1:
        return author

    return author[comma + 2 :] + " " + author[:comma]


def get_wait_length(driver: WebDriver, entry: Tag) -> str:
    """Clicks the Place Hold button to find out how long the wait is for a book."""
    button = entry.select("div[class=title-tile-actions]")[0].select("div[class=title-tile-row]")[0]

    if button.select("span[role=text]")[0].string == "Borrow":
        return "Available now"

    # click the Place Hold button
    url = "https://libbyapp.com" + button.find("a").attrs["href"]
    text = sel.load_page(driver, url, "strong[class=circ-option-estimate]")
    soup = BeautifulSoup(text, "html.parser")

    element = soup.select("strong[class=circ-option-estimate]")[0]
    element = element.select("span[role=text]")[0]
    element = element.select("span")[0]

    return element.string


def get_audio_length(entry: Tag) -> str:
    """Will return something like "14 hours"."""
    foreign_objects = entry.select("foreignObject")

    if len(foreign_objects) == 0:
        return None

    return foreign_objects[0].find("span").string


def search(driver: WebDriver, author: str, title: str, library: str) -> List[Dict[str, str]]:
    """Searches Libby for a book through a specific library.

    The author string can be in reverse order, like "Pollan, Michael". The search will look like
    this:

        How to Change Your Mind Michael Pollan

    A list of relevant results is returned. Each result is a dict with the following keys:

    - author (str)
    - title (str)
    - wait (str; natural language description)
    - audio_length (None if not audiobook, otherwise str; natural language description)
    """
    author = unreverse_author(author)
    title = title.replace(":", "%3A")
    title = title.split("(")[0].split(")")[0]

    url = f"https://libbyapp.com/search/{library}/search/query-{title} {author}/page-1"

    # We have to use Selenium to run the JavaScript and fill in the data.
    page_source = sel.load_page(driver, url, "div[class='chaining-block show']")
    soup = BeautifulSoup(page_source, "html.parser")

    out = []

    entries = soup.select("div[class=title-tile-shell]")
    for entry in entries:
        title = entry.select("span[class=title-tile-title]")[0].string
        author = entry.select("div[class=title-tile-author]")[0].find("a").string
        audio_len = get_audio_length(entry)

        out.append(
            {
                "author": normalize(author),
                "title": normalize(title),
                "wait": normalize(get_wait_length(driver, entry)),
                "audio_length": None if audio_len is None else normalize(audio_len),
            }
        )

    return out


def collect_seen() -> Set[str]:
    out = set()

    try:
        with open("libby.out") as f:
            for line in f:
                line = line.strip()

                if line == "" or line.startswith("- "):
                    continue

                out.add(line)
    except FileNotFoundError:
        pass

    return out


def is_sooner(a: str, b: str) -> bool:
    """Returns True iff a is sooner than b.

    "Available now" < "Available soon" < "About 2 days" < "About 7 weeks" < ... < "Several months"
    """

    def _int_rep(s: str) -> int:
        s = s.lower()

        if s == "available now":
            return -1
        if s == "available soon":
            return 0
        if s == "several months":
            return 10000000  # basically inf
        if not s.startswith("about "):
            raise ValueError("weird wait time: " + s)
        if s.endswith(" days"):
            return int(s[6:-5])
        if s.endswith(" weeks"):
            return 7 * int(s[6:-6])
        if s.endswith(" months"):
            return 30 * int(s[6:-7])

        raise ValueError("weird wait time: " + s)

    return _int_rep(a) < _int_rep(b)


if __name__ == "__main__":
    libraries = sys.argv[1:]
    if len(libraries) == 0:
        print("no library specified", file=sys.stderr)
        exit(0)

    driver = sel.load_driver()

    seen = collect_seen()
    results_count = len(seen)
    if results_count > 0:
        print(f"skipping {results_count} books we've already searched", file=sys.stderr)

    for i, line in enumerate(csv.reader(sys.stdin)):
        if i <= len(seen):
            # skip header + any books we've already searched
            continue
        if ",".join(line) == ",".join(gr_fields):
            # skip any extra header lines that show up in the middle of the input file
            continue

        author, title, link = line

        results = {}

        for library in libraries:
            for res in search(driver, author, title, library):
                res["library"] = library

                # make a unique ID from author + title + type
                title_id = f"{res['title']} + {res['author']} + {res['audio_length']}"

                if title_id not in results:
                    results[title_id] = res
                    continue

                # keep this one instead only if it's available sooner
                try:
                    if is_sooner(res["wait"], results[title_id]["wait"]):
                        results[title_id] = res
                except ValueError as e:
                    print(f"weird wait time: " + str(e))
                    results[str(random.randint())] = res

        # TODO if there's an exact match (author + title starts with), keep only exact matches.
        # otherwise, keep everything

        if len(results) != 0:
            results_count += 1
        print(f"{author}: {title}")
        for res in results.values():
            book_type = "text"
            if res["audio_length"] is not None:
                book_type = "audio"
            print(
                f"- {book_type}, {res['wait']} at {res['library']} ({res['author']}: {res['title']})"
            )

        if i % 10 == 0:
            print(f"completed {i + 1} books, {results_count} had hits", file=sys.stderr)

    driver.quit()
