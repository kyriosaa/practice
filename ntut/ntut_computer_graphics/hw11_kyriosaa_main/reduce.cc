//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 9/29/2021
//Purpose: This function will reduce fractions that are entered into it
//Change History: 

#include <stdio.h>

int find_gcd(int m, int n);
void reduce(int numerator, int denominator,
    int* reduced_numerator, int* reduced_denominator);

int main(void) {

    int num, denom;

    printf("Enter a fraction: ");
    scanf("%d /%d", &num, &denom);

    reduce(num, denom, &num, &denom);

    printf("In lowest terms: %d/%d\n", num, denom);

    return 0;
}

int find_gcd(int m, int n)
{
    while (n != 0)
    {
        int r = m % n;
        m = n;
        n = r;
    }

    return m;
}

void reduce(int numerator, int denominator,
    int* reduced_numerator, int* reduced_denominator) {

    int m = find_gcd(numerator, denominator);

    *reduced_numerator = numerator / m;
    *reduced_denominator = denominator / m;

    if (*reduced_denominator < 0)
    {
        *reduced_numerator *= -1;
        *reduced_denominator *= -1;
    }
}