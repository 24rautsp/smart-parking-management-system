"""
Smart Parking Management System - Action Stack Module
Implements a custom LIFO (Last-In, First-Out) Stack for action history
and undo operations using linked nodes.
"""

from typing import Optional, Dict, Any, List


class StackNode:
    """Represents a node in the Action Stack."""
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data     # Action payload dictionary
        self.next: Optional['StackNode'] = None


class ActionStack:
    """
    Custom LIFO (Last-In, First-Out) Stack implementation.

    DSA Characteristics:
    - Maintains a `top` pointer.
    - push() prepends to top in O(1) time.
    - pop() removes and returns top item in O(1) time.
    - peek() reads top item in O(1) time without removing it.
    - Used to record recent operations and support Undo.
    """

    def __init__(self):
        self.top: Optional[StackNode] = None
        self._count: int = 0

    def is_empty(self) -> bool:
        """Checks if stack has no actions. Time Complexity: O(1)"""
        return self.top is None

    def size(self) -> int:
        """Returns total number of stacked actions. Time Complexity: O(1)"""
        return self._count

    def push(self, action: Dict[str, Any]) -> None:
        """
        Pushes an action onto the top of the stack.
        Time Complexity: O(1)
        """
        new_node = StackNode(action)
        new_node.next = self.top
        self.top = new_node
        self._count += 1

    def pop(self) -> Optional[Dict[str, Any]]:
        """
        Removes and returns the most recent action from top of stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None

        action_data = self.top.data
        self.top = self.top.next
        self._count -= 1
        return action_data

    def peek(self) -> Optional[Dict[str, Any]]:
        """
        Inspects the top action without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.top.data

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Traverses stack from top (most recent) to bottom (oldest).
        Time Complexity: O(S) where S is stack depth.
        """
        result = []
        current = self.top
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __repr__(self) -> str:
        return f"ActionStack(Count: {self._count})"


if __name__ == "__main__":
    print("=== Testing Stack Module ===")
    s = ActionStack()
    print("Is empty:", s.is_empty())
    s.push({"action": "PARK", "vehicle": "KA-01-1111", "slot_id": 1})
    s.push({"action": "PARK", "vehicle": "DL-02-2222", "slot_id": 2})
    print("Stack size:", s.size())
    print("Peek top:", s.peek())
    popped = s.pop()
    print("Popped top action:", popped)
    print("New top after pop:", s.peek())
