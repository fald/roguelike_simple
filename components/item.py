class Item:
    def __init__(self, use_function=None, owner=None, targeting=False, targeting_message=None, **kwargs):
        self.owner = owner
        self.use_function = use_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message