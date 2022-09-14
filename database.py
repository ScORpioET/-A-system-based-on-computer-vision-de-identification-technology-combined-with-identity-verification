import sqlite3




conn = sqlite3.connect('database.db')


c = conn.cursor()

# 創立表格
# c.execute('''CREATE TABLE stocks
#                 (account TEXT, password TEXT,name TEXT,id TEXT,birthday TEXT,email TEXT, first_login TEXT)''')


c.execute("INSERT INTO stocks VALUES ('3A717036', '0000', '王小明', 'A123456789', '1999-11-16', '', '1')")



# 刪除值
# c.execute("DELETE FROM stocks WHERE account LIKE '3A717038'")

# c.execute("UPDATE stocks SET email = 'x917205725@gmail.com' WHERE account = '3A717039'")

# c.execute("INSERT INTO stocks VALUES ('3A717039', '0000', '王昱傑', 'L125404120', '1999-11-16', '', '1')")

for e in c.execute("SELECT * FROM stocks"):
    # if e[1] == 'white' and e[2] == 'male' and e[4] >= 142 and e[4] <= 160:
        print(e)

# for e in c.execute("SELECT * FROM stocks WHERE password LIKE 'zxzxcvv1'" ):
#     print(e)

# for e in c.execute("SELECT * FROM stocks WHERE name LIKE '%"+str(name)+"%'"):
#     print(e)

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
