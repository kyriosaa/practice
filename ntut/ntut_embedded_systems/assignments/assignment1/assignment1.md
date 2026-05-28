# 1) simple hello world script
```
1_hello_world() {
    echo "Hello World!"
}
```

# 2) summation two integers
```
2_sum_integers() {
    read -p "Enter first integer: " num1
    read -p "Enter second integer: " num2
    sum=$((num1 + num2))
    echo "Sum: $sum"
}
```

# 3) summation using basic calculator command
```
3_sum_real() {
    read -p "Enter first real number: " num1
    read -p "Enter second real number: " num2
    sum=$(echo "$num1 + $num2" | bc)
    echo "Sum: $sum"
}
```

# 4) find biggest num
```
4_biggest_of_three() {
    read -p "Enter first number: " num1
    read -p "Enter second number: " num2
    read -p "Enter third number: " num3
    
    biggest=$num1
    if (( $(echo "$num2 > $biggest" | bc -l) )); then
        biggest=$num2
    fi
    if (( $(echo "$num3 > $biggest" | bc -l) )); then
        biggest=$num3
    fi
    echo "Biggest number: $biggest"
}
```

# 5) math operations on two nums
```
5_operations() {
    read -p "Enter first number: " num1
    read -p "Enter second number: " num2
    
    sum=$(echo "$num1 + $num2" | bc)
    diff=$(echo "$num1 - $num2" | bc)
    prod=$(echo "$num1 * $num2" | bc)
    
    if (( $(echo "$num2 == 0" | bc -l) )); then
        echo "Addition: $sum"
        echo "Subtraction: $diff"
        echo "Multiplication: $prod"
        echo "Division: Cannot divide by zero"
    else
        quot=$(echo "scale=2; $num1 / $num2" | bc)
        echo "Addition: $sum"
        echo "Subtraction: $diff"
        echo "Multiplication: $prod"
        echo "Division: $quot"
    fi
}
```

# 6) reverse num
```
6_reverse_number() {
    read -p "Enter a number: " num
    reversed=0
    temp=$num
    
    while [ $temp -gt 0 ]; do
        remainder=$((temp % 10))
        reversed=$((reversed * 10 + remainder))
        temp=$((temp / 10))
    done
    
    echo "Reversed number: $reversed"
}
```

# 7) sort five numbers using array
```
7_sort_five() {
    echo "Enter five numbers:"
    read -p "Number 1: " arr[0]
    read -p "Number 2: " arr[1]
    read -p "Number 3: " arr[2]
    read -p "Number 4: " arr[3]
    read -p "Number 5: " arr[4]
    
    for ((i=0; i<5; i++)); do
        for ((j=0; j<5-i-1; j++)); do
            if (( $(echo "${arr[j]} > ${arr[j+1]}" | bc -l) )); then
                temp=${arr[j]}
                arr[j]=${arr[j+1]}
                arr[j+1]=$temp
            fi
        done
    done
    
    echo "Sorted numbers: ${arr[@]}"
}
```

# 8) calc average numbers on command line arguments
```
8_calculate_average() {
    if [ $# -eq 0 ]; then
        echo "No numbers provided. Usage: Pass numbers as arguments"
        return
    fi
    
    sum=0
    count=$#
    
    for num in "$@"; do
        sum=$(echo "$sum + $num" | bc)
    done
    
    avg=$(echo "scale=2; $sum / $count" | bc)
    echo "Average of $count numbers: $avg"
}
```

# 9) factorial
```
9_factorial() {
    read -p "Enter a number: " num
    
    if [ $num -lt 0 ]; then
        echo "Factorial is not defined for negative numbers"
        return
    fi
    
    fact=1
    for ((i=1; i<=num; i++)); do
        fact=$((fact * i))
    done
    
    echo "Factorial of $num: $fact"
}
```

```
echo "========================================="
echo "       Function Scripts Assignment"
echo "             ID: 114998411"
echo "========================================="
echo "1. Hello World"
echo "2. Sum of two integers"
echo "3. Sum of two real numbers"
echo "4. Find biggest of 3 numbers"
echo "5. Operations on two numbers"
echo "6. Reverse a number"
echo "7. Sort five numbers"
echo "8. Calculate average of numbers"
echo "9. Calculate factorial"
echo "========================================="
read -p "Enter your choice (1-9): " choice

case $choice in
    1)
        1_hello_world
        ;;
    2)
        2_sum_integers
        ;;
    3)
        3_sum_real
        ;;
    4)
        4_biggest_of_three
        ;;
    5)
        5_operations
        ;;
    6)
        6_reverse_number
        ;;
    7)
        7_sort_five
        ;;
    8)
        echo "Enter numbers separated by spaces:"
        read -a numbers
        8_calculate_average "${numbers[@]}"
        ;;
    9)
        9_factorial
        ;;
    *)
        echo "Invalid... Please select 1-9."
        ;;
esac
```