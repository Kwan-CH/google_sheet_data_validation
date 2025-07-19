class missingConfigJSON(Exception):
    def __init__(self):
        super().__init__("\nIt seems you haven\'t include the config.json file into json directory as mentioned in readme.md\n"
                "Please refer to the steps and fix the issue")

class missingField(Exception):
    def __init__(self, field):
        super().__init__(f"\nIt seems you haven\'t include the {field} field into the config.json as mentioned in readme.md\n"
                "Please refer to the steps and fix the issue")

class unrecognizedRule(Exception):
    def __init__(self, rule):
        super().__init__(f"\nIt seems you wrote a rule called {rule} that does not exist, please refer to checkMap.json to enter the correct rule")
