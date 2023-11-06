#include "lists.h"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * is_palindrome - checks if a singly linked list is a palindrome
 * @head: pointer to head of list
 * Return: 0 if it's not a palindrome, 1 if it's a palindrome
 */
int is_palindrome(listint_t **head)
{
	listint_t *fast, *slow, *mid, *slow_track;
	int  pal;

	fast = slow = slow_track = *head;
	mid = NULL;

	pal = 1;
	if (*head && (*head)->next)
	{
		while (fast && fast->next)
		{
			fast = fast->next->next;
			slow_track = slow, slow = slow->next;
		}

		if (fast)
		{
			mid = slow, slow = slow->next;
		}

		flip(&slow);
		slow_track->next = NULL;
		pal = contrast(head, &slow);

		if (mid)
		{
			slow_track->next = mid;
			mid->next = slow;
		}
		else
		{
			slow_track->next = slow;
		}
	}
	return (pal);
}

/**
 *contrast - compares the integer values of the linked list
 *@head: the head of the fast half of linked list
 *@slow: the head of the second half of the linked list
 *Return: 0 if not palindrome else 1
 */
int contrast(listint_t **head, listint_t **slow)
{
	listint_t *Head = *head, *Slow = *slow;

	while (Head && Slow)
	{
		if (Head->n != Slow->n)
		{
			return (0);
		}

		Head = Head->next;
		Slow = Slow->next;
	}

	if (!Head && !Slow)
	{
		return (1);
	}

	return (0);
}

/**
 *flip - reverses a linked list
 *@slow: the head of the first half of the linked list
 *Return: nothing
 */
void flip(listint_t **slow)
{
	listint_t *cp, *next, *prev;

	cp = *slow, prev = NULL;

	while (cp)
	{
		next = cp->next;
		cp->next = prev;
		prev = cp;
		cp = next;
	}
	*slow = prev;
}
