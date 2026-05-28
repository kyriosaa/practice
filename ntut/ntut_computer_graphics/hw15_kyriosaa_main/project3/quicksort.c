//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 9.6 that separates the quicksort and split funtions in different files
//Change History: 

#include "quicksort.h"

void quicksort(int a[], int low, int high) {

	int middle;

	if (low >= high) return;
	middle = split(a, low, high);
	quicksort(a, low, middle - 1);
	quicksort(a, middle + 1, high);
}

int split(int a[], int low, int high) {

	int part_element = a[low];

	for (;;) {
		while (low < high && part_element <= a[high])
			high--;
		if (low >= high) break;
		a[low++] = a[high];

		while (low < high && a[low] <= part_element)
			low++;
		if (low >= high) break;
		a[high--] = a[low];
	}
	a[high] = part_element;
	return high;
}