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
int compare_strings(const void *p, const void *q);

int main(void){
    char *words[MAX_WORDS], word[WORD_LEN+1];
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

    qsort(words, num_words, sizeof(char *), compare_strings);

    printf("\nIn soreted order: ");
    for(i = 0; i < num_words; i++){
        printf(" %s", words[i]);
    }//for

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

int compare_strings(const void *p, const void *q){
    return strcmp(*(char**)p, *(char**)q);
}