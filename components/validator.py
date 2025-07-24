import json
import re

import pandas as pd
from gspread.utils import rowcol_to_a1

from components.customError import invalidMinMax


class Validator:
    with open("json/config.json", "r") as file:
        config = json.load(file)
    ROW_OFFSET = config["headerIndex"] + 2
    COLUMN_OFFSET = 1
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    DATE_FORMAT = "%d/%m/%Y"
    DATE_REGEX = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    VALID_NEGATIVE_REGEX = re.compile(r"^-?\d+(\.\d+)?$")

    def __init__(self, df):
        self.df = df
        self.error_log = []
        self.duplicate_masks = {}

    def get_a1_idx(self, idx, column_name):
        row_num = idx + self.ROW_OFFSET
        col_num = self.df.columns.get_loc(column_name) + self.COLUMN_OFFSET
        return rowcol_to_a1(row_num, col_num)

    def vectorized_log_error(self, failed, column_name, message):
        # .index will always get the Series index that have the True value
        for idx in self.df.index[failed]:
            row = idx + self.ROW_OFFSET
            column = self.df.columns.get_loc(column_name) + self.COLUMN_OFFSET
            cell_A1 = rowcol_to_a1(row, column)
            self.error_log.append(
                {
                    "location": cell_A1,
                    "error": message
                }
            )

    def isEmpty(self, column_name, allowEmpty):
        if allowEmpty.capitalize() == "True":
            return pd.Series(False, index=self.df.index)
        else:
            mask = self.df[column_name].str.strip() == ""
            self.vectorized_log_error(mask, column_name, "This cannot be empty, please fill in this section")
            return mask

    def isASCII(self, column_name):
        mask = ~self.df[column_name].apply(lambda x: x.isascii())
        self.vectorized_log_error(mask, column_name,
                      "This section have unknown character, please remove any tab/enter key or special character")
        return mask

    # substring
    def isContains(self, column_name, target_list, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        ascii_row = ~(self.isASCII(column_name))
        targets = [re.escape(target.strip()) for target in target_list.split(",")]
        pattern = '|'.join(targets)
        mask = non_empty_row & ascii_row & self.df[column_name].str.contains(pattern)
        self.vectorized_log_error(mask, column_name,
                                  f"This section cannot have one of the following character: {target_list}")

    def isNumeric(self, column_name, param, allowEmpty):
        allowNegative = True if param.get("allowNegative") == "True" else False
        try:
            haveMinimum = True if not param.get("min") is None else False
            haveMaximum = True if not param.get("max") is None else False

            numeric_col = pd.to_numeric(self.df[column_name], errors='coerce')

            non_empty_row = ~self.isEmpty(column_name, allowEmpty)
            isNumeric = numeric_col.notna()
            valid_row = non_empty_row & isNumeric
            if allowNegative:
                alphanumeric = self.df[column_name].str.contains(r'[a-zA-Z]')
                self.vectorized_log_error(alphanumeric, column_name, "Please enter digits only!")

                bad_format = ~self.df[column_name].str.match(self.VALID_NEGATIVE_REGEX) & ~isNumeric & ~alphanumeric
                self.vectorized_log_error(bad_format, column_name,
                                          "Please ensure that there is no space between the negative sign and the number")
            else:
                non_numeric = non_empty_row & ~isNumeric
                self.vectorized_log_error(non_numeric, column_name, "Please enter digits and positive number only")

                negative = valid_row & (numeric_col < 0)
                self.vectorized_log_error(negative, column_name, "Negative numbers are not allowed")

            if haveMinimum and haveMaximum:
                minimum = int(param.get("min"))
                maximum = int(param.get("max"))
                if allowNegative:
                    not_in_range = valid_row & ~numeric_col.between(minimum, maximum)
                else:
                    not_in_range = valid_row & ~negative & ~numeric_col.between(minimum, maximum)
                self.vectorized_log_error(not_in_range, column_name, f"Please numeric value that is between the range of {minimum} - {maximum}")
        except ValueError:
            raise invalidMinMax from None

    def isEmail(self, column_name, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        ascii_row = ~(self.isASCII(column_name))
        mask = non_empty_row & ascii_row & ~self.df[column_name].str.match(self.EMAIL_PATTERN)
        self.vectorized_log_error(mask, column_name, "Please enter a valid email")

    def isDate(self, column_name, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        regex_match = self.df[column_name].str.match(self.DATE_REGEX)
        parsed_date = pd.to_datetime(self.df[column_name], format=self.DATE_FORMAT, errors="coerce")

        # not empty, but not match regex
        invalidFormat = non_empty_row & ~regex_match
        self.vectorized_log_error(invalidFormat, column_name,
                                  "Please add leading zero when it is single digit, eg. 01/01/2024")

        # not empty , match regex but not valid date
        invalidDate = non_empty_row & regex_match & parsed_date.isna()
        self.vectorized_log_error(invalidDate, column_name,
                          "Please ensure you have enter a correct format, day/month/year, and please double confirm on leap year")

    def isDuplicate(self, column_name, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        ascii_row = ~(self.isASCII(column_name))
        valid_row  = non_empty_row & ascii_row
        non_empty = self.df.loc[valid_row, column_name]
        duplicate_mask = non_empty.duplicated(keep=False)

        if not duplicate_mask.any():
            return  # No duplicates to log
        # Get unique duplicate values only
        dup_values = non_empty.loc[duplicate_mask].unique()

        for value in dup_values:
            matches = self.df.index[self.df[column_name] == value].tolist()
            locations = [self.get_a1_idx(idx, column_name) for idx in matches]
            self.error_log.append({
                "location": ", ".join(locations),
                "error": f"Has duplicate value: '{value}'"
            })

    def isPrefix(self, column_name, prefix, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        ascii_row = ~(self.isASCII(column_name))
        mask = non_empty_row & ascii_row & ~self.df[column_name].str.startswith(prefix)
        self.vectorized_log_error(mask, column_name, f"Please enter data that starts with {prefix}")

    # isEqual
    def isInOption(self, column_name, options, allowEmpty):
        non_empty_row = ~(self.isEmpty(column_name, allowEmpty))
        ascii_row = ~(self.isASCII(column_name))
        option_list = [option.strip() for option in options.split(",")]
        mask = non_empty_row & ascii_row & ~self.df[column_name].isin(option_list)
        self.vectorized_log_error(mask, column_name,
                                  f"Please only enter the options available in [{options}], AS EXACTLY AS IT IS")
