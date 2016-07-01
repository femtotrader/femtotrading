#!/usr/bin/env python

"""
priority queue (heapq / heap queue)

https://docs.python.org/3/library/queue.html
https://docs.python.org/3/library/heapq.html
"""

from .compat import queue
import heapq


class UPriorityQueue:
    """
    Priority queue

    > pq = UPriorityQueue()
    > pq.enqueue("a", 10)
    > pq.enqueue("b", 5)
    > pq.enqueue("c", 15)
    > pq.enqueue("b2", 5)
    > pq.dequeues()
    ['b', 'b2']
    > pq.dequeues()
    ['a']
    > pq.dequeues()
    ['c']
    > pq.dequeues()
    ---------------------------------------------------------------------------
    Empty                                     Traceback (most recent call last)


    priority can also be datetime
    > import datetime
    > pq.enqueue("a", datetime.datetime(year=2016,month=1,day=10))
    > pq.enqueue("b", datetime.datetime(year=2016,month=1,day=5))
    > pq.enqueue("c", datetime.datetime(year=2016,month=1,day=15))
    > pq.enqueue("b2", datetime.datetime(year=2016,month=1,day=5))
    """

    def __init__(self, maxsize=0):
        self._pq = queue.PriorityQueue(maxsize=maxsize)

    @property
    def q(self):
        return self._pq.queue

    def enqueue(self, data, priority):
        self._pq.put((priority, data), block=False)

    def dequeue(self):
        """Remove the lowest priority key"""
        return self._pq.get(block=False)[1]

    def dequeues(self):
        """Remove and return a list with all the lowest priority keys"""
        lst_dequeued = []
        if len(self) == 0:
            raise queue.Empty
        first_priority = self.next_priority
        while(self.next_priority == first_priority):
            dequeued = self.dequeue()
            lst_dequeued.append(dequeued)
            if len(self) == 0:
                break
        return lst_dequeued

    def keys(self):
        for priority, key in self._pq.queue:
            yield key

    @property
    def next_priority(self):
        try:
            return heapq.nsmallest(1, self._pq.queue)[0][0]
        except IndexError:
            raise queue.Empty

    def __len__(self):
        return self._pq.qsize()
