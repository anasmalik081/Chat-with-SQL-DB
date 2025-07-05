import sqlite3

# Connect to Sqlite
connection = sqlite3.connect("student.db")

# Create a cursor object to insert record, create table
cursor = connection.cursor()

# create the table
table_info = (
    """
    CREATE TABLE student(
        name VARCHAR(25),
        class VARCHAR(25),
        section VARCHAR(25),
        marks INT
    )
    """
)
cursor.execute(table_info)

# Insert some records
cursor.execute('''INSERT INTO student VALUES('Anas', 'Data Science', 'A', 90)''')
cursor.execute('''INSERT INTO student VALUES('Aarish', 'Web Developer', 'B', 100)''')
cursor.execute('''INSERT INTO student VALUES('Afzal', 'DevOps', 'A', 85)''')
cursor.execute('''INSERT INTO student VALUES('Ruby', 'DevOps', 'A', 50)''')
cursor.execute('''INSERT INTO student VALUES('Ayzal', 'Data Science', 'A', 35)''')

# Display all the records
print("The Inserted Records are: ")
data = cursor.execute('''SELECT * FROM student''')
for row in data:
    print(row)
    print("-"*10)

# Commit your changes in the database
connection.commit()
connection.close()