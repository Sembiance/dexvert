class FileNotLoadedError(FileNotFoundError):
    def __init__(self):
        pass

    def __str__(self):
        return "Function cannot be called without a loaded file."


class PILNotLoadedError(FileNotFoundError):
    def __init__(self):
        pass

    def __str__(self):
        return "Function cannot be called without having PIL installed."
