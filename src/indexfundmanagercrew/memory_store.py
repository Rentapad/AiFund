import json
import os

class MemoryStore:
    def __init__(self, filename='memory_store.json'):
        self.filename = filename
        # Initialize the memory file if it does not exist
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({}, f)

    def load_memory(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data

    def update_memory(self, key, value):
        memory = self.load_memory()
        memory[key] = value
        with open(self.filename, 'w') as f:
            json.dump(memory, f, indent=4)

    def get_memory(self, key):
        memory = self.load_memory()
        return memory.get(key, None)

# Example usage:
# store = MemoryStore()
# store.update_memory('last_run', '2023-10-05')
# print(store.get_memory('last_run')) 