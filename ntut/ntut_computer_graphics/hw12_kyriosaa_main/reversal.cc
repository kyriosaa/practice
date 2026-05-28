//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 10/20/2021
//Purpose: This program reads a message, then prints the reversal of that message.
//Change History: 

#include <iostream>

#define MAX_LEN 100

int main(void) {

	char message[MAX_LEN];
	char c, * p = message;

	printf("Enter a message: ");
	
	while ((c = getchar()) != '\n' && p < message + MAX_LEN)
		*p++ = c;

	p--;
	printf("Reversal is: ");

	while (p >= message)
		putchar(*p--);

	printf("\n");

	return 0;
}