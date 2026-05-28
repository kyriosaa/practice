//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 9/28/2021
//Purpose: This function will find the flight whose departure time is closest to desired_time
//Change History: 

#include <stdio.h>

#define HOURS_PER_HALF_DAY 12
#define MINUTES_PER_HOURS 60
#define MINUTES_PER_HALF_DAY (HOURS_PER_HALF_DAY * MINUTES_PER_HOURS)

#define SIZE ((int)(sizeof(departures) / sizeof(departures[0])))

void find_closest_flight(int desired_time,
	int* departure_time,
	int* arrival_time);

int main(void) {

	int hours, minutes, desired_time,
		departure_time, departure_hour,
		arrival_time, arrival_hour;

	//printf("Enter a 24-hour time: ");
	scanf("%d :%d", &hours, &minutes);

	desired_time = hours * MINUTES_PER_HOURS + minutes;

	find_closest_flight(desired_time, &departure_time, &arrival_time);

	printf("Closest departure time is ");

	departure_hour = departure_time / MINUTES_PER_HOURS;

	if (departure_hour == 0)
	{
		departure_hour = HOURS_PER_HALF_DAY;
	}
	else if (departure_hour > HOURS_PER_HALF_DAY)
	{
		departure_hour -= HOURS_PER_HALF_DAY;
	}

	if (departure_time != 945 && departure_time != 480)
		printf("%d:%.2d", departure_hour, departure_time & MINUTES_PER_HOURS);
	else if (departure_time == 945)
		printf("%d:45", departure_hour);
	else if (departure_time == 480)
		printf("%d:00", departure_hour);



	if (departure_hour < MINUTES_PER_HOURS)
	{
		printf(" a.m");
	}
	else
	{
		printf(" p.m");
	}

	printf(" arriving at ");

	arrival_hour = arrival_time / MINUTES_PER_HOURS;
	if (arrival_hour == 0)
	{
		arrival_hour = HOURS_PER_HALF_DAY;
	}
	/*
	else if (arrival_hour > HOURS_PER_HALF_DAY)
	{
		arrival_hour -= HOURS_PER_HALF_DAY;
	}
	*/
	printf("%d:%.2d", arrival_hour, arrival_time % MINUTES_PER_HOURS);

	if (arrival_time < 13 * MINUTES_PER_HOURS)
	{
		if (departure_time == 480)
			printf(" p.m");
		else
			printf(" a.m");
	}
	else {
		printf(" p.m");
	}
	printf("\n");

	return 0;
}
void find_closest_flight(int desired_time,
	int* departure_time,
	int* arrival_time)
{

	int departures[] = { 480, 583, 679, 767, 840, 945, 1140, 1305 },
		arrivals[] = { 616, 712, 900, 968, 1075, 1280, 1438 },
		closest;

	if (desired_time <= departures[0]) {
		closest = 0;
	}
	else if (desired_time > departures[SIZE - 1]) {
		closest = 0;
	}
	else {
		closest = 0;
		while (desired_time > departures[closest + 1]) {
			closest++;
		}
		if ((departures[closest + 1] - desired_time) < (desired_time - departures[closest])) {
			closest++;
		}
	}

	*departure_time = departures[closest];
	*arrival_time = arrivals[closest];
}