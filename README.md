# goodreads2libby

This is a BeautifulSoup script to scrape a GoodReads list and search all your Libby libraries for those books.

Run the following to download your to-read list to a CSV file:

```sh
python get_books.py 'https://www.goodreads.com/review/list/<your-list-id>?shelf=to-read' > want-to-read.csv
```

## dependencies

See `requirements.txt`.
