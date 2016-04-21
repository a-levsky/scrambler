#!/usr/bin/python
import re
import os
import sys
import random
import subprocess
from time import sleep

# pattern R>>..endobj as list of hex characters
hide_pattern = ["5", "2", "3", "E", "3", "E", "0", "D", "0", "A", "6", "5", "6", "E", "6", "4", "6", "F", "6", "2", "6", "A"]
key = []

# finds all locations of hide_pattern within a hex dump
# returns list of locations
def findHidePattern(target_hex):
    matches = []
    for i in range(len(target_hex)):
        if target_hex[i] == hide_pattern[0] and target_hex[i:i+len(hide_pattern)] == hide_pattern:
            matches.append(i)
    return matches

# generates a hex dump of a specified file
# returns hex dump as a list of characters
def generateHexDump(file_name):
  # hex generated through subprocess call to xxd bash command
  xxd = "xxd -u -ps -c 10000000000 %s > dump.hex" % file_name
  subprocess.call(xxd, shell=True)
  file = open("dump.hex", "r")
  hex_dump = list(file.read().strip('\n'))
  file.close()
  os.remove("dump.hex")
  sleep(1)
  return hex_dump

# hides each character of hide_hex within a random hide_pattern location of target_hex
# returns updated target_hex list
def hideFile(target_hex, hide_hex):
  for char in hide_hex:
    # update locations of hide_patterns with each iteration
    hide_pattern_locs = findHidePattern(target_hex)
	
	# specify location of space between angle brackets >*> within hide_pattern
    loc = random.choice(hide_pattern_locs) + 4
    loc2 = loc + 1
	
	# update all key locations preceded by new key location
    for val in key:
       if loc < val:
         key[key.index(val)] = val + 2
    key.append(loc)
    
    target_hex.insert(loc, char)
    target_hex.insert(loc2, "0")
    print "Characters hidden:", target_hex[loc] + target_hex[loc2]
	
  return target_hex

# creates a key file out of locations listed in key list
def createKeyFile(key, target_file):
  key_file_name = target_file + ".key"
  key_file = open(key_file_name, "w+")
  for loc in key:
    key_file.write("%d\n" % loc)
  key_file.close()

# creates a key location list out of values in the key file
# returns key_list of key locations
def createKeyList(key_file):
  key_list = []  
  with open(key_file) as fp:
    for loc in fp:
	  key_list.append(loc.strip("\n"))
  return key_list

# restore file by compiling list of hex values
def restoreFile(target_hex, target_file):
  restored_file = open("target.hex", "w+")
  # turn list of hex values into single string
  restored_file.write("%s" % ''.join(target_hex))
  restored_file.close()
  xxd = "xxd -r -p target.hex " + target_file
  # subprocess call to xxd command for file recompilation
  subprocess.call(xxd, shell = True)
  os.remove("target.hex")

# retrieves characters from hex dump at locations specified by values in key list
def retrieveHidden(source_hex, key_list):
  hidden_text = ""  
  for val in key_list:
    hidden_text = hidden_text + source_hex[int(val)]
  # creates a file
  echo = "echo -n %s > hextest123.hex" % hidden_text
  xxd = "xxd -r -p hextest123.hex"
  subprocess.call(echo, shell = True)
  subprocess.call(xxd, shell = True)
  print("\n")
  os.remove("hextest123.hex")

# scrambles secret text and hides it in pdf
def scramble(target_file, hide_file):
  print "Generating hex dump of target file\n"
  target_hex = generateHexDump(target_file)
  
  print "Generating hex dump of hide file\n"
  hide_hex = generateHexDump(hide_file)
  
  print "Hiding file\n"
  target_hex = hideFile(target_hex, hide_hex)
  
  print "\nCreating key file\n"
  createKeyFile(key, target_file)
  
  print "Restoring file\n"
  restoreFile(target_hex, target_file)

# retrieves hidden message from pdf hex
def unscramble(source_file, key_file):
  print "Generating hex dump of pdf file\n"
  source_hex = generateHexDump(source_file)

  print "Generating key list\n"
  key_list = createKeyList(key_file)

  print "Retrieved hidden message:\n"
  retrieveHidden(source_hex, key_list)

# proceed with script based on command line file input
if __name__ == '__main__':
  if(len(sys.argv) != 3):
    print "invalid number of arguments"
    sys.exit()
	
  else:
    file1 = sys.argv[1]
    file2 = sys.argv[2]
	
    if(((".key" in file1) or (".key" in file2))):
      if((".key" in file1)):
        key_file = file1
        source_file = file2
      else:
        key_file = file2
        source_file = file1
      unscramble(source_file, key_file)
	  
    elif(((".key" not in file1) and (".key" not in file2))):
      scramble(file1, file2)