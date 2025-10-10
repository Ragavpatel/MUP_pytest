class StateManager:
    _store = {}

    @classmethod
    def set_value(cls, key, value):
        """Set a variable"""
        cls._store[key] = value

    @classmethod
    def get_value(cls, key, default=None):
        """Get a variable"""
        return cls._store.get(key, default)