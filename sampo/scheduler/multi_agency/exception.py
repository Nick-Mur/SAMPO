"""Exceptions for multi-agency scheduling.

Исключения для многопользовательского планирования.
"""


class NoSufficientAgents(Exception):
    """Raised when manager lacks agents.

    Возникает, когда менеджеру не хватает агентов.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
