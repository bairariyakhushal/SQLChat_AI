import sqlite3

## connect to sqllite
connection=sqlite3.connect("student.db")

##create a cursor object to insert record,create table
cursor=connection.cursor()

# create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS student (
    name VARCHAR(25),
    class VARCHAR(25),
    section VARCHAR(25),
    marks INTEGER
)
""")

# insert records
cursor.execute("INSERT INTO student VALUES ('Krish','Data Science','A',90)")
cursor.execute("INSERT INTO student VALUES ('John','Data Science','B',85)")
cursor.execute("INSERT INTO student VALUES ('Mukesh','Data Science','A',88)")
cursor.execute("INSERT INTO student VALUES ('Jacobs','DevOps','A',50)")

# read records
data = cursor.execute("SELECT * FROM student")

print("Inserted Records:")
for row in data:
    print(row)
    
    
# save + close
connection.commit()
connection.close()