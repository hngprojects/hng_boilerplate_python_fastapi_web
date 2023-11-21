#!/usr/bin/python3


class Node:
    """
    A class representing a node of a singly linked list.

    Attributes:
        data (int): The data stored in the node.
        next_node (Node): The next node in the linked list.
    """

    def __init__(self, data, next_node=None):
        """
        Initialize a Node instance.

        Args:
            data (int): The data to be stored in the node.
            next_node: The next node in the linked list. Default is None.
        """
        self.data = data
        self.next_node = next_node

        @property
        def data(self):
            return self.__data

        @data.setter
        def data(self, value):
            if not isinstance(value, int):
                raise TypeError("data must be an integer")
            self.__data = value

        @property
        def next_node(self):
            return self.__next_node

        @next_node.setter
        def next_node(self, value):
            if value is not None and not isinstance(value, Node):
                raise TypeError("next_node must be a Node object")
            self.__next_node = value


class SinglyLinkedList:

    """
    A class representing a singly linked list.
    """

    def __init__(self):
        """
        Initialize an empty SinglyLinkedList instance.
        """
        self.head = None

    def sorted_insert(self, value):
        """
        Insert a new Node into the correct sorted position in the list
        Args:
            value (int): The value to be inserted.
        """
        new_node = Node(value)

        if self.head is None or self.head.data > value:
            new_node.next_node = self.head
            self.head = new_node
        else:
            current = self.head
            while current.next_node is not None
            and current.next_node.data < value:
                current = current.next_node
            new_node.next_node = current.next_node
            current.next_node = new_node

    def __str__(self):
        """
        Return a string representation of the linked list.
        """
        nodes = []
        current = self.head
        while current is not None:
            nodes.append(str(current.data))
            current = current.next_node
        return '\n'.join(nodes)
