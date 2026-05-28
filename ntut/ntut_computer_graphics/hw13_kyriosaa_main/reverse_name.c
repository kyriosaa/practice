//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 11/16/2021
//Purpose: Reverses the name so that the last name comes first, followed by a comma, a space, the first initial, then a period
//Change History:

#include <stdio.h>

void reverse_name(char* name);

int main(void) {

	char name[81];

	printf("Enter a first and last name: ");
	fgets(name, sizeof(name), stdin);
	reverse_name(name);

	return 0;
}

void reverse_name(char* name) {

	char* p = name, initial;

	while (*p == ' ')
		p++;
	initial = *p++;

	while (*p && *p++ != ' ')
		;

	while (*p && *p != '\n')
		putchar(*p++);
	printf(", %c.\n", initial);
}