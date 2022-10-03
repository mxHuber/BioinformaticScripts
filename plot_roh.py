import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os

# checks if everything is as it should be
if not len(sys.argv) == 6:
	print("Bad input. Command is: python plot_roh.py [FILE_PATH] -o [OUTPUT_PATH] -n [NAME_FOR_FILE]")
	exit()

# .vcf file path
file_path = sys.argv[1]
output_path = sys.argv[3]
file_name = sys.argv[5]
# sys.argv[0] is the command itself

data_file = open(file_path, 'r')
current_line = data_file.readline()

found_beginning = False

# find beginning of data
while current_line:
	if not current_line[0] == '#':
		print("Found beginning of data")
		found_beginning = True
		break

	current_line = data_file.readline()

if not found_beginning:
	print("Beginning of data couldn't be found. Exiting...")
	data_file.close()
	exit()

results = [ 0 , 0 , 0 , 0]
lines = 1

# extract relevant data
while current_line:
	splitted = current_line.split("\t")
	if splitted[0] == "RG":
		size = int(splitted[5])
		
		if size < 50000:
			results[0] = results[0] + 1
		elif size < 100000:
			results[1] = results[1] + 1
		elif size < 300000:
			results[2] = results[2] + 1
		else:
			results[3] = results[3] + 1

	current_line = data_file.readline()
	lines = lines + 1

data_file.close()

# set seaborn default theme
sns.set_theme()

# plot stuff
bars = ("<50kb", "<100kb", "<300kb", ">300kb")
y_pos = np.arange(len(bars))
plt.bar(y_pos, results)
plt.xticks(y_pos, bars)
plt.savefig(output_path + file_name + ".png")

#plot = plt.figure(figsize=(10, 8))
#subPlt = plot.add_subplot(111)
#subPlt.bar(results[0], results[1], results[2], results[3])
#subPlt.set_xticks(["<200kb", "<500kb", "<1mb", ">1mb"])
#subPlt.ylabel("Number of positions")
#subPlot.savefig(output_path + file_name + ".png")
