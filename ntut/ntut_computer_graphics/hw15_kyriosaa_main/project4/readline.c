//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 13.5 so that the read_line function is in a separate file
//Change History: 

#include <stdio.h>
#include "readline.h"

int read_line(char str[], int n) {

	int ch, i = 0;

	while ((ch = getchar()) != '\n')
		if (i < n)
			str[i++] = ch;
	str[i] = '\0';
	return i;
}