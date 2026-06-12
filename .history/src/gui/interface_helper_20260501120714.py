def load_stylesheet(path):
    """ Load a stylesheet from a file """
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Stylesheet not found: {path}. Using default.")
        return ""