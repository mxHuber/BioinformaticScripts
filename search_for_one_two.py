import os
import sys
import time
from os.path import exists

# get starting time of program 
program_start_time = time.time()

# checks if everything is as it should be
if not len(sys.argv) == 2:
	print("Bad input. Command is: python get_het_vcf.py [FILE_PATH]")
	exit()

# .vcf file path
file_path = sys.argv[1]
# sys.argv[0] is the command itself

# if needed, unzip .vcf file and remember to rezip it at the end
wasZipped = False
if file_path[-3:] == ".gz":
	wasZipped = True
	print("Unzipping .vcf file...")
	os.system("gunzip " + file_path)
	file_path = file_path[:-3]

# we now have to extract the neccesary information from the .vcf file
# we search every line for "1/2"
data_file = open(file_path, 'r')

current_line = data_file.readline()
line_number = 1
found_beginning_of_data = False

# search for beginning of data
while current_line:
	line_number = line_number + 1

	if current_line.split("\t")[0] == "#CHROM":
		print("Found beginning of data")
		# read next line, which is first actual data line
		current_line = data_file.readline()
		found_beginning_of_data = True
		break;

	current_line = data_file.readline()

if not found_beginning_of_data:
	print("Beginning of data wasn't found, exiting...")
	exit()

# check if current line contains "1/2"
while current_line:
	line_number = line_number + 1

	if "1/2" in current_line:
		print("Found 1/2 in line: " + line_number)
		print(current_line)

	current_line = data_file.readline()

data_file.close()

if wasZipped:
	print("Rezipping .vcf file")
	os.system("gzip " + file_path)

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time) + " seconds to complete. (" + str(run_time / 60) + " minutes")