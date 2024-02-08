class LockedClass:
    def __setattr__(self, name, value):
        if name == 'first_name':
            self.__dict__[name] = value
        else:
            raise AttributeError(f"'LockedClass' object has no attribute '{name}'")

locked_instance = LockedClass()


locked_instance.first_name = 'John'
print(locked_instance.first_name)

try:
    locked_instance.last_name = 'Doe'
except AttributeError as e:
    print(e)
