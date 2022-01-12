from typing import Collection, Optional, Union

from .Exceptions import EmptyExpressionHead
from .Types import Outcome


class Expression:

    def __init__(self, head: Union[Outcome, Collection[Outcome]], body: Optional[Collection[Outcome]] = None):
        if head is None:
            raise EmptyExpressionHead

        if body is None:
            body = []

        self._head = set(head) if not isinstance(head, Outcome) else {head}
        self._body = set(body) if not isinstance(body, Outcome) else {body}

    def __str__(self) -> str:
        if len(self._body) == 0:
            return f'P({", ".join(map(str, self._head))})'

        return f'P({", ".join(map(str, self._head))} | {", ".join(map(str, self._body))})'

    # getters
    def head_contains(self, outcome: Outcome) -> bool:
        return outcome in self._head

    def body_contains(self, outcome: Outcome) -> bool:
        return outcome in self._body

    def head(self) -> Collection[Outcome]:
        return self._head.copy()

    def body(self) -> Collection[Outcome]:
        return self._body.copy()

    # setters
    def add_to_head(self, outcome: Outcome) -> bool:
        if outcome in self._head:
            return False
        self._head.add(outcome)
        return True

    def add_to_body(self, outcome: Outcome) -> bool:
        if outcome in self._body:
            return False
        self._body.add(outcome)
        return True

    def remove_from_head(self, outcome: Outcome) -> bool:
        if outcome not in self._head:
            return False
        self._head.remove(outcome)
        return True

    def remove_from_body(self, outcome: Outcome) -> bool:
        if outcome not in self._body:
            return False
        self._body.remove(outcome)
        return True
