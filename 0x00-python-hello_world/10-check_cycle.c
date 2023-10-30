#include "lists.h"

/**
*check_cycle -  checks for a cycle
*@list: the linked list to check
*Return: 1 if a cycle is found else 0
*/

int check_cycle(listint_t *list)
{
listint_t *slow = list;
listint_t *fast = list;

while (slow != NULL && fast != NULL && fast->next != NULL)
{
slow = slow->next;
fast = fast->next->next;
if (slow == fast)
{
return (1);
}
}

return (0);
}
