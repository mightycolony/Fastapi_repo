import sqlite3
con = sqlite3.connect("./base/os_info.db")

cur = con.cursor()



cur.execute("SELECT * FROM osinfo;")
print(f"Table Name : {cur.fetchall()}")

cur.execute("SELECT * FROM signingpass;")
print(f"Table Name : {cur.fetchall()}")