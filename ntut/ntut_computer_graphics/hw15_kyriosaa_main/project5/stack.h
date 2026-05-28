//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Modified program from Section 10.6 so that it has stack.h and stack.c files
//Change History: 

#ifndef STACK_H
#define STACK_H

void make_empty(void);
bool is_empty(void);
bool is_full(void);
void push(char i);
char pop(void);

#endif