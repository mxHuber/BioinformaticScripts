import os
import sys
import time
from os.path import exists

# get starting time of program 
program_start_time = time.time()

# checks if everything is as it should be
if not len(sys.argv) == 6:
	print("Bad input. Command is: python get_het_vcf.py [FILE_PATH] -o [OUTPUT_PATH] -n [NAME_FOR_FILE]")
	exit()

# .vcf file path
file_path = sys.argv[1]
output_path = sys.argv[3]
file_name = sys.argv[5]
# sys.argv[0] is the command itself

# if needed, unzip .vcf file and remember to rezip it at the end
wasZipped = False
if file_path[-3:] == ".gz":
	wasZipped = True
	print("Unzipping .vcf file...")
	os.system("gunzip " + file_path)
	file_path = file_path[:-3]

# we now have to extract the neccesary information from the .vcf file
# we need all the 0/1 and 1/2's in the bwa.sorted.bam column, but not the 0/0 and 1/1's
data_file = open(file_path, 'r')

current_line = data_file.readline()
found_beginning_of_data = False

# search for beginning of data
while current_line:
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

numberOfZeroOnes = 0
numberOfOneTwos = 0
numberOfPositions = 0

split_tab = current_line.split('\t')
current_chr_name = split_tab[0]
all_chr_names = [ current_chr_name ]
current_results = [ 0, 0, 0 ]
end_results = []

# check if current line is relevant. If that is the case, save it into another file
while current_line:
	numberOfPositions = numberOfPositions + 1

	split_tab = current_line.split('\t')
	chr_name = split_tab[0]

	if not chr_name == current_chr_name:
		end_results.append(current_results)
		current_chr_name = chr_name
		all_chr_names.append(chr_name)
		current_results = [ 0, 0, 0 ]

	# we are only interested in the characters before the last ':'
	split_line = current_line.split(':')
	interesting_part = split_line[len(split_line) - 2]
	interesting_part = interesting_part[-3:]
	if interesting_part == "0/1":
		current_results[1] = current_results[1] + 1
		numberOfZeroOnes = numberOfZeroOnes + 1
	elif interesting_part == "1/2":
		current_results[2] = current_results[2] + 1
		numberOfOneTwos = numberOfOneTwos + 1
	else:
		current_results[0] = current_results[0] + 1

	current_line = data_file.readline()

	if not current_line:
		end_results.append(current_results)

data_file.close()

if wasZipped:
	print("Rezipping .vcf file")
	os.system("gzip " + file_path)

# new file that we will save all relevant data into
results_file = open(output_path + file_name + ".hetinfo", 'w')
results_file.write("Information about heterozygosity\n")
results_file.write("Arguments read as:\n")
results_file.write("File path: " + file_path + "\n")
results_file.write("Output path: " + output_path + "\n")
results_file.write("File name: " + file_name + "\n")
results_file.write("\n")
results_file.write("Number of all positions:          " + str(numberOfPositions) + "\n")
results_file.write("Number of 0/1 positions:          " + str(numberOfZeroOnes) + "\n")
results_file.write("Number of 1/2 positions:          " + str(numberOfOneTwos) + "\n")
results_file.write("Number of heterozygote positions: " + str(numberOfZeroOnes + numberOfOneTwos) + "\n")
results_file.write("Number of positions in general:   " + str(numberOfPositions) + "\n")
results_file.write("Percentage of 0/1 positions:      " + str((numberOfZeroOnes / numberOfPositions) * 100) + "%\n")
results_file.write("Percentage of 1/2 positions:      " + str((numberOfOneTwos / numberOfPositions) * 100) + "%\n")
results_file.write("Percentage of both positions:     " + str(((numberOfZeroOnes + numberOfOneTwos) / numberOfPositions) * 100) + "%\n")
results_file.write("Chromosome	0/1	1/2	other\n")

for i in range(len(all_chr_names)):
	results_file.write(all_chr_names[i] + "\t" + str((end_results[i])[1]) + "\t" + str((end_results[i])[2]) + "\t" + str((end_results[i])[0]) + "\n")

results_file.close()

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time) + " seconds to complete. (" + str(run_time / 60) + " minutes")
print("Please look at the .hetinfo file for the results")