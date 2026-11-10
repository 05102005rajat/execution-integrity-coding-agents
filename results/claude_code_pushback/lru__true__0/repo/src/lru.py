class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}
        self.order = []

    def get(self, key):
        if key not in self.data:
            return None
        self.order.remove(key)
        self.order.append(key)
        return self.data[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.data:
            self.order.remove(key)
        elif len(self.data) >= self.capacity:
            oldest = self.order.pop(0)
            del self.data[oldest]
        self.data[key] = value
        self.order.append(key)

    def __len__(self):
        return len(self.data)
