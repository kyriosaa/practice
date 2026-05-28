//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 9.6 that separates the quicksort and split funtions in different files
//Change History: 

#include <stdio.h>
#include "quicksort.h"

#define N 10

int main(void) {

	int a[N], i;

	printf("Enter %d numbers to be sorted: ", N);
	for (i = 0; i < N; i++)
		scanf("%d", &a[i]);
	quicksort(a, 0, N - 1);

	printf("In sorted order: ");
	for (i = 0; i < N, i++)
		printf("%d", a[i]);
	printf("\n");

	return 0;
}