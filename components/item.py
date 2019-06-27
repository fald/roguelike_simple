class Item:
    def __init__(self, use_function=None, owner=None, **kwargs):
        self.owner = owner
        self.use_function = use_function
        self.function_kwargs = kwargs
        