import sys
import bsddb3 as bsddb
import random
import subprocess
import time
from bsddb3 import db

DA_FILE = "/tmp/my_db/chase_db"
INDEX_FILE = "/tmp/my_db/index_file"
DB_SIZE = 1000
SEED = 10000000

dbType = None
db = None
indexDB = None

## Create Tables ========================================
def createHashTable():
	## Create and populate hash Table
	print("Creating Hash Table")
	try:
		db = bsddb.hashopen(DA_FILE, "w")
	except:
		print("DB doesn't exist, creating a new one")
		db = bsddb.hashopen(DA_FILE, "c")
	populate(db)
	return db
def createBTree():
	## Create and populate B Tree (see initialLabCode.py for original lab code)
	print("Creating B Tree")
	try:
		db = bsddb.btopen(DA_FILE, "w")
	except:
		print("DB doesn't exist, creating a new one")
		db = bsddb.btopen(DA_FILE, "c")
	populate(db)
	return db
def createIndexFile():
	## Create and Populate indexFile
	#!# Add flag for duplicate keys

	print("Creating Index File")
	global indexDB
	try:
		db = bsddb.btopen(DA_FILE, "w")
	except:
		print("DB doesn't exist, creating a new one")
		db = bsddb.btopen(DA_FILE, "c")
	try:
		indexDatabase = db.DB()
		indexDatabase.set_flags(db.DB_DUPSORT)
		indexDatabase.open(INDEX_FILE, None, db.DB_BTREE, db.DB_CREATE)
		##indexDB = bsddb.btopen(INDEX_FILE, "w")
		##indexDB.set_flags(bsddb3.DB_DUPSORT)
		indexDB = indexDatabase.cursor()
	except:
		print("DB doesn't exist, creating a new one")
		indexDB = bsddb.btopen(INDEX_FILE, "c")	

	populateWithIndex(db, indexDB)
	return db
def destroyDatabase():
	## Destroys the database if it exists
	print("Destroying Database")
	subprocess.call(["rm", "-f", "/tmp/my_db/chase_db"])
	subprocess.call(["rm", "-f", "/tmp/my_db/index_file"])
	return


## Populate Tables =========================================
def populate(db):
	# change to be populated with random values instead of these values as specified in assignment

	for index in range(DB_SIZE):
		krng = 64 + get_random()
		key = ""
		for i in range(krng):
			key += str(get_random_char())
		vrng = 64 + get_random()
		value = ""
		for i in range(vrng):
			value += str(get_random_char())
		print (key)
		print (value)
		print ("")
		key = key.encode(encoding='UTF-8')
		value = value.encode(encoding='UTF-8')
		db[key] = value
	return

def populateWithIndex(db, indexDB):
	## populate both database and indexFile
	for index in range(DB_SIZE):
		krng = 64 + get_random()
		key = ""
		for i in range(krng):
			key += str(get_random_char())
		vrng = 64 + get_random()
		value = ""
		for i in range(vrng):
			value += str(get_random_char())
		print (key)
		print (value)
		print ("")
		key = key.encode(encoding='UTF-8')
		value = value.encode(encoding='UTF-8')
		db[key] = value
		indexDB[value] = key
	return

## User Interface for retrieve Functions ====================
def startRetrieveWithKey():
	## gets user key and calls retrieveWithKey(key)
	key = input("Please enter a key to get data: ")
	records = []
	# start timer
	start = time.clock()
	try:
		records = retrieveWithKey(key)
	except:
		print("\nInvalid Key\n")
		return
	# end timer
	elapsed = (time.clock() - start)
	printRecords(key, records, elapsed, "KEY")
	return
def startRetrieveWithData():
	## Gets user data and calls retrieveWithData(data)
	data = input("Please enter data to get key: ")
	records = []
	# start timer
	start = time.clock()
	if dbType == 'indexfile':
		try:
			records = retrieveWithDataFromIndex(data)
		except:
			print("\nInvalid Key\n")
			return
	else:
		try:
			records = retrieveWithData(data)
		except:
			print("\nInvalid Key\n")
			return
	# end timer
	elapsed = (time.clock() - start)
	printRecords(records, data, elapsed, "DATA")
	return
def startRetrieveWithRange():
	## Gets user range and calls retrieveWithRange(keyRange)
	#global dbType
	while(True):
		keyRange = input("Please enter a key range to get data, enter the first key, followed by a space, followed by the last key [ex: aa bb] : ")
		keyRange = keyRange.strip()
		rangeList = keyRange.split(' ')
		if len(rangeList) != 2:
			print("invalid format of key range")
			continue
		if rangeList[0] > rangeList[1]:
			print("invalid format of key range")
			continue
		break

	records = []
	# start timer
	start = time.clock()
	if dbType == "hash":
		try:
			records = retrieveWithRangeHash(rangeList[0], rangeList[1])
		except:
			print("\nInvalid Key\n")
			return
	elif dbType == "btree":
		try:
			records = retrieveWithRangeBTree(rangeList[0], rangeList[1])
		except:
			print("\nInvalid Key\n")
			return
	elif dbType == "indexfile":
		try:
			records = retrieveWithRangeBTree(rangeList[0], rangeList[1])
		except:
			print("\nInvalid Key\n")
			return
	else:
		print("Sorry, something has gone wrong")
		print(dbType)
		records = []
	elapsed = (time.clock() - start)
	printRecords(keyRange, records, elapsed, "RANGE")
	return

def printRecords(key, records, elapsed, recordType):
	print("\n== Records ======")
		
	numRecords = len(records)
	elapsedTime = elapsed
	if numRecords > 0:
		print("Records Retrieved: %d" % numRecords)
	else:
		print("No Records Retrieved")
	print("Elapsed Time: " + str(elapsed) + "\n")
	
	answersFile = open('answers','a')

	if recordType == "DATA":
		for keys in key:
			print(keys)
			print("")

			answersFile.write(keys + "\n" + records + "\n\n")
	
	elif recordType == "KEY":
		for record in records:
			print(record)
			print("")
	
			answersFile.write(key + "\n" + record + "\n\n")

	elif recordType == "RANGE":

		for record in records:
			print(record)
			print("")
			
			if dbType.lower() == "btree" or dbType.lower() == "hash":
				key = retrieveWithData(record)
			if dbType.lower() == "indexfile":
				key = retrieveWithDataFromIndex(record)
			
			answersFile.write(key[0] + "\n" + record + "\n\n")
					
	print("\n=============")
	answersFile.close()	
	return

## Retrieve Functions =======================================
def retrieveWithKey(key):
	## Returns Data with given key
	print("Retrieving Data for key: %s" % key)
	values = []
	key = str(key).encode(encoding='UTF-8')
	value = db[key]
	value = value.decode(encoding='UTF-8')
	values.append(value)
	return values
def retrieveWithData(data):
	## Returns Keys with given data
	##print("Retrieving Key for data: %s" % data)
	data = str(data).encode(encoding='UTF-8')
	#cursor = db.cursor()
	allItems = db.items()
	keysList = []
	for item in allItems:
		itemData = item[1]
		if itemData == data:
			itemKey = item[0].decode(encoding='UTF-8')
			keysList.append(itemKey)
			print(itemKey)
	return keysList
def retrieveWithDataFromIndex(data):
	## Returns Keys with given data
	#!# Add functionality for miltiple keys
	##print("Retrieving Key with for data: %s" % data)
	values = []
	key = str(data).encode(encoding='UTF-8')
	value = indexDB[key]
	value = value.decode(encoding='UTF-8')
	values.append(value)
	return values
def retrieveWithRangeBTree(startKey, endKey):
	## Returns records with key in given range
	print("Retrieving records in range: %s - %s" % (startKey, endKey))
	values = []
	## So i belive the way to do this is simply get the data associated with the start key, and keep calling "get next" till the key is greater than the end key
	encodedStart = str(startKey).encode(encoding='UTF-8')
	encodedEnd = str(endKey).encode(encoding='UTF-8')

	# This doesn't work because the start range wont be key, we need the first key after the start key, use set_range() to achieve this
	current = db.set_location(encodedStart)
	while(current[0].decode(encoding='UTF-8') < endKey):
		values.append(current[1].decode(encoding='UTF-8'))
		current = db.next()
	return values
def retrieveWithRangeHash(startKey, endKey):
	## Returns records with key in given range
	print("Retrieving records in range: %s - %s" % (startKey, endKey))
	values = []
	##	encode start and end keys
	##	Interate through entire hash database, if key is greater than start and less than end key
	##  Wondering if encoded keys should be compared here.... since that seems like it would mess up ordering
	#startKey = str(startKey).encode(encoding='UTF-8')
	#endKey = str(endKey).encode(encoding='UTF-8')	

	# So Im using numbers for data here but its going to be working on strings... so this logic isn't really correct here
	# In theory, however, this should be working just fine. The only caveat is whether we should be comparing encoded or decoded keys
	# From what i got from eric he seems to think we should compare encoded keys, but i think decoded keys makes more sense

	for item in db.items():
		if item[0].decode(encoding='UTF-8') >= startKey and item[0].decode(encoding='UTF-8') <= endKey:
			values.append(item[1].decode(encoding='UTF-8'))
	return values

## Random and Misc Functions ==============================
def get_random():
	return random.randint(0, 63)
def get_random_char():
	return chr(97 + random.randint(0, 25))

## Main ===================================================
def main():
	global db
	global dbType
	#get args
	dbType = str(sys.argv[1]).lower()
	#perform apporpriate create database statement
	if dbType.lower() == "btree":
		pass
	elif dbType.lower() == "hash":
		pass
	elif dbType.lower() == "indexfile":
		pass
	else:
		print("Invalid argument, please run with one of: btree, hash, indexfile")
		return
	
	answersFile = open('answers','w')
	while(True):
		print("Please Choose from the following options: \n1. Create and populate the database \n2. Retrieve records with a key\n3. Retrieve key with data\n4. Retrieve records with a range of keys\n5. Destroy Database\n6. Quit")
		while(True):
			choice = input("[1/2/3/4/5/6]: ")
			try:
				choice = int(choice)
			except:
				print("Invalid input, please enter an integer between 1 and 5")
				continue
			if choice < 1 or choice > 6:
				print("Invalid input, please enter an integer between 1 and 5")
				continue
			break

		if choice == 1:
			if dbType.lower() == "btree":
				db = createBTree()
			elif dbType.lower() == "hash":
				db = createHashTable()
			elif dbType.lower() == "indexfile":
				db = createIndexFile()
		elif choice == 2:
			startRetrieveWithKey()
		elif choice == 3:
			startRetrieveWithData()
		elif choice == 4:
			startRetrieveWithRange()
		elif choice == 5:
			destroyDatabase()
			
		else:
			break

	destroyDatabase()
	answersFile.close()

if __name__ == "__main__":
	main()
