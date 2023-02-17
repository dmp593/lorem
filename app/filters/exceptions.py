class FilterOperatorNotExistsError(RuntimeError):
    def __init__(self, operator: str, registry: dict, *args: object) -> None:
        self.invalid_operator = operator
        self.allowed_operators = list(registry.keys())
        
        super().__init__(f"Invalid filter operator: '{operator}'. Allowed: {', '.join(self.allowed_operators)}", *args)


class FilterError(RuntimeError):
    def __init__(self, key: str, value: any, reason: Exception, *args: object) -> None:
        self.key = key
        self.value = value
        self.reason = reason
        super().__init__(f"Error Applying filter: {key}={value}. Reason: {reason}", *args)
