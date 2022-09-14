import sqlite3


def database(name, race, gender, nose, avg, shadow, light):
    

    conn = sqlite3.connect('face_color.db')


    c = conn.cursor()

    # 創立表格
    # name, race, gender, nose width, avg color, shadow, light
    # c.execute('''CREATE TABLE stocks
    #              (name TEXT, race TEXT, gender, avg INTEGER, shadow INTEGER, light INTEGER)''')

    # 插入值

    c.execute("INSERT INTO stocks VALUES ( '" + str(name) + "', '" + str(race) + "', '" + str(gender) + "', " + str(nose) + ", " + str(avg) + "," + str(shadow) + ", " + str(light) + ")")
    
    
    

    # 刪除值
    # c.execute("DELETE FROM stocks WHERE light = '5'")



    # for e in c.execute("SELECT * FROM stocks ORDER BY name"):
    #     print(e)

    for e in c.execute("SELECT * FROM stocks WHERE name LIKE '%"+str(name)+"%'"):
        print(e)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def watch_database():

    conn = sqlite3.connect('face_color.db')


    c = conn.cursor()

    # c.execute('''CREATE TABLE stocks
    #              (name TEXT, race TEXT, gender TEXT, nose INTEGER, avg INTEGER, shadow INTEGER, light INTEGER)''')


    # for e in c.execute("SELECT * FROM stocks WHERE race LIKE '%white%'"):
    for e in c.execute("SELECT * FROM stocks WHERE gender LIKE 'male' ORDER BY avg"):
    # for e in c.execute("SELECT * FROM stocks WHERE name"):
        # if e[4] > 167:
        print(e)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()







if __name__ == '__main__':
    watch_database()

