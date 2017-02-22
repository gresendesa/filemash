'''
    File name: filemash.py
    Version: 0.1
    Author: Guilherme Sá
    Email: gresendesa@gmail.com
    Date created: 2/22/2017
    Date last modified: 2/22/2017
    Python Version: 3.6	
'''

import sys
import os
import re
import string

CONNECTION_COM = '@@connection'
CONNECTION_PATTERN = '^( +)?' + CONNECTION_COM + ' ( +)?.*$'
DEPENDENCY_BRANCH = []
if len(sys.argv) > 1:
	ROOT_DIR = os.path.dirname(sys.argv[1])

def file_exists(file_path):
	"""
		Checks if the especified file exists (Boolean)
	"""
	if os.path.exists(file_path):
		return True
	else:
		return False

def is_connection(line):
	"""
		Checks if the passed text maches to a connection sintax (Boolean)
	"""
	if re.match(CONNECTION_PATTERN, line):
		return True
	else:
		return False

def get_connection_param(connection):
	"""
		Gets a string connection and extracts its parameter and interprets it as a relative path
	"""
	return re.sub(' +', ' ', connection.strip()).split(CONNECTION_COM)[1].strip()

def get_branch_path(deep = None):
	"""
		It gets a path and bind the defined root dir
	"""
	path = ROOT_DIR + '/'
	if deep == None:
		deep = len(DEPENDENCY_BRANCH)
	for i in range(0, deep):
		if len(os.path.dirname(DEPENDENCY_BRANCH[i])) > 0:
			path += os.path.dirname(DEPENDENCY_BRANCH[i]) + '/'
	return path

def get_basename(path):
	"""
		Works exactly how the name sugests ;)
	"""
	return os.path.basename(path)


def append_branch_path(path, just_basename = True):
	"""
		It appends the brach 
	"""
	if just_basename:
		return os.path.normpath(get_branch_path() + os.path.basename(path))
	else:
		return os.path.normpath(get_branch_path() + path)



def get_processed_line(line):
	"""
		Process a line. 
		If the line is a connection it returns the linked file. 
		Else it returns the same input.
	"""
	if is_connection(line):
		if file_exists(append_branch_path(get_connection_param(line), False)) and not(is_connection_circular(line)):
			return compose(get_connection_param(line))
		else:
			return None
	else:
		return line

def get_parent_file_path(connection):
	"""
		Returns the previous position of passed connection on tree dependency
	"""
	path_pos_connection = DEPENDENCY_BRANCH.index(get_connection_param(connection))
	if path_pos_connection > 0:
		return os.path.normpath(get_branch_path(path_pos_connection - 1) + get_basename(DEPENDENCY_BRANCH[path_pos_connection - 1]))
	else:
		return "the main input"

def show_log_error(file_name, line_number, message):
	"""
		Shows a message error in the default way
	"""
	print("Error: {} ({}, on line {})".format(message, os.path.normpath(file_name), line_number))

def handle_error(file_name, line_number, connection):
	"""
		Finds out the type error
	"""
	if is_connection_circular(connection):
		show_log_error(file_name, line_number, "Circular connection to {} defined previously at {}".format(append_branch_path(get_connection_param(connection), False), get_parent_file_path(connection)))
	if file_exists(append_branch_path(get_connection_param(connection), False)):
		show_log_error(file_name, line_number, "Dependency not satisfied")
	else:
		show_log_error(file_name, line_number, "File \"{}\" not found".format(append_branch_path(get_connection_param(connection), False)))

def concat(str_a, str_b):
	"""
		Returns pair of string concatenation or returns none if any of them is None
	"""
	if str_a != None and str_b != None:
		return str_a + str_b
	else:
		result = None
	return result

def build_file(file_path):
	"""
		Brings together all linked files
	"""
	with open(append_branch_path(file_path), 'r') as file:
		built_file = ''
		line_counter = 0
		for line in file:
			line_counter += 1
			built_file = concat(built_file, get_processed_line(line))
			if built_file == None:
				handle_error(append_branch_path(file_path), line_counter, line)
				break
	return built_file

def is_connection_circular(connection):
	"""
		It checks if a connection is already taken along the dependency branch. It avoids infinite loops.
	"""
	if get_connection_param(connection) in DEPENDENCY_BRANCH:
		return True
	else:
		return False

def compose(file_path):
	"""
		It composes the set of files implementing registering of instances to avoid circular connections
	"""
	DEPENDENCY_BRANCH.append(file_path)
	composing = build_file(file_path)
	DEPENDENCY_BRANCH.pop()
	return composing

def main_controller():
	"""
		It handles input program
	"""
	if len(sys.argv) > 1 and file_exists(sys.argv[1]):
		print(compose(os.path.basename(sys.argv[1])))
	else:
		print("Invalid argument")

main_controller()
