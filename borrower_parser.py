import mysql.connector
from mysql.connector import Error

f = open('borrowers.csv', 'r', encoding="utf-8")
f.readline()
rowCounter = 0

try:
    connection = mysql.connector.connect(host='localhost', database='library', user='root', password='root', auth_plugin="mysql_native_password")                        
    

    for line in f:
        cols = line.split(",") #card_id,ssn,first_name,last_name,email,address,city,state,phone   
        #borrowers card_id, ssn, bname, address, phone 
        card_id="\""+cols[0] + "\""  
        ssn="\""+cols[1] + "\"" 
        bname = "\""+ cols[2]+" "+cols[3] + "\""       
        address="\""+cols[5]+" "+cols[6]+" "+cols[7]+ "\""  
        phone="\""+cols[8]+ "\""

        #print(card_id, ssn, bname, address, phone)
        
        cursor = connection.cursor()
        cursor.execute("INSERT INTO borrower(card_id,ssn,bname,address,phone) VALUES ("+card_id+","+ssn+","+bname+","+address+","+phone+");")
            
        rowCounter += 1    
    connection.commit()
    print(rowCounter)

except Error as e:
    print("Error while connecting to MySQL", e)

f.close()
