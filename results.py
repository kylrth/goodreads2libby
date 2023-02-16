import sys
from typing import Dict


def update(totals: Dict[str, int], has_text: bool, has_audio: bool):
    if has_text and has_audio:
        totals["has_both"] += 1
    elif has_text:
        totals["has_text"] += 1
    elif has_audio:
        totals["has_audio"] += 1
    else:
        totals["has_none"] += 1


if __name__ == "__main__":
    totals = {
        "has_both": 0,
        "has_text": 0,
        "has_audio": 0,
        "has_none": 0,
    }

    has_text = False
    has_audio = False

    for line in sys.stdin:
        line = line.strip()

        if line == "":
            continue

        if line.startswith("- text"):
            has_text = True
            continue
        if line.startswith("- audio"):
            has_audio = True
            continue

        # new book
        update(totals, has_text, has_audio)
        has_text = False
        has_audio = False

    # last book
    update(totals, has_text, has_audio)

    print(f"Of {sum(totals.values())} books:")
    print(f" - {totals['has_text']} are available as ebooks,")
    print(f" - {totals['has_audio']} are available as audiobooks,")
    print(f" - {totals['has_both']} are available as both,")
    print(f" - {totals['has_none']} are unavailable.")
