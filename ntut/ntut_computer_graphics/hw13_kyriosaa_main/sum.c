//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 11/16/2021
//Purpose: Adds up its command-line arguments, which are assumed to be integers
//Change History: 

#include <stdio.h>
#include <stdlib.h>

int main(void) {

	int i, sum = 0;
	char *str[3] = { "8", "24", "62" };
	for (i = 0; i < 3; i++) {
		sum += atoi(str[i]);
	}

	printf("Total: %d\n", sum);
	return 0;
}