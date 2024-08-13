import mysql.connector
from mysql.connector import Error

f = open('books.csv', 'r', encoding="utf-8")
f.readline()
rowCounter = 0

try:
    connection = mysql.connector.connect(host='localhost', database='library', user='root', password='root', auth_plugin="mysql_native_password")                        
    author_id = 1
    book_id   = 1
    author_dict = dict()
    for line in f:
        cols = line.split("\t")  
        authors = cols[3].replace('"','\\"').split(",")    
        isbn_13 = cols[1]
        title = cols[2]
        
        title= title.replace('"','\\"')
        title=title.replace("'","\\'")
        title=title.replace("(","\\(")
        title=title.replace(")","\\)")
        
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Books (book_id, isbn13, title) VALUES (" + str(book_id) + "," + isbn_13 +",\""+ title + "\");")

        for auth in authors:
            if auth not in author_dict:
                author_dict[auth]=author_id
                cursor.execute("INSERT INTO Authors (author_id, name) VALUES (" + str(author_id) + ",\"" + str(auth) + "\");")
                cursor.execute("INSERT INTO Book_authors (book_id, author_id) VALUES (" + str(book_id) + "," + str(author_id) + ");")    
                author_id += 1  
            else:
                cursor.execute("INSERT INTO Book_authors (book_id, author_id) VALUES (" + str(book_id) + "," + str(author_dict[auth]) + ");")              

        book_id += 1 
        rowCounter += 1    
    connection.commit()

except Error as e:
    print("Error while connecting to MySQL", e)

f.close()
