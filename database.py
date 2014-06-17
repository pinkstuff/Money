import sqlite3
import money4
#import numpy as np
#import matplotlib.pyplot as plt


#conn = sqlite3.connect('/Users/pholland/Database/money.db')
#c = conn.cursor()
#santander = money2.statement('/Users/pholland/Downloads/Statements09012746909754.txt')

def formatDatabase():
    safety = raw_input('Caution: This will destroy EVERYTHING \nContinue  Y/N:')
    if safety == 'Y' or safety == 'y': 
        conn = sqlite3.connect('/Users/pholland/Database/money.db')
        c = conn.cursor()
        
        commands = ["DROP TABLE IF EXISTS raw_statement;", \
                    "DROP TABLE IF EXISTS useful_statement;", \
                    "CREATE TABLE raw_statement(Date TEXT, Description TEXT, Amount TEXT, Balance TEXT);", \
                    "CREATE TABLE useful_statement \
                     (Timestamp INTEGER, \
                      Description TEXT,  \
                      Place TEXT, \
                      Amount REAL, \
                      Balance REAL, \
                      Type TEXT, \
                      Account TEXT);"]
                     
        for command in commands:
            c.execute(command)
    
        conn.commit()
        c.close

def exportRaw(statementlist):
    conn = sqlite3.connect('/Users/pholland/Database/money.db')
    c = conn.cursor()
    for trans in statementlist:
        c.execute('INSERT INTO raw_statement VALUES(?, ?, ?, ?);', 
                  (trans.date, trans.description, trans.amount, trans.balance),)
    conn.commit()
    c.close

def exportUseful(statementlist):
    conn = sqlite3.connect('/Users/pholland/Database/money.db')
    c = conn.cursor()
    for trans in statementlist:
        c.execute('INSERT INTO useful_statement VALUES(?, ?, ?, ?, ?, ?, ?);', \
                  (trans.timestamp, \
                   trans.description, \
                   trans.place, \
                   trans.amount, \
                   trans.balance, \
                   trans.transaction_type,
                   trans.account),)
    conn.commit()
    c.close

def exportAll(statementlist):
    exportRaw(statementlist)
    exportUseful(statementlist)
        
#formatDatabase()
#exportAll()
#conn.commit()
#
#fig = plt.figure()
#graph = fig.add_subplot(111)

def getdata():
    conn = sqlite3.connect('/Users/pholland/Database/money.db')
    c = conn.cursor()
    command = """SELECT Timestamp, SUM(Amount) 
                 FROM useful_statement  
                 GROUP BY Timestamp
                 ORDER BY Timestamp ASC;"""    
    c.execute(command)
    foo = c.fetchall()
    conn.commit()
    c.close
    return foo

#data = getdata()
#i = 0
#X = []
#Y = []
#while i < len(data)-1:
#    if data[i+1][0] - data[i][0] > 24*60*60:
#        data.insert(i+1, (data[i][0] + 24*60*60, 0))
#    i += 1
# 
#for time, amount in data:
#    X.append(time)
#    Y.append(amount)    
#
#
#graph.plot(np.asarray(X),np.asarray(np.abs(Y)))
#graph.set_xlabel("Timestamp")
#graph.set_ylabel("Amount")
#graph.grid(True)
#graph.set_ylim(0,250)
#plt.show()


#formatDatabase()
#sant = money4.fromSantander('/Users/pholland/Documents/workspace/money/Statements/Statements09012746909754 (1).txt')
#nat = money4.fromNatwest('/Users/pholland/Downloads/HOLLANDPSV07-20130531.csv')
#exportAll(nat)
#exportAll(sant)

#print 'done'
