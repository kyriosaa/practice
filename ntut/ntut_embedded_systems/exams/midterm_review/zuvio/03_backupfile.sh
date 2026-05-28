# Script to create a backup of a file
# Shell script

# check if a filename is provided as an argument
if [ $# -eq 0 ]; then
    echo "Error: No filename provided. Please provide a filename as an argument."
    exit 1
fi

# check if the file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' does not exist."
    exit 1
fi

# create a backup with .bak extension
cp "$1" "$1.bak"

# display success message
echo "Backup created successfully: $1.bak"