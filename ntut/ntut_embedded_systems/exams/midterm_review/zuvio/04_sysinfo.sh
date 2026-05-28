# Script that displays the system information
# Shell script

echo "Hostname: $(hostname)"
echo "Operating System: $(uname -o)"
echo "Kernel Version: $(uname -r)"
echo "CPU Model: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')"
echo "Total Memory: $(grep MemTotal /proc/meminfo | awk '{print $2 " " $3}')"