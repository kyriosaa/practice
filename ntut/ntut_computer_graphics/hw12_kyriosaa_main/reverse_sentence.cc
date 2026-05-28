//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 10/20/2021
//Purpose: A modified Project 14 Chapter 8 program that uses a pointer instead of an interger to keep track of the current position in the array that contains the sentence
//Change History: 

#include <stdio.h>

#define MAX_VALUE 100

int main(void) {

	char c, * p, * q, terminating_char, words[MAX_VALUE] = { 0 };

	printf("Enter a sentence: ");
	for (p = words; (c = getchar()) != '\n' && p < words + MAX_VALUE; p++) {
		if (c == '.' || c == '!' || c == '?') {
			terminating_char = c;
			break;
		}
		*p = c;
	}	

	printf("Reversal of sentence: ");
	while (p > words) {
		while (*--p != ' ' && p != words);
		q = p == words ? words : p + 1;
		while (*q != ' ' && *q != '\0')
			printf("%c", *q++);
		if (p > words)
			printf(" ");
	}

	printf("%c\n", terminating_char);

	return 0;
}