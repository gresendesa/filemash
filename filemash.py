import sys
from FileMasher import File

try:
	print(File(file_name=sys.argv[1]).mash())
except Exception as e:
	print("Error: {}".format(e))



