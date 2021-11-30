from typing import Collection, Optional

from .Types import VMeasured

class Expression:

    def __init__(self, head: Collection[VMeasured], body: Optional[Collection[VMeasured]]):
        self._head = set(head)
        self._body = set(body) if body else set()

    # getters

    def head_contains(self, outcome: VMeasured) -> bool:
        return outcome in self._head
    
    def body_contains(self, outcome: VMeasured) -> bool:
        return outcome in self._body

    # setters

    def add_to_head(self, outcome: VMeasured) -> bool:
        if outcome in self._head:
            return False
        self._head.add(outcome)
        return True

    def add_to_body(self, outcome: VMeasured) -> bool:
        if outcome in self._body:
            return False
        self._body.add(outcome)
        return True

    def remove_from_head(self, outcome: VMeasured) -> bool:
        if outcome not in self._head:
            return False
        self._head.remove(outcome)
        return True
    
    def remove_from_body(self, outcome: VMeasured) -> bool:
        if outcome not in self._body:
            return False
        self._body.remove(outcome)
        return True
