import urllib
import sqlite3
from collections import deque
import sgmllib
import sys

q = deque([])         # This is a queue to store the urls as BFS algorithm is used here.

class URLLister(sgmllib.SGMLParser):
    '''
    Brief explanation here

    '''
    def reset(self):
        sgmllib.SGMLParser.reset(self)
        
    def store(self,u):
        self.url = u            # This is a string object to store the immediate parent url.
        
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
    Brief explanation here

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
    Brief explanation here

    '''
    u = raw_input("Enter a URL: ")
    connection, cursor=openDB()
    resetDB(connection,cursor)
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
        cursor.execute("drop table data;")
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
    Brief description here

    '''
    try:
        cursor.execute("select count(*) from data;")
        count=cursor.fetchone()
        print count[0]
        
        if count[0] < 1000:
            cursor.execute("select urls from data where urls = ? ;", (url,))
            rows = cursor.fetchone()
            if rows:
                cursor.execute("update data set score=score+1 where urls = ?;",
                               (url,))      
                cursor.execute("update data set root=0;")
                connection.commit()
                showDB(connection,cursor)
                return True, None
            cursor.execute("update data set root=0;")
            cursor.execute("insert into data values(?, 1, 1);", (url,))    
             
            connection.commit()
            showDB(connection,cursor)
            return False, url
        sys.exit(1)           
    except sqlite3.OperationalError, exp:
        print exp            


if __name__ == "__main__":
    crawl()
