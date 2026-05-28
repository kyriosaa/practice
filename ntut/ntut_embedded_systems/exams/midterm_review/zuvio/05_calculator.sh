# Script to create a simple calculator
# Shell script

# num input
echo "Enter the first number:"
read num1

echo "Enter the second number:"
read num2

# operation
echo "Enter an arithmetic operation (+, -, *, /):"
read op

case $op in
    +)
        result=$((num1 + num2))
        echo "Result: $num1 + $num2 = $result"
        ;;
    -)
        result=$((num1 - num2))
        echo "Result: $num1 - $num2 = $result"
        ;;
    \*)
        result=$((num1 * num2))
        echo "Result: $num1 * $num2 = $result"
        ;;
    /)
        if [ $num2 -eq 0 ]; then
            echo "Error: Division by zero is not allowed."
            exit 1
        fi
        result=$(echo "scale=2; $num1 / $num2" | bc)
        echo "Result: $num1 / $num2 = $result"
        ;;
    *)
        echo "Error: Invalid operation. Supported operations are +, -, *, /."
        exit 1
        ;;
esac