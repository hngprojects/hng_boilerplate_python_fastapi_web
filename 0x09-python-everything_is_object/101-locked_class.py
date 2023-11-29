class LockedClass:
    def __setattr__(self, name, value):
        # Allow setting only if the attribute is 'first_name'
        if name == 'first_name':
            self.__dict__[name] = value
        else:
            raise AttributeError(f"'LockedClass' object has no attribute '{name}'")

# Example usage:
locked_instance = LockedClass()

# This will work
locked_instance.first_name = 'John'
print(locked_instance.first_name)  # Output: John

# This will raise an AttributeError
try:
    locked_instance.last_name = 'Doe'
except AttributeError as e:
    print(e)  # Output: 'LockedClass' object has no attribute 'last_name'

