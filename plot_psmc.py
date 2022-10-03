import sys
from matplotlib import pyplot as plt

# example command: python plot_psmc.py [FILE] -o [OUTPUT_PATH]-n [IMAGE_NAME]

# system arguments
data_path = sys.argv[1]
output_path = sys.argv[3]
file_name = sys.argv[5]
# sys.argv[0] is the command itself

if not output_path[-1:] == "/" and not output_path[:-1] == "\\":
	output_path = output_path + "/"

# option variables

binSize = 100
mutationRate = 2.5e-9
yearsPerGeneration = 10
x_origin = 1e5
y_origin = 0
x_end = 5e7
y_end = 8e5

# read in data from the input file
data_file = open(data_path, "r")
data = data_file.read()
data_file.close()

# extract time windows and lambda values
lastBlock = data.split('//\n')[-2]
lastBlock = lastBlock.split("\n")
times = []
lambdas = []
for i in range(len(lastBlock)):
	current = lastBlock[i]
	if current[:2] == "RS":
		times.append(float(current.split("\t")[2]))
		lambdas.append(float(current.split("\t")[3]))

# extract estimations of theta for computing N0
# "PA" lines contain the values of the estimated parameters
result = data.split("PA\t") 
result = result[-1].split("\n")[0]
result = result.split(" ")
theta = float(result[1])
N0 = theta/(4*mutationRate)/binSize

# scale times and sizes
times = [yearsPerGeneration * 2 * N0 * i for i in times]
sizes = [N0 * i for i in lambdas]

# plot variables
plot = plt.figure()
subPlot = plot.add_subplot(111)
subPlot.set_title("Ptilorrhoa leucosticta")
subPlot.step(times, sizes, where='post', linestyle='-')
subPlot.set_xlabel("Unscaled Generation Time")
subPlot.set_ylabel("Effective size")
subPlot.set_xlim(x_origin, x_end)
subPlot.set_ylim(y_origin, y_end)
subPlot.set_xscale('log')
subPlot.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
subPlot.grid(True)

plot.savefig(output_path + file_name + ".png")
