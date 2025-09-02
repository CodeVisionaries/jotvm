class SimpleDebugPrinter:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(SimpleDebugPrinter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._debug = False
        self._initialized = True

    def enable(self):
        self._debug = True

    def disable(self):
        self._debug = False

    def is_active(self):
        return self._debug

    def debug(self, message):
        if self.is_active():
            print(message)
