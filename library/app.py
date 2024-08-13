from flask import Flask, render_template, request, Response, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)
list_loanid = ()
connection = mysql.connector.connect(host='localhost', database='library', user='root', password='root', auth_plugin="mysql_native_password")
cursor = connection.cursor(buffered=True)

@app.route('/checkin', methods=['GET', 'POST'])
def check_in(): 
    if request.method == "POST":  
        if request.form['search'] == 'Search':
            book = "\"%"+request.form['book']+"%\""        
            cursor.execute("SELECT book_loans.isbn13,book_loans.card_id,borrower.bname,book_loans.loan_id FROM book_loans JOIN borrower ON book_loans.card_id = borrower.card_id JOIN books ON books.isbn13 = book_loans.isbn13 WHERE (borrower.bname like "+book+" or book_loans.card_id like "+book+" or book_loans.isbn13 like "+book+") and (books.available=\"NO\") and book_loans.date_in is NULL;")
            connection.commit()       
            data = cursor.fetchall()
            if data==[]:
                msg="This user has not taken any book" 
                return render_template('checkin.html',msg=msg) 
            return render_template('checkin.html', data=data)
        else:
            return render_template('fine.html')     
    return render_template('checkin.html')



@app.route("/clear_fines", methods=["GET","POST"])
def clear_fines():
    # search = request.args.get("loanid")        
    # list_loanid = tuple(search.split(','))
    if(request.method=="POST"):
        loan_ids = request.json['loanIds']
        lids=','.join(loan_ids)        
        if(len(loan_ids)>0):
            for loanid in loan_ids:                
                loanid=str(loanid)
                cursor.execute("UPDATE books join book_loans on books.isbn13=book_loans.isbn13 set books.available=\"YES\" where book_loans.loan_id="+loanid+";")
                cursor.execute("UPDATE book_loans set date_in=sysdate() where loan_id="+loanid+";")
            cursor.execute("select loan_id, date_out, due_date, date_in, IF(DATEDIFF(sysdate(), due_date)>0, DATEDIFF(sysdate(), due_date)*0.25, 0) as fine from book_loans where date_in is NULL and loan_id in ("+lids+");")
            connection.commit()       
            data = cursor.fetchall()
            cursor.execute("select loan_id, date_out, due_date, date_in, IF(DATEDIFF(sysdate(), due_date)>0, DATEDIFF(sysdate(), due_date)*0.25, 0) as fine from book_loans where date_in is not NULL and loan_id in ("+lids+");")
            connection.commit()       
            datax = cursor.fetchall()
            for d in datax:                
                x=str(d[4])
                li=str(d[0])                
                cursor.execute("insert ignore into fines values("+li+","+x+","+"True"+");")
            cursor.execute("SELECT * FROM( SELECT * FROM fines ORDER BY loan_id DESC LIMIT 5) AS sub ORDER BY loan_id ASC;")
            connection.commit()       
            data1 = cursor.fetchall()
            cursor.execute("select book_loans.card_id, SUM(fines.fine_amt) from book_loans inner join fines on book_loans.loan_id=fines.loan_id where book_loans.date_in is not NULL group by book_loans.card_id;")
            connection.commit()       
            data2 = cursor.fetchall()
            return render_template('fine.html', data=data, data1=data1, data2=data2)            
        return Response("No Loans selected",status=404)
    return Response("Invalid Request Type",status=404)


@app.route('/fine', methods=['GET', 'POST'])
def fine(): 
    search = request.args.get("loanid")        
    list_loanid = search.split(',')
    lids=','.join(list_loanid)
    if request.method == "GET" or request.method == "POST":
        cursor.execute("select loan_id, date_out, due_date, date_in, IF(DATEDIFF(sysdate(), due_date)>0, DATEDIFF(sysdate(), due_date)*0.25, 0) as fine from book_loans where date_in is NULL and loan_id in ("+lids+");")
        connection.commit()       
        data = cursor.fetchall() 
        cursor.execute("SELECT * FROM( SELECT * FROM fines ORDER BY loan_id DESC LIMIT 5) AS sub ORDER BY loan_id ASC;")
        connection.commit()       
        data1 = cursor.fetchall()
        connection.commit()  
        cursor.execute("select book_loans.card_id, SUM(fines.fine_amt) from book_loans inner join fines on book_loans.loan_id=fines.loan_id where book_loans.date_in is not NULL group by book_loans.card_id;")     
        data2 = cursor.fetchall()
        return render_template('fine.html', data=data, data1=data1, data2=data2)       
    return render_template('fine.html')
    


@app.route('/borrow', methods=['GET', 'POST'])
def borrow():  
    list_isbn=[] 
    card_id=""
    
    search = request.args.get("isbn")        
    list_isbn = search.split(',')
    msg=""
    
    if request.method == "POST":
        card_id = "\""+request.form["cardid"]+"\""
        cursor.execute("SELECT count(card_id) FROM book_loans where card_id="+card_id+" and date_in is NULL;")               
        num_books = cursor.fetchall()         
        if num_books[-1][-1]+len(list_isbn) <= 3:
            for isbn in list_isbn:
                cursor.execute("SELECT available from books where isbn13=\""+isbn+"\";")
                available=cursor.fetchall()
                if available[-1][-1]=="YES":                    
                    cursor.execute("Select count(*) from borrower where card_id="+card_id+";")
                    user=cursor.fetchall()
                    if user[-1][-1]:                    
                        cursor.execute("Insert into book_loans(isbn13,card_id,date_out,due_date) values("+isbn+","+card_id+",SYSDATE(),DATE_ADD(sysdate(), INTERVAL 14 DAY));")    
                        cursor.execute("UPDATE books set available=\"NO\" where isbn13="+isbn+";")
                    else:
                        msg="STUDENT RECORD NOT FOUND"     
                else:
                    msg="BOOK "+isbn+" NOT AVAILABLE"            
        else: 
            msg="STUDENT HAS ALREADY TAKEN "+ str(num_books[-1][-1]) +" BOOKS"

        cursor.execute("select book_loans.loan_id, book_loans.isbn13, books.title, book_loans.card_id, book_loans.date_out, book_loans.due_date from book_loans join books on book_loans.isbn13=books.isbn13 where book_loans.card_id="+card_id+" and book_loans.date_in is NULL;")
        connection.commit()
        data = cursor.fetchall()  
        return render_template('borrow.html', data=data,msg=msg)
    return render_template('borrow.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":  
        if request.form['search'] == 'Search':
            book = "\"%"+request.form['book']+"%\""        
            cursor.execute("SELECT DISTINCT books.isbn13, books.title, authors.name, books.available FROM books inner JOIN book_authors ON books.book_id = book_authors.book_id inner JOIN authors ON authors.author_id = book_authors.author_id WHERE authors.name like "+book+" or books.title like "+book+" or books.isbn13 like "+book+";")
            connection.commit()       
            data = cursor.fetchall()       
            return render_template('search.html', data=data)
        else:
            return render_template('borrow.html')              
    return render_template('search.html')


@app.route('/insertborrower', methods=['GET', 'POST'])
def insert_borrower():
    if request.method == "POST":
        ssn = "\""+request.form["ssn"]+"\""
        name = "\""+request.form["name"]+"\""
        address = "\""+request.form["address"]+"\""
        phone = "\""+request.form["phone"]+"\""
        if request.form['insert'] == 'ADD':
            cursor.execute("Select count(*) from borrower where ssn="+ssn+";")
            num=cursor.fetchall()
            if num[-1][-1] == 0:
                cursor.execute("set @card_id:=(SELECT IFNULL (CONCAT('ID',LPAD((SUBSTRING_INDEX(MAX(card_id),'ID',-1)+1),6,'0')),'ID001') AS card_id FROM borrower ORDER BY card_id ASC);")
                cursor.execute("insert into borrower(card_id,ssn,bname,address,phone) values(@card_id,"+ssn+","+name+","+address+","+phone+");")
                cursor.execute("SELECT * FROM( SELECT * FROM borrower ORDER BY card_id DESC LIMIT 10) AS sub ORDER BY card_id ASC;")
                connection.commit()       
                data = cursor.fetchall()  
                return render_template('insertborrower.html', data=data, msg="Borrower Inserted")
            else:
                return render_template('insertborrower.html', msg="SSN already exists")
        else:
            cursor.execute("delete from borrower where ssn="+ssn+";")
            cursor.execute("SELECT * FROM( SELECT * FROM borrower ORDER BY card_id DESC LIMIT 10) AS sub ORDER BY card_id ASC;")
            connection.commit()       
            data = cursor.fetchall()
            return render_template('insertborrower.html', data=data, msg="Borrower Deleted")
    return render_template('insertborrower.html')


@app.route('/insertbooks', methods=['GET', 'POST'])
def insert_books():
    if request.method == "POST":
        book_id = "\""+request.form["book_id"]+"\""
        isbn13 = "\""+request.form["isbn13"]+"\""
        title = "\""+request.form["title"]+"\""
        available = "\""+request.form["available"]+"\""
        if request.form['insert'] == 'ADD':
            cursor.execute("insert into books values("+book_id+","+isbn13+","+title+","+available+");")
            cursor.execute("Select * from books where book_id="+book_id+";")
            connection.commit()       
            data = cursor.fetchall()
            return render_template('insertbooks.html', data=data, msg="Book Inserted")
        else:
            cursor.execute("delete from books where isbn13="+isbn13+";")
            connection.commit()       
            return render_template('insertbooks.html', msg="Book Deleted")
    return render_template('insertbooks.html')




























