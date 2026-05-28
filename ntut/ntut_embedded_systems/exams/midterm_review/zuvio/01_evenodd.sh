# Script to check if a number is even or odd
# Shell script

# prompt the user to input an integer
echo "Enter an integer:"
read number

# check if the number is even or odd
if (( number % 2 == 0 )); then
    echo "$number is even"
else
    echo "$number is odd"
fi