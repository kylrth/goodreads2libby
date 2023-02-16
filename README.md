# goodreads2libby

This is a BeautifulSoup script to scrape a GoodReads list and search all your Libby libraries for those books. It uses `requests` and `beautifulsoup4` for GoodReads, but it has to use Selenium for Libby because it needs to run the JavaScript.

Run the following to download your to-read list to a CSV file:

```sh
python get_books.py 'https://www.goodreads.com/review/list/<your-list-id>?shelf=to-read' > want-to-read.csv
```

And then run this command to search Libby for those books:

```sh
cat want-to-read.csv | python search_libby.py <library-ids>
```

You can get the library IDs by visiting <https://libbyapp.com/>, searching for your library, and checking the URL once you've clicked on the library:

```txt
https://libbyapp.com/library/<library-ID>
```

## dependencies

See `requirements.txt`. You'll need to have a browser installed for Selenium to use. The code is written to use the  Firefox driver but it can conceivably use other browsers.
