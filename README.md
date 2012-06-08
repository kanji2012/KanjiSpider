KanjiSpider
============

A very simple, far from perfect Web crawler. It uses SQLite3 to store the 
crawled data and succesfully handles cycles. It simply ignores pages with
malformed markup.

usage:

    $ git clone https://github.com/kanji2012/KanjiSpider
    $ cd KanjiSpider
    $ python KanjiSpider.py
    Enter a URL: http://www.wikipedia.com
    ...

An SQLite3 DB file called `mydb` will be created in the current directory, 
which may later be queried for fun and profit. The table is called `data` and 
the `urls` column holds(surprisingly) the URLs, and the `score` column is a
measure of how "famous" this particular URL is &mdash; larger the score, the
more famous is the page linked to by the URL.

PS: This is an attempt by a relative newcomer to Python; so proceed with a 
light heart :)
