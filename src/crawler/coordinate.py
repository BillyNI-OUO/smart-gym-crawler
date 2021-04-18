from src import constants
import re
import sys
def get_coordinate(filepath):
	try:
		coordinate_list = []
		with open(filepath, 'r') as fp:
			lines = fp.readlines()
			for line in lines:
				line = re.split(r'[,|\s]+', line)
				line = list(map(float, line[:-1]))
				coordinate_set = ((min(line[0], line[2]),max(line[0], line[2])), (min(line[1], line[3]),max(line[1], line[3])))
				coordinate_list.append(coordinate_set)
		return coordinate_list
	except Exception as e:
		sys.stderr.write(str(e)+'\n')