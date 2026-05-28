# Script to list files in a directory
# Shell script

# check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directory path provided. Please provide a relative path."
    exit 1
fi

# check if the provided path is a directory
if [ ! -d "$1" ]; then
    echo "Error: '$1' is not a valid directory."
    exit 1
fi

# list all files in the directory
echo "Files in '$1':"
ls -1 "$1"

# count the total number of files
file_count=$(ls -1 "$1" | wc -l)
echo "Total number of files: $file_count"