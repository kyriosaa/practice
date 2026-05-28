//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 11/16/2021
//Purpose: Accepts the date from a user in the form of mm/dd/yyyy and then displays in the form of month dd, yyyy where the month is the name of the month
//Change History:

#include <stdio.h>

int main(void) {

	int m, d, y;

	char* months[12] = { "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" };

	printf("Enter a date (mm/dd/yyyy): ");
	scanf("%d / %d / %d", &m, &d, &y);
	printf("You entered the date %s %.2d, %d\n", months[m - 1], d, y);
	return 0;
}