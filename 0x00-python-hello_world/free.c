void free_list(listint *head)
{
	listint *current;

	while (head != NULL)
	{
		current = head->next;
		free(head);
		head = current;
	}
}

