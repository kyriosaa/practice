//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 10.6 so that it has stack.h and stack.c files
//Change History: 

#include <stdio.h>
#include <stdlib.h> /* exit */
#include <ctype.h> /* isdigit */
#include <stdbool.h> /* C99+ only */
#include "stack.h"

int main(void) {

	char c, op1, op2;

	while (true) {

		printf("Enter an RPN expression: ");

		while ((c = getchar()) != '\n') {
			if (isdigit(c))
				push(c - '0');
			else
				switch (c) {
					case '+': push(pop() + pop());
						break;
					case '-': op2 = pop();
						   	  op1 = pop();
							  push(op1 - op2);
							  break;
					case '*': push(pop() * pop());
						      break;
					case '/': op2 = pop();
						   	  op1 = pop();
							  push(op1 / op2);
							  break;
					case '=': printf("Value of expression: %d\n", pop());
							  break;
					case ' ': break;
					default:  exit(0);
				}
		}
	}
}