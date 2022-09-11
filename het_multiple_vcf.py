import os
import sys
import time

# get starting time of program
program_start_time = time.time()

# check for correct number of arguments
if not len(sys.argv) == 2:
	print("Bad Inputs. Command is: python Pipeline.py [FILE]")
	exit()

current_path = "/vol/storage/ba/scripts/"

data_file = open(sys.argv[1])

# the format is: name, read download link, reference genome download link, new line
lines = data_file.readlines()

data_file.close()

names = []

number_of_lines = len(lines)

# get all the names and corresponding download links
for i in range(number_of_lines):
	# name and remove newline character
	if (i % 4 == 0):
		names.append(lines[i][:-1])

for i in range(len(names)):
	print("Now working on: " + names[i])	
	if not os.path.exists("/vol/storage/pipeline/" + names[i] + "/mito/" + names[i] + ".hetinfo"):
		os.system("python " + current_path + "get_het_vcf.py /vol/storage/pipeline/" + names[i] + "/standard_vcf/output.vcf.gz -o /vol/storage/pipeline/" + names[i] + "/mito/" + " -n " + names[i])

print("Finished! It took " + str((time.time() - program_start_time) / 3600) + " hours to complete")
