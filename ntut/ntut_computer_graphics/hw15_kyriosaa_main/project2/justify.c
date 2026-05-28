//Class: Computer Programming II
//Author: Purit Hongjirakul
//ID: 109990016
//Date: 12/14/2021
//Purpose: Justifies lines by inserting extra spaces between words
//Change History: 

#include <string.h>
#include "line.h"
#include "word.h"

#define MAX_WORD_LEN 20

int main(void) {

	char word[MAX_WORD_LEN + 2];
	int word_len;

	clear_line();
	for (;;) {
		read_word(word, MAX_WORD_LEN + 1);
		word_len = strlen(word);
		if (word_len == 0) {
			flush_line();
			return 0;
		}
		if (word_len + 1 > space_remaining()) {
			write_line();
			clear_line();
		}
		add_word(word);
	}
}