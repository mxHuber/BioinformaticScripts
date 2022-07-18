import os
import sys
import time

# get starting time of program 
program_start_time = time.time()

# example:
# python split_vcf_into_chromosomes.py /vol/storage/prmd/secondTry/output.vcf -o /vol/storage/prmd/secondTry/chromosome_vcfs/

if not len(sys.argv) == 4:
	print("Bad Inputs. Command is: split_vcf_into_chromosomes.py [VCF_FILE] -o [OUTPUT_DIRECTORY]")
	exit()

# path of .vcf
file_path = sys.argv[1]
# output directory
output_dir = sys.argv[3]
# sys.argv[0] is the command itself

# just incase someone (me) gives a bad output path
if not output_dir[len(output_dir) - 1] == "/" and not output_dir[len(output_dir) - 1] == "\\":
	output_dir = output_dir + '/'

data_file = open(file_path, 'r')
current_line = data_file.readline()
meta_info = current_line
found_beginning_of_data = False

# search for beginning of data. Also, save meta information
while current_line:
	if current_line[0:6] == "#CHROM":
		print("Found beginning of data")
		# read next line, which is first actual data line
		current_line = data_file.readline()
		found_beginning_of_data = True
		break;
	
	current_line = data_file.readline()

if not found_beginning_of_data:
	print("Something went wrong. Beginning of data wasn't able to be found")
	data_file.close()
	exit()

# check if output folder exists. If not, create folder
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

# go over given vcf and extract chromosome lines in seperate files
while current_line:
	current_chr = current_line.split("\t")[0]
	print("Now working on: " + current_chr)
	chr_file_path = output_dir + current_chr + ".vcf"
	
	# create new vcf file 
	os.system("touch " + output_dir + current_chr + ".vcf")
	chr_file = open(chr_file_path, 'w')
	# add meta information at the beginning of the file
	chr_file.write(meta_info)

	# find all chromosome lines and put them in their respective file
	while current_line and current_chr == current_line.split("\t")[0]:
		chr_file.write(current_line)
		data_file.readline()

	chr_file.close()

# don't forget to close the data file
data_file.close()

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time) + " seconds to complete. (" + str((run_time / 60) /60) + " hours")
