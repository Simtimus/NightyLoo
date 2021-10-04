import mysql.connector


# Initierea clasului
class DBlib:

	# Initiating class and database connector
	def __init__(self, host, user, password, database):
		self.host = host
		self.user = user
		self.password = password
		self.database = database
		self.mydb = None
		self.mycursor = None

	# Connects the database
	def connect(self):
		"""
		Face conectiunea intre baza de date
		"""
		self.mydb = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
		self.mycursor = self.mydb.cursor()

		self.mycursor.execute(f"USE {self.database}")

	# Return the names of all tables from database
	def table_names(self) -> list:
		"""
		Returneaza: o lista cu toate denumirile de tabele
		"""
		self.mycursor.execute("SHOW TABLES")
		table_names = []
		for tab in self.mycursor.fetchall():
			table_names.append(tab[0])
		return table_names

	# Read all rows from a tabel
	def read_rows(self, table: str, ends: int = 1, starts: int = 1) -> tuple:
		"""
		Returneaza: un tuple format din randurile alese: ((<row_info>, ...), (<row_info>, ...))
		"""
		self.mycursor.execute(f"SELECT * FROM `{table}` WHERE `Id` >= {starts} AND `Id` <= {ends}")
		myresult = self.mycursor.fetchall()
		return myresult

	# Count how many times a user has been called
	def count_times(self, table: str, name: str) -> int:
		"""
		Returneaza: numarul de cate ori o persoana se gaseste in tabel
		"""
		sql = f"SELECT * FROM `{table}` WHERE `Numele` = '{name}'"
		self.mycursor.execute(sql)
		myresult = self.mycursor.fetchall()
		times = 0
		for x in myresult:
			times += 1
		return times

	# Read all users from database
	def get_users(self, table: str = 'Utilizatorii') -> list:
		"""
		Returneaza: o lista de utilizatori
		"""
		self.mycursor.execute(f"SELECT * FROM `{table}`")
		myresult = self.mycursor.fetchall()
		users = []
		for result in myresult:
			users.append(result[1])
		return users

	# Return the last row id from table
	def last_row_id(self, table: str) -> int:
		"""
		Returneaza: o lista de utilizatori din tabel
		"""
		sql = f"SELECT * FROM `{table}` ORDER BY `Id` DESC LIMIT 1"
		self.mycursor.execute(sql)
		return self.mycursor.fetchall()[0][0]

	# Inserts a row into a table
	def insert(self, table: str, user: str, indexes: list, values: list):
		"""
		Insereaza in tabel valori dupa index-urile date
		"""
		tab_name = 'TabeleRestrictionate'
		restricted = self.read_rows(tab_name, self.last_row_id(tab_name))

		sql_indexed = '`, `'.join(indexes)

		sql_values = ''
		ind = 0
		while ind < len(values):
			if ind < len(values) - 1:
				sql_values += '%s, '
			elif ind == len(values) - 1:
				sql_values += '%s'
			ind += 1

		if table not in restricted and user in self.get_users():
			sql = f"INSERT INTO `{table}` (`{sql_indexed}`) VALUES({sql_values})"
			val = tuple(values)
			self.mycursor.execute(sql, val)
			self.mydb.commit()

	# Inserts data into table with a default input values
	def default_insert(self, table: str, indexes: list, values: list):
		"""
		Insereaza in tabel valori dupa index-urile date, lucreaza pentru orice baza de date
		"""
		sql_indexed = '`, `'.join(indexes)

		sql_values = ''
		ind = 0
		while ind < len(values):
			if ind < len(values) - 1:
				sql_values += '%s, '
			elif ind == len(values) - 1:
				sql_values += '%s'
			ind += 1
		
		sql = f"INSERT INTO `{table}` (`{sql_indexed}`) VALUES({sql_values})"
		val = tuple(values)
		self.mycursor.execute(sql, val)
		self.mydb.commit()

	# Updates a row
	def update(self, table: str, row_id: int, change_list: list):
		"""
		Innoieste un rand din tabel
		"""
		sql = f"UPDATE `{table}` SET `{change_list[0]}` = '{change_list[1]}' WHERE `Id` = {row_id}"
		self.mycursor.execute(sql)
		self.mydb.commit()

	# Returns the table collumns names
	def collumn_name(self, table_schema: str, table_name: str):
		"""
		Returneaza: o lista de denumire de coloane din tabel
		"""
		sql = f"SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='{table_schema}' AND `TABLE_NAME`='{table_name}';"
		self.mycursor.execute(sql)
		return self.mycursor.fetchall()[0][0]

# UPDATE customers SET address = 'Canyon 123' WHERE address = 'Valley 345'
