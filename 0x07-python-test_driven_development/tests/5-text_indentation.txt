The ``5-text_indentation`` module
============================

Using ``text_indentation``
---------------------

Importing function from the module:

    >>> text_indentation = __import__('5-text_indentation').text_indentation

Printing a large message

    >>> text_indentation("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quonam modo? Utrum igitur tibi litteram videor an totas paginas commovere? Non autem hoc: igitur ne illud quidem. Fortasse id optimum, sed ubi illud: Plus semper voluptatis? Teneo, inquit, finem illi videri nihil dolere. Transfer idem ad modestiam vel temperantiam, quae est moderatio cupiditatum rationi oboediens. Si id dicis, vicimus. Inde sermone vario sex illa a Dipylo stadia confecimus. Sin aliud quid voles, postea. Quae animi affectio suum cuique tribuens atque hanc, quam dico. Utinam quidem dicerent alium alio beatiorem! Iam ruinas videres""")
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    <BLANKLINE>
    Quonam modo?
    <BLANKLINE>
    Utrum igitur tibi litteram videor an totas paginas commovere?
    <BLANKLINE>
    Non autem hoc:
    <BLANKLINE>
    igitur ne illud quidem.
    <BLANKLINE>
    Fortasse id optimum, sed ubi illud:
    <BLANKLINE>
    Plus semper voluptatis?
    <BLANKLINE>
    Teneo, inquit, finem illi videri nihil dolere.
    <BLANKLINE>
    Transfer idem ad modestiam vel temperantiam, quae est moderatio cupiditatum rationi oboediens.
    <BLANKLINE>
    Si id dicis, vicimus.
    <BLANKLINE>
    Inde sermone vario sex illa a Dipylo stadia confecimus.
    <BLANKLINE>
    Sin aliud quid voles, postea.
    <BLANKLINE>
    Quae animi affectio suum cuique tribuens atque hanc, quam dico.
    <BLANKLINE>
    Utinam quidem dicerent alium alio beatiorem! Iam ruinas videres

Printing a word with spaces around

    >>> text_indentation("    Holberton    ")
    Holberton

Printing a word with a special character at the end

    >>> text_indentation("    Hello    .")
    Hello.
    <BLANKLINE>

Printing all special characters

    >>> text_indentation(".?:")
    .
    <BLANKLINE>
    ?
    <BLANKLINE>
    :
    <BLANKLINE>

Passing Node as a text

    >>> text_indentation(None)
    Traceback (most recent call last):
    	      ...
    TypeError: text must be a string

Passing a number as a text

    >>> text_indentation(10)
    Traceback (most recent call last):
    	      ...
    TypeError: text must be a string

Printing a text with special characters

    >>> text_indentation("Betty: Holberton? Python is. cool   ")
    Betty:
    <BLANKLINE>
    Holberton?
    <BLANKLINE>
    Python is.
    <BLANKLINE>
    cool

Printing a char number

    >>> text_indentation('2')
    2

Passing an empty string

    >>> text_indentation('    ')

Passing a new line as a text

    >>> text_indentation('\n')
    <BLANKLINE>

Passing a special character and some special characters

    >>> text_indentation('\n.\n?\n:')
    <BLANKLINE>
    .
    <BLANKLINE>
    <BLANKLINE>
    ?
    <BLANKLINE>
    <BLANKLINE>
    :
    <BLANKLINE>

Passing a text with spaces and one new line

    >>> text_indentation("   \n")
    <BLANKLINE>

Passing a text with spaces and one new line 2

   >>> text_indentation("   \n   ")
   <BLANKLINE>

Passing a text with spaces and one new line 3

   >>> text_indentation("\n   ")
   <BLANKLINE>
