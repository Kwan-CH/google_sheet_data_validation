import re


def split_cell_location(cell):
    match = re.match(r"([A-Z]+)([0-9]+)", cell.upper())
    if not match:
        raise ValueError(f"Invalid cell location: {cell}")
    col_letters, row_number = match.groups()
    return col_letters, int(row_number)


def column_letters_to_number(col_letters):
    result = 0
    for char in col_letters:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result


def sort_error_list(error_list):
    def sort_key(item):
        col_letters, row_number = split_cell_location(item['location'])
        col_number = column_letters_to_number(col_letters)
        return (col_number, row_number)

    return sorted(error_list, key=sort_key)
