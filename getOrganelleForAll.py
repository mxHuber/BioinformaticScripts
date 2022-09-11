import os
import sys
import time
import wget
from prettytable import PrettyTable

# example:
# python getOrganelleForAll.py [TXTFILE]

# get starting time of program
program_start_time = time.time()

#
#	get all names and download links from file
#

names = []
readDownloadLinks = []
refGenomeDownloadLinks = []

# check for correct number of arguments
if not len(sys.argv) == 2:
	print("Bad Inputs. Command is: python Pipeline.py [FILE]")
	exit()

# edit this to your working directory
base_path = "/vol/storage/pipeline/"

# data_file = open("names_and_links")
data_file = open(sys.argv[1])

# the format is: name, read download link, reference genome download link, new line
lines = data_file.readlines()

data_file.close()

number_of_lines = len(lines)

for i in range(number_of_lines):
	# name and remove newline character
	if (i % 4 == 0):
		names.append(lines[i][:-1])
	# read download link and remove newline character
	elif (i % 4 == 1):
		readDownloadLinks.append(lines[i][:-1])
	# reference genome download link and remove newline character
	elif (i % 4 == 2):
		refGenomeDownloadLinks.append(lines[i][:-1])
	# (i % 4 == 3) is a new line character, must be skipped

number_of_genomes = len(names)
print("The data file contains " + str(number_of_genomes) + " animal species")

#
#	Run getOrganelle for all species
#

runtime_per_animal = []

for i in range(number_of_genomes):
	# get time at the beginning of this loop
	for_loop_start_time = time.time()
	loop_time = -1

	current_path = base_path + names[i] + "/"

	print("Now working on " + names[i] + "\n")

	# check if general folder and getOrganelle folder already exists. If not, create them
	if not os.path.exists(current_path):
		os.makedirs(current_path)

	if os.path.exists(current_path + "getOrganelle_" + names[i]):
		print("getOrganelle folder for " + names[i] + " already exists, skipping...\n")
		runtime_per_animal.append(loop_time)
		continue

	#
	#	Downloads
	#

	# download read. If read already exists, don't redownload it
	cut_read_download_link_name = readDownloadLinks[i].split('/')
	current_read_name = cut_read_download_link_name[len(cut_read_download_link_name) - 1]
	current_read = "PLACEHOLDER_PATH_READ"

	if os.path.exists(current_path + current_read_name):
		print("Read file found, no need to download it again\n")
		current_read = current_path + current_read_name
	elif os.path.exists(current_path + current_read_name + ".lite.1"):
		print("Read file found, no need to download it again")
		current_read = current_path + current_read_name + ".lite.1"
	elif os.path.exists(current_path + current_read_name + ".sralite.1"):
		print("Read file found, no need to download it again")
		current_read = current_path + current_read_name + ".sralite.1"
	else:
		print("Downloading read file...\n")
		current_read = wget.download(readDownloadLinks[i], out=current_path)

	# wget saves the file with a weird '//' which makes the rest of the script not work
	current_read = current_read.replace("//",'/')

	if(not os.path.exists(current_read)):
		runtime_per_animal.append(loop_time)
		print("File: " + current_read + " not found. Skipping genome")
		continue

	#
	#	preparing reads by converting them to fastq and trimming them
	#

	print("\n\n" + current_read + "\n\n")

	# convert read file to fastq format
	if os.path.exists(current_read + "_1.fastq"):
		print("Read file in .fastq format exists, no need to convert it again")
	elif os.path.exists(current_read[:-7] + "_1.fastq"):
		print("Read file in .fastq format exists, no need to convert it again")
	elif os.path.exists(current_read[:-10] + "_1.fastq"):
		print("Read file in .fastq format exists, no need to convert it again")
	else:
		print("\nConverting read file to fastq format...")
		os.system("/vol/storage/ncbi_sra_tools/sratoolkit.3.0.0-ubuntu64/bin/fasterq-dump  --split-files " + current_read + " --outdir " + current_path)

	# some read files have a ".lite.1" or ".sralite.1" part at the end when downloaded,
	# but (new addendum SOMETIMES) NOT after being converted to fastq
	# I check if these are in the path of the read file and cut off these parts in the variable string if needed
	# Also, it's important to check for ".sralite.1" first. If we check for ".lite.1" first, that could get cut
	# off of a ".sralite.1" file, which would leave an undetected ".sr" which would break the pipeline
	if ".sralite.1" in current_read and not os.path.exists(current_read + "_1.fastq"):
		current_read = current_read[:-10]
	elif ".lite.1" in current_read and not os.path.exists(current_read + "_1.fastq"):
		current_read = current_read[:-7]	

	# zipping .fastq files, if the zipped files don't already exist
	if os.path.exists(current_read + "_1.fastq.gz"):
		print(current_read + "_1.fastq already exists")
	else:
		print("\nGzipping " + current_read + "_1.fastq...")
		os.system("gzip " + current_read + "_1.fastq")

	if os.path.exists(current_read + "_2.fastq.gz"):
		print(current_read + "_2.fastq already exists")
	else:
		print("\nGzipping " + current_read + "_2.fastq...")
		os.system("gzip " + current_read + "_2.fastq")

	if not os.path.exists(current_read + "_1.fastq.gz"):
		runtime_per_animal.append(loop_time)
		print("fastq-dump didn't work. Therefore the neccesary file " + current_read + ".fastq is missing. Skipping genome")
		continue

	# cut adapters and trim low-quality reads
	print("\nTrimming adapters and low-quality reads...\n")
	os.system("java -jar /vol/storage/Trimmomatic-0.39/trimmomatic-0.39.jar PE -threads 8 " + current_read + "_1.fastq.gz " + current_read + "_2.fastq.gz " + current_read + "_paired_1.fastq.gz " + current_read + "_unpaired_1.fastq.gz " + current_read + "_paired_2.fastq.gz " + current_read + "_unpaired_2.fastq.gz " + "SLIDINGWINDOW:4:20 MINLEN:25 ILLUMINACLIP:/vol/storage/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:keepBothReads")
	
	if not os.path.exists(current_read + "_paired_1.fastq.gz"):
		print("Trimmomatic failed. Trying again with argument -phred33...\n")
		os.system("java -jar /vol/storage/Trimmomatic-0.39/trimmomatic-0.39.jar PE -threads 8 -phred33 " + current_read + "_1.fastq.gz " + current_read + "_2.fastq.gz " + current_read + "_paired_1.fastq.gz " + current_read + "_unpaired_1.fastq.gz " + current_read + "_paired_2.fastq.gz " + current_read + "_unpaired_2.fastq.gz " + "SLIDINGWINDOW:4:20 MINLEN:25 ILLUMINACLIP:/vol/storage/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:keepBothReads")
	
	if not os.path.exists(current_read + "_paired_1.fastq.gz"):
		print("Trimmomatic failed. Trying again with argument -phred64...\n")
		os.system("java -jar /vol/storage/Trimmomatic-0.39/trimmomatic-0.39.jar PE -threads 8 -phred64 " + current_read + "_1.fastq.gz " + current_read + "_2.fastq.gz " + current_read + "_paired_1.fastq.gz " + current_read + "_unpaired_1.fastq.gz " + current_read + "_paired_2.fastq.gz " + current_read + "_unpaired_2.fastq.gz " + "SLIDINGWINDOW:4:20 MINLEN:25 ILLUMINACLIP:/vol/storage/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:keepBothReads")

	if not os.path.exists(current_read + "_paired_1.fastq.gz"):
		runtime_per_animal.append(loop_time)
		print("Trimmomatic didn't work!")
		continue

	#
	#	getOrganelle
	#
	
	getOrganelle = "/vol/storage/GetOrganelle-1.7.6.1/get_organelle_from_reads.py"
	first = current_read + "_paired_1.fastq.gz"
	second = current_read + "_paired_2.fastq.gz"
	getOrgDir = current_path + "getOrganelle_" + names[i]
	SPAdesDir = "/vol/storage/SPAdes-3.15.5-Linux/bin/"
	os.system(getOrganelle + " -1 " + first + " -2 " + second + " -o " + getOrgDir + " -F animal_mt -R 10 --memory-save --out-per-round --which-spades " + SPAdesDir)

	os.system("rm " + current_read)
	# The two lines below are here, because some files have ".lite.1" or ".sralite.1" in their name
	# It's not a problem if these files don't exists, because the command will just print out that it didn't work
	os.system("rm " + current_read + ".lite.1")
	os.system("rm " + current_read + ".sralite.1")
	os.system("rm " + current_read + "_1.fastq.gz")
	os.system("rm " + current_read + "_2.fastq.gz")
	os.system("rm " + current_read + "_paired_1.fastq.gz")
	os.system("rm " + current_read + "_paired_2.fastq.gz")
	os.system("rm " + current_read + "_unpaired_1.fastq.gz")
	os.system("rm " + current_read + "_unpaired_2.fastq.gz")

	# calculate runtime of current loop and save it in the corresponding list
	for_loop_end_time = time.time()
	loop_time = for_loop_end_time - for_loop_start_time
	runtime_per_animal.append(loop_time)

program_end_time = time.time()
final_time = program_end_time - program_start_time

print("Program finished! It took " + str(final_time) + " to finish")

time_table = PrettyTable()
# time_table.field_names["Name", "Time"]

for t in range(number_of_genomes):
	time_table.add_row([names[t], str((runtime_per_animal[t] / 60) / 60) + " hours"])

print(time_table)