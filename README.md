# scrambler
Python script for hiding files inside PDFs without corrupting the PDF or altering its formatting

Updated version of script is much more efficient and allows for hiding of much larger files
Double updated version now does all hex encoding/decoding within script without any subprocess calls to xxd in bash

Instructions:
Pass either a PDF and another file to hide the file within the PDF
OR
Pass a PDF with hidden contents and its key file to retrieve the hidden data

Default version of script looks for hex patterns matching 'R>>..endobj' within the PDF and hides hex values between the
angle brackets. This position is specified by the default offset of 4: R>*>

The pattern being searched for and the offset are defined at the beginning of the script and can be changed freely
