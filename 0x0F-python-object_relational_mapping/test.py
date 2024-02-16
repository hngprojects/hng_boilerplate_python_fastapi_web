import MySQLdb

# Establish a connection to the MySQL database
db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="Njenga008!",
                     db="hbtn_0e_0_usa")

# Create a cursor object using cursor() method
cursor = db.cursor()

# Execute a SQL query
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method
data = cursor.fetchone()

print("Database version:", data[0])

# Disconnect from server
db.close()

