"""
Smart Parking Management System - Waiting Queue Module
Implements a custom FIFO (First-In, First-Out) Queue using linked nodes.
"""

from typing import Optional, List, Any


class QueueNode:
    """Represents an individual node in the Waiting Queue."""
    def __init__(self, data: str):
        self.data: str = data           # Vehicle registration number
        self.next: Optional['QueueNode'] = None


class WaitingQueue:
    """
    Custom FIFO (First-In, First-Out) Queue implementation.

    DSA Characteristics:
    - Maintains front and rear pointers.
    - enqueue() inserts at rear in O(1) time.
    - dequeue() removes from front in O(1) time.
    - peek() inspects front element in O(1) time.
    - Avoids Python list's O(N) pop(0) overhead.
    """

    def __init__(self):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._count: int = 0

    def is_empty(self) -> bool:
        """Checks if the queue is empty. Time Complexity: O(1)"""
        return self.front is None

    def size(self) -> int:
        """Returns the total number of waiting vehicles. Time Complexity: O(1)"""
        return self._count

    def enqueue(self, vehicle_number: str) -> None:
        """
        Adds a vehicle to the rear of the waiting queue.
        Time Complexity: O(1)
        """
        normalized_plate = vehicle_number.strip().upper()
        new_node = QueueNode(normalized_plate)

        if self.rear is None:
            # Queue is empty: new node is both front and rear
            self.front = new_node
            self.rear = new_node
        else:
            # Append new node after current rear and move rear pointer
            self.rear.next = new_node
            self.rear = new_node

        self._count += 1

    def dequeue(self) -> Optional[str]:
        """
        Removes and returns the vehicle from the front of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None

        dequeued_plate = self.front.data
        self.front = self.front.next

        # If queue became empty after removal, reset rear pointer
        if self.front is None:
            self.rear = None

        self._count -= 1
        return dequeued_plate

    def peek(self) -> Optional[str]:
        """
        Inspects the first waiting vehicle without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.front.data

    def contains(self, vehicle_number: str) -> bool:
        """
        Checks if a vehicle is already waiting in the queue.
        Time Complexity: O(M) where M is waiting vehicles.
        """
        normalized = vehicle_number.strip().upper()
        current = self.front
        while current is not None:
            if current.data == normalized:
                return True
            current = current.next
        return False

    def to_list(self) -> List[str]:
        """
        Traverses the queue and returns elements as a Python list.
        Time Complexity: O(M)
        """
        result = []
        current = self.front
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __repr__(self) -> str:
        return f"WaitingQueue(Count: {self._count}, Vehicles: {self.to_list()})"


if __name__ == "__main__":
    print("=== Testing Queue Module ===")
    q = WaitingQueue()
    print("Is empty:", q.is_empty())
    q.enqueue("KA-01-1111")
    q.enqueue("DL-02-2222")
    q.enqueue("MH-03-3333")
    print("Queue state:", q)
    print("Front vehicle (peek):", q.peek())
    print("Size:", q.size())
    print("Contains DL-02-2222:", q.contains("DL-02-2222"))
    print("Contains UP-04-4444:", q.contains("UP-04-4444"))
    print("Dequeued:", q.dequeue())
    print("Queue after 1 dequeue:", q)
