'''
    File name: filemash.py
    Version: 0.2
    Author: Guilherme Sá
    Email: gresendesa@gmail.com
    Date created: 2/22/2017
    Date last modified: 27/11/2019
    Python Version: 3.6 
'''
import os
import re
import string

class File:
  def __init__(self, file_name):
    token_open = '{%'
    token_close = '%}'
    self.file_name = file_name
    self.CONNECTION_PATTERN = '{} *["\']([^"\']+)["\'] *{}'.format(token_open, token_close)
    self.DEPENDENCY_BRANCH = []

  def file_exists(self, file_path):
    """
      Checks if the especified file exists (Boolean)
    """
    if os.path.exists(file_path):
      return True
    else:
      return False

  def get_root_dir(self):
    """
      It gets a root directory from the program argument
    """
    root_dir = ''
    if len(self.file_name) > 1 and len(os.path.dirname(self.file_name)) > 0:
      root_dir = os.path.dirname(self.file_name) + os.sep
    return root_dir


  def is_connection(self, line):
    """
      Checks if the passed text maches to a connection sintax (Boolean)
    """
    if re.match('^.*' + self.CONNECTION_PATTERN, line):
      return True
    else:
      return False

  def get_connection_param(self, connection):
    """
      Gets a string connection and extracts its parameter and interprets it as a relative path
    """
    return os.path.normpath(re.search(self.CONNECTION_PATTERN, connection).group(1))
    #return re.search(self.CONNECTION_PATTERN, re.sub(' +', ' ', connection.strip())).group(0).strip().replace('"', '').replace("'", '').split(self.CONNECTION_COM)[1].strip()

  def get_branch_path(self, deep = None):
    """
      It gets a path and bind the defined root dir
    """
    path = self.get_root_dir()
    if deep == None:
      deep = len(self.DEPENDENCY_BRANCH)
    for i in range(0, deep):
      if len(os.path.dirname(self.DEPENDENCY_BRANCH[i])) > 0:
        path += os.path.dirname(self.DEPENDENCY_BRANCH[i]) + os.sep
    return path

  def get_basename(self, path):
    """
      Works exactly how the name sugests ;)
    """
    return os.path.basename(path)


  def append_branch_path(self, path, just_basename = True):
    """
      It appends the brach 
    """
    if just_basename:
      return os.path.normpath(os.path.join(self.get_branch_path(), os.path.basename(path)))
    else:
      return os.path.normpath(os.path.join(self.get_branch_path(), path))



  def get_processed_line(self, line):
    """
      Process a line. 
      If the line is a connection it returns the linked file. 
      Else it returns the same input.
    """
    if self.is_connection(line):
      f=self.append_branch_path(self.get_connection_param(line), False)
      if self.file_exists(f) and not(self.is_connection_circular(line)):
        snippet = re.search(self.CONNECTION_PATTERN, line).group(0)
        return line.replace(snippet, self.compose(self.get_connection_param(line)))
      else:
        return None
    else:
      return line

  def get_parent_file_path(self, connection):
    """
      Returns the previous position of passed connection on tree dependency
    """
    path_pos_connection = self.DEPENDENCY_BRANCH.index(self.get_connection_param(connection))
    if path_pos_connection > 0:
      return os.path.normpath(os.path.join(self.get_branch_path(path_pos_connection - 1), self.get_basename(self.DEPENDENCY_BRANCH[path_pos_connection - 1])))
    else:
      return "the main input"

  def raise_exception(self, file_name, line_number, message):
    """
      Shows a message error in the default way
    """
    raise Exception ("Error: {} ({}, on line {})".format(message, os.path.normpath(file_name), line_number))

  def handle_error(self, file_name, line_number, connection):
    """
      Finds out the type error
    """
    if self.is_connection_circular(connection):
      self.raise_exception(file_name, line_number, "Circular connection to {} defined previously at {}".format(self.append_branch_path(self.get_connection_param(connection), False), self.get_parent_file_path(connection)))
    if self.file_exists(self.append_branch_path(self.get_connection_param(connection), False)):
      self.raise_exception(file_name, line_number, "Dependency not satisfied")
    else:
      self.raise_exception(file_name, line_number, "File \"{}\" not found".format(self.append_branch_path(self.get_connection_param(connection), False)))

  def concat(self, str_a, str_b):
    """
      Returns pair of string concatenation or returns none if any of them is None
    """
    if str_a != None and str_b != None:
      return str_a + str_b
    else:
      result = None
    return result

  def build_file(self, file_path):
    """
      Brings together all linked files
    """
    with open(self.append_branch_path(file_path), 'r', encoding = 'cp1252' if os.name == 'nt' else 'utf-8') as file:
      built_file = ''
      line_counter = 0
      for line in file:
        line_counter += 1
        built_file = self.concat(built_file, self.get_processed_line(line))
        if built_file == None:
          self.handle_error(self.append_branch_path(file_path), line_counter, line)
          break
    return built_file

  def is_connection_circular(self, connection):
    """
      It checks if a connection is already taken along the dependency branch. It avoids infinite loops.
    """
    if self.get_connection_param(connection) in self.DEPENDENCY_BRANCH:
      return True
    else:
      return False

  def compose(self, file_path):
    """
      It composes the set of files implementing registering of instances to avoid circular connections
    """
    self.DEPENDENCY_BRANCH.append(file_path)
    composing = self.build_file(file_path)
    self.DEPENDENCY_BRANCH.pop()
    if composing != None:
      return composing.strip('\n')
    else:
      return None

  def mash(self):
    return self.compose(os.path.basename(self.file_name))