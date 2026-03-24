class RegisterBank:
    #This piece of code makes the object singleton.
    _instance = None
    def __new__(cls):

        cls.values = {
            '0': "0000000000000000",
            '1': "0000000000000000",
            '2': "0000000000000000",
            '3': "0000000000000000",
            '4': "0000000000000000",
            '5': "0000000000000000",
            '6': "0000000000000000",
            '7': "0000000000000000",
            '8': "0000000000000000",
            '9': "0000000000000000",
            'A': "0000000000000000",
            'B': "0000000000000000",
            'C': "0000000000000000",
            'D': "0000000000000000",
            'E': "0000000000000000",
            'F': "0000000000000000"
        } 


        cls.stack_pointer = 0

        if cls._instance is None:
            # If it doesn't exist yet, create it
            cls._instance = super(RegisterBank, cls).__new__(cls)
        return cls._instance
    

registers = RegisterBank()