#!/usr/bin/python

# Arseny Moguilevski

#import re
import os
import sys
import random
from time import sleep

# pattern R>>..endobj as list of hex characters, make hide_pattern whatever hex pattern you want to hide data in
hide_pattern = ['5', '2', '3', 'e', '3', 'e', '0', 'd', '0', 'a', '6', '5', '6', 'e', '6', '4', '6', 'f', '6', '2', '6', 'a']
key = []
offset = 4
ascii_char = 2

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
  file = open(file_name, "r")
  file_contents = file.read()
  hex_dump = list(file_contents.encode('hex'))
  file.close()
  sleep(1)
  return hex_dump

# hides each character of hide_hex within a random hide_pattern location of target_hex
# returns updated target_hex list
def hideFile(target_hex, hide_hex):
  # find all locations of hide_pattern within the target_hex
  hide_pattern_locs = findHidePattern(target_hex)
   
  for char in hide_hex:
    # specify location of space between angle brackets >*> within hide_pattern
    selection = random.choice(hide_pattern_locs)
	
    loc = selection + offset
    loc2 = loc + 1
	
    # update all hide_pattern_locs preceded by current loc
    for val in hide_pattern_locs:
      if loc <= val:
        hide_pattern_locs[hide_pattern_locs.index(val)] = val + ascii_char
		
    # update all key locations preceded by new key location	
    for val in key:
       if loc <= val:
         key[key.index(val)] = val + ascii_char
		
    target_hex.insert(loc, char)
    target_hex.insert(loc2, "0")
	
    # add location of hidden character to key list
    key.append(loc)
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

# restores file by compiling list of hex values
def restoreFile(target_hex, target_file):
  restored_file = open(target_file, "w+")
  # turns list of hex values into single string
  restored_file.write("%s" % ''.join(target_hex).decode("hex"))
  restored_file.close()
  
# retrieves characters from hex dump at locations specified by values in key list
def retrieveHidden(source_hex, key_list):
  hidden_text = ""  
  # locates hex characters within PDF
  for val in key_list:
    hidden_text = hidden_text + source_hex[int(val)]
  # creates a file and decodes the hidden text back into ascii
  hidden_file = open("hidden_file", "w+")
  hidden_file.write("%s" % ''.join(hidden_text).decode("hex"))
  hidden_file.close()

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

  print "Retrieved hidden file"
  retrieveHidden(source_hex, key_list)

# proceed with script based on command line file input
if __name__ == '__main__':
  if(len(sys.argv) != 3):
    print "invalid number of arguments"
    sys.exit()
	
  else:
    file1 = sys.argv[1]
    file2 = sys.argv[2]
	
    if((".key" in file1) or (".key" in file2)):
      if ".key" in file1:
        key_file = file1
        source_file = file2
      else:
        key_file = file2
        source_file = file1
      unscramble(source_file, key_file)
	  
    elif((".key" not in file1) and (".key" not in file2)):
      scramble(file1, file2)
