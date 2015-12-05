import sqlite3


try:
    conn = sqlite3.connect("data_2.0.db")
except sqlite.Error as e:
    print "Error:", e.arg[0]
else:
    cursor = conn.cursor()
# though dagerous, may help here.
    cursor.execute("select contract, minday from tcontracts")
    r = cursor.fetchone()
    tablenames = {}
    while r is not None:
        name = r[0] + "_" +r[1]
        tablenames.setdefault(name, [])
        r = cursor.fetchone()

    for i in tablenames.keys():
        cursor.execute("select count(*) from '%s'" % i)
        ii = cursor.fetchone();
        if ii is not None:
            tablenames[i].append(ii)

    cursor.close()
    cursor = None
    conn.close()
    conn = None
    print len(tablenames)

    
