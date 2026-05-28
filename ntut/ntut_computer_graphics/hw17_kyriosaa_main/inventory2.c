/********************************************************************/
/* Class: Computer Programming (II), Fall 2021                      */
/* Author: Purit Hongjirakul                                        */
/* ID: 109990016                                                    */
/* Date: 2020.01.11                                                 */
/* Purpose: Modify the inventory2.c program of Section 17.5 by adding an e (erase) command that allows the user to remove a part from the database. */                                             */
/* Change History: -                                                */
/********************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#define NAME_LEN 25

struct part {
    int number;
    char name[NAME_LEN - 1];
    int on_hand;
    struct part *next;
};

struct part *inventory = NULL;

struct part *find_part(int number);
void insert(void);
void search(void);
void update(void);
void print(void);
void erase(void);
int read_line(char str[], int n);

int main(void)
{
    char code;
    
    for(;;){
        printf("Enter operation code: ");
        scanf(" %c", &code);

        while (getchar() != '\n')
            ;

        switch(code)
        {
            case 'i': insert();
                break;
            case 'e': erase();
                break;
            case 's': search();
                break;
            case 'u': update();
                break;
            case 'p': print();
                break;
            case 'q': return 0;
            default: printf("Illegal code\n");
        }
        printf("\n");
    }
}
//looks up a part number in the inventory array. Returns the array index if the part number is found; otherwise returns -1.
struct part *find_part(int number)
{
    struct part *p;
    for (p = inventory;
        p!= NULL && number > p->number;
        p = p->next)
    ;
    if (p != NULL && number == p->number)
        return p;
    return NULL;
}
//inserting new part to database,Prints an error message and returns prematurely if the part already exists or the database is full.
void insert(void)
{
  struct part *cur, *prev, *new_node;

  new_node = malloc(sizeof(struct part));
  if (new_node == NULL) {
    printf("Database is full; can't add more parts.\n");
    return;
  }

  printf("Enter part number: ");
  scanf("%d", &new_node->number);

  for (cur = inventory, prev = NULL;
       cur != NULL && new_node->number > cur->number;
       prev = cur, cur = cur->next)
    ;
  if (cur != NULL && new_node->number == cur->number) {
    printf("Part already exists.\n");
    free(new_node);
    return;
  }

  printf("Enter part name: ");
  read_line(new_node->name, NAME_LEN);
  printf("Enter quantity on hand: ");
  scanf("%d", &new_node->on_hand);

  new_node->next = cur;
  if (prev == NULL)
    inventory = new_node;
  else
    prev->next = new_node;
}
//erase a part in the database if part not exist -> print error
void erase(void)
{
    struct part **pp = &inventory;
    struct part *temp;
    int n;
    printf("Enter part number: ");
    scanf("%d", &n);

    while(*pp) {
        if ((*pp)->number == n) {
            temp = *pp;
            *pp = (*pp)->next;
            free(temp);
            return;
        }
        pp = &(*pp)->next;
    }
    printf("Part number %d not found in database\n", n);
    return;
}
//looks up the part inthe database. If exists, prints the name and quantity on hand; if not, prints an error message.
void search(void)
{
  int number;
  struct part *p;

  printf("Enter part number: ");
  scanf("%d", &number);
  p = find_part(number);
  if (p != NULL) {
    printf("Part name: %s\n", p->name);
    printf("Quantity on hand: %d\n", p->on_hand);
  } else
    printf("Part not found.\n");
}

void update(void)
{
  int number, change;
  struct part *p;

  printf("Enter part number: ");
  scanf("%d", &number);
  p = find_part(number);
  if (p != NULL) {
    printf("Enter change in quantity on hand: ");
    scanf("%d", &change);
    p->on_hand += change;
  } else
    printf("Part not found.\n");
}
//prints an error message if the part doesn't exist; otherwise, prompts the user to enter new price and updates the database.
void print(void)
{
  struct part *p;

  printf("Part Number   Part Name                  "
         "Quantity on Hand\n");
  for (p = inventory; p != NULL; p = p->next)
    printf("%7d       %-25s%11d\n", p->number, p->name,
           p->on_hand);
}

int read_line(char str[], int n)
{
    int ch, i = 0;

    while (isspace(ch = getchar()))
        ;
    while(ch != '\n' && ch != EOF){
        if (i < n)
            str[i++] = ch;
        ch = getchar();
    }
    str[i] ='\0';
    return i;
}