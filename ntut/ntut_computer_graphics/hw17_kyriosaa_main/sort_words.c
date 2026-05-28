/********************************************************************/
/* Class: Computer Programming (II), Fall 2021                      */
/* Author: Purit Hongjirakul                                        */
/* ID: 109990016                                                    */
/* Date: 2020.01.11                                                 */
/* Purpose: a program that sorts a series of words entered by the user */ 
/* Change History: -                                                */
/********************************************************************/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_WORDS 50
#define WORD_LEN 20

int read_line(char stf[], int n);
void quicksort(char **low, char **high);
char **split(char **low, char **high);

int main(void)
{
    char *words[MAX_WORDS], word[WORD_LEN-1];
    int i, num_words = 0;

    for(;;)
    {
        if (num_words == MAX_WORDS){
            printf(" --No space left --\n");
            break;
        }//if

        printf("Enter word: ");
        read_line(word, WORD_LEN);
        if(strlen(word) == 0){
            break;
        }

        words[num_words] = (char*)malloc(strlen(word) +1);
        if(words[num_words] == NULL){
            printf(" --No space left --\n");
            break;
        }//if

        strcpy(words[num_words], word);
        num_words++;
    }//for

    quicksort(words, words+num_words-1);
    printf("\nIn sorted order: ");
    for(i = 0; i < num_words; i++){
        printf("%s ", words[i]);
    }
    printf("\n");
    
    return 0;
}

int read_line(char str[], int n)
{
    int ch, i = 0;
    while ((ch = getchar()) != '\n'){
        if (i <n){
            str[i++] = ch;
        }
    }
    str[i] = '\0';
    return i;
}

void quicksort(char **low, char**high){
    char **middle;

    if(low>=high) return;
    middle = split(low,high);
    quicksort(low, middle);
    quicksort(middle+1,high);
}

char ** split(char **low, char **high){
    char *part_element = *low;

    for(;;){
        while (low < high && strcmp(part_element, *high) <= 0){
            high--;
        }
        if(low >= high) break;
        *low++ = *low;

        while(low <high && strcmp(*low, part_element) <= 0){
            low++;
        }
        if(low>= high) break;
        *low-- = *low;
    }

    *high = part_element;
    return high;
}