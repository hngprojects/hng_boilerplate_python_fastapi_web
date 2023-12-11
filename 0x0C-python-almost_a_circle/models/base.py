#!/usr/bin/python3
"""
class base
"""
import json
import csv
import turtle


class Base:
    """
    a class Base

    ARGS
    __nb_objects - (int) number of objects
    id - (int) object id
    """
    __nb_objects = 0

    def __init__(self, id=None):
        """
        class constructor
        innitializes the class base
        """
        if id is not None:
            self.id = id
        else:
            Base.__nb_objects += 1
            self.id = Base.__nb_objects

    @staticmethod
    def to_json_string(list_dictionaries):
        """
        returns a json representation of list_dictionaries

        ARGS
        List_dictionaries - a list containing a list of dictionaries
        """
        ld = list_dictionaries
        if ld is None or len(ld) == 0:
            return "[]"
        return json.dumps(ld)

    @classmethod
    def save_to_file(cls, list_objs):
        """
        saves a list of dictionary representation of an
        object to a file
        """
        lo = list_objs
        filename = cls.__name__ + ".json"
        with open(filename, "w") as file:
            if lo is None or len(lo) == 0:
                file.write("[]")
            else:
                new = [a.to_dictionary() for a in lo]
                file.write(Base.to_json_string(new))

    @staticmethod
    def from_json_string(json_string):
        """
        deserializes a json string
        """
        if json_string is None or json_string == "[]":
            return ([])
        return json.loads(json_string)

    @classmethod
    def create(cls, **dictionary):
        """
        instanciates an object from the arguments in  **dictionary
        """
        if cls.__name__ == "Rectangle":
            new = cls(1, 2)
        else:
            new = cls(3)
        new.update(**dictionary)
        return (new)

    @classmethod
    def load_from_file(cls):
        """
        reads data from a json file
        """
        filename = cls.__name__ + ".json"
        try:
            with open(filename, "r") as file:
                dc = Base.from_json_string(file.read())
                return [cls.create(**a) for a in dc]
        except IOError:
            return []

    @classmethod
    def save_to_file_csv(cls, list_objs):
        """
        saves data to a file using csv file format
        """
        lo = list_objs
        if cls.__name__ == "Rectangle":
            fieldnames = ["id", "width", "height", "x", "y"]
        else:
            fieldnames = ["id", "size", "x", "y"]
        filename = cls.__name__ + ".csv"

        with open(filename, "w", newline="") as file:
            if lo is None or len(lo) == 0:
                file.write("[]")
            else:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                for a in lo:
                    writer.writerow(a.to_dictionary())

    @classmethod
    def load_from_file_csv(cls):
        """
        loads data from a file which is in dictionry form
        objects are then instancialised from the dictionary info
        """
        if cls.__name__ == "Rectangle":
            fieldnames = ["id", "width", "height", "x", "y"]
        else:
            fieldnames = ["id", "size", "x", "y"]
        filename = cls.__name__ + ".csv"
        try:
            with open(filename, "r", newline="") as file:
                reader = csv.DictReader(file, fieldnames=fieldnames)
                dc = [dict([k, int(v)] for k, v in a.items()) for a in reader]
                return ([cls.create(**a) for a in dc])
        except IOError:
            return ([])

    @staticmethod
    def draw(lis_rectangles, list_squares):
        """
        draws shapes from objects.
        list_rectangles holds objects with rectangle shapes
        list_squares holds objects with square shapes
        """
        doll = turtle.Turtle()
        doll.pen(fillcolor="black", pencolor="black")
        doll.screen.bgcolor("#C8A2C8")
        doll.shape("turtle")

        for a in lis_rectangles:
            doll.showturtle()
            doll.up()
            doll.setpos(a.x, a.y)
            doll.down()

            for _ in range(2):
                doll.fd(a.width)
                doll.lt(90)
                doll.fd(a.height)
                doll.lt(90)
            doll.hideturtle()

        for a in list_squares:
            doll.showturtle()
            doll.up()
            doll.setpos(a.x, a.y)
            doll.down()
            for _ in range(2):
                doll.fd(a.width)
                doll.lt(90)
                doll.fd(a.height)
                doll.lt(90)
        doll.hideturtle()
