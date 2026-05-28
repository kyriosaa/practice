/********************************************************************/
/* Class: Computer Programming (II), Fall 2020                      */
/* Author: Purit Hongjirakul                                        */
/* ID: 109990016                                                    */
/* Date: 2020.12.26                                                 */
/* Purpose: Modify the inventory.c program of Section 16.3 by adding a price member to the part structure                                                                                                      */
/* Change History:                                                  */
/********************************************************************/

#include <stdio.h>
#include "readline.h"

#define NAME_LEN 25
#define MAX_PARTS 100

struct part {
    int number;
    char name[NAME_LEN + 1];
    int on_hand;
    double price;
};

int num_parts = 0;

int find_part(const struct part inventory[], int num_parts, int number);
void insert(struct part inventory[], int* num_parts);
void search(const struct part inventory[], int num_parts);
void update(struct part inventory[], int num_parts);
void print(struct part inventory[], int num_parts);
void change_price(struct part inventory[], int num_parts);

int main(void) {

    struct part inventory[MAX_PARTS];
    char code;

    for (;;) {
        printf("Enter operation code: ");
        scanf(" %c", &code);
        while (getchar() != '\n')
            ;
        switch (code) {
        case 'i': insert(inventory, &num_parts);
            break;
        case 's': search(inventory, num_parts);
            break;
        case 'u': update(inventory, num_parts);
            break;
        case 'p': print(inventory, num_parts);
            break;
        case 'c': change_price(inventory, num_parts);
            break;
        case 'q': return 0;
        default:  printf("Illegal code\n");
        }
        printf("\n");
    }
}


//looks up a part number in the inventory array. Returns the array index if the part number is found; otherwise returns -1.
int find_part(const struct part inventory[], int num_parts, int number) {
    int i;
    for (i = 0; i < num_parts; i++)
        if (inventory[i].number == number)
            return i;
    return -1;
}

//inserting new part to database,Prints an error message and returns prematurely if the part already exists or the database is full.
void insert(struct part inventory[], int* num_parts) {
    int part_number;

    if (*num_parts == MAX_PARTS) {
        printf("Database is full; can't add more parts.\n");
        return;
    }
    printf("Enter part number: ");
    scanf("%d", &part_number);
    if (find_part(inventory, *num_parts, part_number) >= 0) {
        printf("Part already exists.\n");
        return;
    }

    inventory[*num_parts].number = part_number;
    printf("Enter part name: ");
    read_line(inventory[*num_parts].name, NAME_LEN);
    printf("Enter quantity on hand: ");
    scanf("%d", &inventory[*num_parts].on_hand);
    printf("Enter price: ");
    scanf("%lf", &inventory[*num_parts].price);
    (*num_parts)++;
}

//looks up the part inthe database. If exists, prints the name and quantity on hand; if not, prints an error message.
void search(const struct part inventory[], int num_parts) {
    int i, number;

    printf("Enter part number: ");
    scanf("%d", &number);
    i = find_part(inventory, num_parts, number);
    if (i >= 0) {
        printf("Part name: %s\n", inventory[i].name);
        printf("Quantity on hand: %d\n", inventory[i].on_hand);
        printf("Price: $%.2f\n", inventory[i].price);
    }
    else
        printf("Part not found.\n");
}

//prints an error message if the part doesn't exist; otherwise, prompts the user to enter change in quantity on hand and updates the database.

void update(struct part inventory[], int num_parts) {
    int i, number, change;

    printf("Enter part number: ");
    scanf("%d", &number);
    i = find_part(inventory, num_parts, number);
    if (i >= 0) {
        printf("Enter change in quantity on hand: ");
        scanf("%d", &change);
        inventory[i].on_hand += change;
    }
    else
        printf("Part not found.\n");
}

//prints a listing of all parts in the database, showing the part number, part name and quantity on hand. Parts are printed, sorted by their part number.
void print(struct part inventory[], int num_parts) {
    int i;

    quicksort(inventory, 0, num_parts - 1);

    printf("Part Number   Part Name                  "
        "Quantity on Hand   Price\n");
    for (i = 0; i < num_parts; i++)
        printf("%7d       %-25s%11d          $%7.2f\n", inventory[i].number,
            inventory[i].name, inventory[i].on_hand, inventory[i].price);
}

//prints an error message if the part doesn't exist; otherwise, prompts the user to enter new price and updates the database.
void change_price(struct part inventory[], int num_parts) {
    int i, number;

    printf("Enter part number: ");
    scanf("%d", &number);
    i = find_part(inventory, num_parts, number);
    if (i >= 0) {
        printf("Enter new price: ");
        scanf("%lf", &inventory[i].price);
    }
    else
        printf("Part not found.\n");
}
