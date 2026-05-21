import struct

class StoreOperationTracker:
    """Tracks modified memory addresses and shows their current values"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StoreOperationTracker, cls).__new__(cls)
            cls._instance.modified_addresses = set()
        return cls._instance
    
    def log_store(self, address: str, value: str):
        """Log a modified memory address
        
        Args:
            address: hex address as string (16 chars)
            value: hex value as string (16 chars)
        """
        try:
            addr_int = int(address, 16)
            self.modified_addresses.add(address)
        except Exception as e:
            print(f"Error logging store operation: {e}")
    
    def get_modified_addresses(self):
        """Get all modified addresses"""
        return list(self.modified_addresses)
    
    def clear(self):
        """Clear all modified addresses"""
        self.modified_addresses = set()
    
    def reset(self):
        """Reset the tracker"""
        self.modified_addresses = set()


# Singleton instance
store_tracker = StoreOperationTracker()
