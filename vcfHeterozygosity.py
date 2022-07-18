import os
import sys
import time
from os.path import exists

# get starting time of program 
program_start_time = time.time()

# checks if everything is as it should be
if not len(sys.argv) == 2:
	print("Please provide the path to the .vcf file")
	exit()

if exists("new_VCF_filtered_het.vcf"):
	print("A filtered .vcf file already exists, move it so it doesn't get overwritten")
	exit()

# .vcf file path
file_path = sys.argv[1]
# sys.argv[0] is the command itself

# get number of lines
print("Determining number of lines\n")
numberOfLines = 0

#while current_line_for_length:
#	numberOfLines = numberOfLines + 1
#	current_line_for_length = data_file_lines.readline()

before = time.time()
numberOfLines = sum(1 for line in open(file_path, 'r'))

print("Found " + str(numberOfLines) + " lines. It took " + str(time.time() - before) + " to determine that")

# i'm dividing by numberOfLines later on, so make sure it's not equal to 0. Also, if it's 0, that's not good too, so exit there
if numberOfLines < 1:
	print("number of lines equal to 0. Something went wrong")
	exit()

# we now have to extract the neccesary information from the .vcf file
# we need all the 0/1 and 1/2's in the bwa.sorted.bam column, but not the 0/0 and 1/1's

print("Extracting neccesary information from .vcf ...\n")
data_file = open(file_path, 'r')

# new file that we will save all relevant data into
results_file = open("new_VCF_filtered_het.vcf", 'w')

current_line = data_file.readline()

# search for beginning of data. Also, save lines into new file, we need those lines in there (i think)
while current_line:
	if current_line == "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	bwa.sorted.bam\n":
		print("Found beginning of data")
		results_file.write(current_line)
		# read next line, which is first actual data line
		current_line = data_file.readline()
		break;

	results_file.write(current_line)
	current_line = data_file.readline()

numberOfZeroOnes = 0
numberOfOneTwos = 0
counter = 1
next_time = time.time() + 60

print("Extracting 0/1 and 1/2 chromosomes...")
# check if current line is relevant. If that is the case, save it into another file
while current_line:
	# progress report
	counter = counter + 1
	if time.time() > next_time:
		next_time = next_time + 60
		print("Went over " + str(counter/numberOfLines) + "% of lines")
	
	# we are only interested in the characters before the last ':'
	split_line = current_line.split(':')
	interesting_part = split_line[len(split_line) - 2]
	interesting_part = interesting_part[-3:]
	if interesting_part == "0/1":
		results_file.write(current_line)
		numberOfZeroOnes = numberOfZeroOnes + 1
	elif interesting_part == "1/2":
		results_file.write(current_line)
		numberOfOneTwos = numberOfOneTwos + 1

	current_line = data_file.readline()

data_file.close()
results_file.close()

print("There were " + str(numberOfZeroOnes) + " 0/1's and " + str(numberOfOneTwos) + " 1/2's")

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time) + " seconds to complete. (" + str(run_time / 60) + " minutes")