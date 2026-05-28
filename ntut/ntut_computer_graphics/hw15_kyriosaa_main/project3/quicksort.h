//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 9.6 that separates the quicksort and split funtions in different files
//Change History: 

#ifndef QUICKSORT_H_INCLUDED
#define QUICKSORT_H_INCLUDED

void quicksort(int a[], int low, int high);
int split(int a[], int low, int high);

#endif