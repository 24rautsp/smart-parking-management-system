"""
Smart Parking Management System - Linked List Module
Implements a custom Singly Linked List to maintain completed parking records.
"""

from typing import Optional, Dict, Any, List


class HistoryNode:
    """Represents a single completed parking session record node."""
    def __init__(self, record: Dict[str, Any]):
        self.record: Dict[str, Any] = record  # e.g., vehicle, slot, entry, exit, duration, fee
        self.next: Optional['HistoryNode'] = None


class HistoryLinkedList:
    """
    Custom Singly Linked List for completed parking history.

    DSA Characteristics:
    - Maintains head and tail pointers.
    - append() adds a new record at the end in O(1) time.
    - Eliminates the need for fixed-size preallocated contiguous memory.
    - Linear traversal O(K) for searches and reporting.
    """

    def __init__(self):
        self.head: Optional[HistoryNode] = None
        self.tail: Optional[HistoryNode] = None
        self._count: int = 0

    def is_empty(self) -> bool:
        """Checks if history list is empty. Time Complexity: O(1)"""
        return self.head is None

    def size(self) -> int:
        """Returns total historical records count. Time Complexity: O(1)"""
        return self._count

    def append(self, record: Dict[str, Any]) -> None:
        """
        Appends a completed parking session to the end of the linked list.
        Time Complexity: O(1)
        """
        new_node = HistoryNode(record)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._count += 1

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Traverses the linked list from head to tail to generate a list of records.
        Time Complexity: O(K) where K is number of records.
        """
        records = []
        current = self.head
        while current is not None:
            records.append(current.record)
            current = current.next
        return records

    def search_by_vehicle(self, vehicle_number: str) -> List[Dict[str, Any]]:
        """
        DSA Concept: Linear Search over Linked List - O(K)
        Finds all past parking sessions matching the given registration number.
        """
        target = vehicle_number.strip().upper()
        matches = []
        current = self.head
        while current is not None:
            if current.record.get("vehicle_number") == target:
                matches.append(current.record)
            current = current.next
        return matches

    def get_total_revenue(self) -> float:
        """
        Traverses nodes and sums total fees collected.
        Time Complexity: O(K)
        """
        total = 0.0
        current = self.head
        while current is not None:
            total += float(current.record.get("fee", 0.0))
            current = current.next
        return total

    def __repr__(self) -> str:
        return f"HistoryLinkedList(Count: {self._count})"


if __name__ == "__main__":
    print("=== Testing Linked List Module ===")
    history = HistoryLinkedList()
    print("Is empty:", history.is_empty())
    history.append({"vehicle_number": "KA-01-1111", "slot_id": 1, "duration_hours": 2.0, "fee": 40.0})
    history.append({"vehicle_number": "DL-02-2222", "slot_id": 2, "duration_hours": 1.5, "fee": 30.0})
    print("Size:", history.size())
    print("Total revenue:", history.get_total_revenue())
    print("Records:", history.to_list())
    print("Search KA-01-1111:", history.search_by_vehicle("KA-01-1111"))
