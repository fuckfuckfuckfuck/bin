import re
import sqlite3

pattern = "([(a-zA-Z)]{1,3})(\d{4})_(Min|Day)"
p = re.compile(pattern)

def record(res):
    records = {
        'pinzhong' : res[0],
        'jiaogeyue' : res[1],
        'minday' : res[2],
        'name' : res[0]+res[1]
        }
    return records
        
def scan(filestr):
    reader = open(filestr, 'r')
    records = []
    errors = []
    cnt = 0
    for line in reader:
        tmp_0 = (line.strip()).split()
        for lin in tmp_0:
            tmp = p.match(lin.strip())
            if (tmp == None):
                errors.append(lin.strip())
            else:
                tmp1 = tmp.groups()
                records.append(record(tmp.groups()))
            cnt = cnt + 1

    print "%s are scaned.", cnt
    reader.close()
    reader = None
    return (records, errors)

sqls = "INSERT INTO tcontracts (contract, ticker, deliver, minday) VALUES (?,?,?,?)"

def inserta(aa):
    try:
        # conn = sqlite3.connect("data_2.0.db")
        conn = sqlite3.connect("data_2_0.db")
    except sqlite3.Error as e:
        print "Error:", e.arg[0]    
    else:
        cursor = conn.cursor()
        for a in aa:
            cursor.execute(sqls, (a['name'],a['pinzhong'],a['jiaogeyue'],a['minday']))

        conn.commit()
        
        cursor.close()
        conn.close()
        conn = None

a = scan("contract_name")
a0 = a[0]
a1= a[1]
b=inserta(a0)


    
