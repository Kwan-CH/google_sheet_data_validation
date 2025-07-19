import re
from datetime import datetime
from gspread.utils import rowcol_to_a1


class Validator:
    ROW_OFFSET = 2
    COLUMN_OFFSET = 1
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    DATE_FORMAT = "%d/%m/%Y"

    def __init__(self, df):
        self.df = df
        self.error_log = []
        self.duplicate_masks = {}

    def get_a1_idx(self, idx, column_name):
        row_num = idx + self.ROW_OFFSET
        col_num = self.df.columns.get_loc(column_name) + self.COLUMN_OFFSET
        return rowcol_to_a1(row_num, col_num)

    def log_error(self, row_loc, column_loc, message):
        row = row_loc.name + self.ROW_OFFSET
        column = self.df.columns.get_loc(column_loc) + self.COLUMN_OFFSET
        cell_A1 = rowcol_to_a1(row, column)
        self.error_log.append(
            {
                "location": cell_A1,
                "error": message
            }
        )


    def isEmpty(self, row, column_name):
        if row[column_name].strip() == "":
            self.log_error(row, column_name, "This cannot be empty, please fill in this section")
            return True
        else:
            return False


    def isNumeric(self, row, column_name):
        if self.isEmpty(row, column_name):
            return False
        try:
            int(row[column_name])
        except ValueError:
            self.log_error(row, column_name, "This section can only be digits only")

    def isEmail(self, row, column_name):
        if self.isEmpty(row, column_name):
            return False
        if not re.match(self.EMAIL_PATTERN, row[column_name]):
            self.log_error(row, column_name, "Please enter a valid email")

    def isDate(self, row, column_name):
        if self.isEmpty(row, column_name):
            return False
        try:
            datetime.strptime(row[column_name], self.DATE_FORMAT)
        except ValueError:
            self.log_error(row, column_name, "Please enter a valid date format, day/month/year")


    def isDuplicate(self, row, column_name):
        if self.isEmpty(row, column_name):
            return False
        value = row[column_name]
        if column_name not in self.duplicate_masks:
            self.duplicate_masks[column_name] = self.df[column_name].duplicated(keep=False)

        if self.duplicate_masks[column_name][row.name]:
            matches = self.df.index[self.df[column_name] == value].tolist()
            if row.name == min(matches):
                locations = [self.get_a1_idx(idx, column_name) for idx in matches]
                self.error_log.append({
                    "location": ", ".join(locations),
                    "error": "Both cells have the same value"
                })

    def isPrefix(self, row, column_name, prefix):
        if self.isEmpty(row, column_name):
            return False
        if not row[column_name].startswith(prefix):
            self.log_error(row, column_name, f"Please enter data that starts with {prefix}")

    def isInOption(self, row, column_name, options):
        if self.isEmpty(row, column_name):
            return False
        if not row[column_name] in options:
            self.log_error(row, column_name, f"Please enter data that is only available in here: {options}")

