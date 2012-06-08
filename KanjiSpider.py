import urllib
import sqlite3
from collections import deque
import sgmllib
import sys
import os

# This is a queue to store the urls as BFS algorithm is used here.
q = deque([])         

class URLLister(sgmllib.SGMLParser):
    '''
    URLLister extends SGMLParser class which is inside the sgmllib module.The 
reset method of the URLLister class gets called by the __init__ method of the
SGMLParser class.Whenever SGMLParser finds a '<a' tag the start_a() method
gets called.attrs is a list of tuples containing attribute-value pair.Here a
queue is maintained through out the whole program to store all the child link
of their immediate root link.Every root link is a child link of its immediate
root link and so on.
    '''
    def reset(self):
        sgmllib.SGMLParser.reset(self)
        
    def store(self,u):
    	 # This is a string object to store the immediate parent url.
        self.url = u           
        
    def start_a(self,attrs):        
        self.href = [v for k, v in attrs if k == "href"]
        if self.href:
            print self.href
                
            self.h = self.href[0]
            if self.h.lstrip().startswith("http"):
                q.append(self.h)
            else:
                q.append(self.url + self.h)    


def call(u=None):
    '''
    This method is called by the crawl() method to parse the given url. It
passes the url to the URLLister class to visit the page and append all the
links found on that page to the queue.Sometimes the parser gets confused
due to some bad coding found in the given url while parsing and gives error.
That is why I put this code into a try-except block to avoid this kind of
confusion.

    '''
    try:
        if u!=None:
            parser = URLLister()
            parser.store(u)
            usock = urllib.urlopen(u)
            parser.feed(usock.read())
            usock.close()
            parser.close()        
    except sgmllib.SGMLParseError, exp:
        print(exp)

        
def crawl():
    '''
    crawl() is the first method gets called when the module is run.The
first url given by the user will get stored into the database by
calling the insert_val() method and depending on the returned value
call() method gets called.After that the first element of the queue
is popped out and again insert_val() method gets called with that
element i.e. the url.

    '''
    if os.path.exists("./mydb"):
        connection, cursor=openDB()
        resetDB(connection,cursor)
    else:
        connection, cursor=openDB()
        createDB(connection,cursor)
    u = raw_input("Enter a URL: ")
    x, u = insert_val(u,connection,cursor)
    while True:
        if x:
            call(u)
            if q:
                item = q.popleft()
                x, u = insert_val(item,connection,cursor)
                continue
            break
        else:
            call(u)
            if q:
                item = q.popleft()
                x, u = insert_val(item,connection,cursor)
                continue
            break
    connection.close()


def createDB(connection,cursor):
    '''
    Creates the SQLite3 DB to hold crawled data.

    '''
    try:
        cursor.execute("create table data (urls varchar2(50), score integer, root integer);")
        connection.commit()
    except sqlite3.OperationalError, exp:
        print(exp)


def showDB(connection,cursor):
    '''
    Dumps the DB on screen.

    '''
    try:
        cursor.execute("select * from data order by score desc;")
        rows = cursor.fetchall()
        description = cursor.description
        for rowdescription in description:
            print '%s' % rowdescription[0].ljust(15),
        print
        for row in rows:
            for i in range(len(row)):
                print ' %s' % str(row[i]).ljust(15),
            print
        connection.commit()
    except sqlite3.OperationalError, exp:
        print exp

    
def resetDB(connection,cursor):
    cursor.execute("delete from data;")
    connection.commit()
    
    
def openDB():
    connection = sqlite3.connect('mydb')
    cursor = connection.cursor()
    return connection, cursor


def insert_val(url,connection,cursor):
    '''
    This method gets called by the crawl method.The url it receives, either
inserts it into the database or the score attribute gets increased by one
everytime it is found in the database.The root(=1) attribute defines the
url that is going to be visited.After being visited the value of the root
attribute is changed to 0.count is used to set limit of the crawler
i.e. how many links will be stored n the database.
    '''
    try:
        cursor.execute("select count(*) from data;")
        count=cursor.fetchone()
        print count[0]
        
        if count[0] < 1000:
            cursor.execute("select urls from data where urls = ? ;", (unicode(url),))
            rows = cursor.fetchone()
            if rows:
                cursor.execute("update data set score=score+1 where urls = ?;",
                               (unicode(url),))      
                cursor.execute("update data set root=0;")
                connection.commit()
                showDB(connection,cursor)
                return True, None
            cursor.execute("update data set root=0;")
            cursor.execute("insert into data values(?, 1, 1);", (unicode(url),))    
             
            connection.commit()
            showDB(connection,cursor)
            return False, url
        sys.exit(1)           
    except sqlite3.OperationalError, exp:
        print exp            


if __name__ == "__main__":
    crawl()
