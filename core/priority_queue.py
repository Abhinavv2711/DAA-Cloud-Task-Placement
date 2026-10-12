"""
Custom Priority Queue Implementation using a Binary Min-Heap.
Provides O(log N) push, pop, and decrease-key operations via an internal index lookup table.
"""

from typing import Any, Dict, List, Optional, Tuple


class PriorityQueue:
    """
    Min-Priority Queue backed by a binary heap with an item-to-index map.
    Enables O(log N) decrease_key operations required by Prim's and Dijkstra's algorithms.
    """

    def __init__(self):
        # Array of tuples: (priority, item)
        self.heap: List[Tuple[float, Any]] = []
        # Mapping from item to its current index in self.heap
        self.entry_finder: Dict[Any, int] = {}

    def __len__(self) -> int:
        return len(self.heap)

    def is_empty__(self) -> bool:
        return len(self.heap) == 0

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def __contains__(self, item: Any) -> bool:
        return item in self.entry_finder

    def _swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.entry_finder[self.heap[i][1]] = i
        self.entry_finder[self.heap[j][1]] = j

    def _sift_up(self, idx: int) -> None:
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx][0] < self.heap[parent][0]:
            self._swap(idx, parent)
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int) -> None:
        n = len(self.heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < n and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < n and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break

    def push(self, item: Any, priority: float) -> None:
        """Insert a new item with given priority in O(log N)."""
        if item in self.entry_finder:
            self.decrease_key(item, priority)
            return

        idx = len(self.heap)
        self.heap.append((priority, item))
        self.entry_finder[item] = idx
        self._sift_up(idx)

    def pop(self) -> Tuple[Any, float]:
        """Remove and return (item, priority) with the minimum priority in O(log N)."""
        if self.is_empty():
            raise IndexError("pop from empty PriorityQueue")

        min_priority, min_item = self.heap[0]
        last_priority, last_item = self.heap.pop()
        del self.entry_finder[min_item]

        if self.heap:
            self.heap[0] = (last_priority, last_item)
            self.entry_finder[last_item] = 0
            self._sift_down(0)

        return min_item, min_priority

    def peek(self) -> Tuple[Any, float]:
        """Return (item, priority) of the minimum element without removing it in O(1)."""
        if self.is_empty():
            raise IndexError("peek from empty PriorityQueue")
        p, item = self.heap[0]
        return item, p

    def get_priority(self, item: Any) -> Optional[float]:
        """Return the current priority of item, or None if not in queue."""
        if item in self.entry_finder:
            return self.heap[self.entry_finder[item]][0]
        return None

    def decrease_key(self, item: Any, new_priority: float) -> None:
        """
        Decrease the priority of an existing item in O(log N).
        If new_priority is greater than current priority, raises ValueError or updates only if smaller.
        """
        if item not in self.entry_finder:
            self.push(item, new_priority)
            return

        idx = self.entry_finder[item]
        current_priority = self.heap[idx][0]
        if new_priority < current_priority:
            self.heap[idx] = (new_priority, item)
            self._sift_up(idx)
        elif new_priority > current_priority:
            # For general updates
            self.heap[idx] = (new_priority, item)
            self._sift_down(idx)


# Alias for naming consistency
MinHeap = PriorityQueue
