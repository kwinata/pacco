def check_ascii(string):
    if not string.isascii():
        raise NameError(f"{string} must be ascii instead.")
