import time

def blocking_cpu_task(duration):
    """Simulates a long-running CPU-bound task."""
    print(f"[{time.strftime('%H:%M:%S')}] CPU-bound task started (running for {duration}s)...")
    start_time = time.time()
    while (time.time() - start_time) <= duration:
        # Perform some actual computation to keep the CPU busy
        # Example: a simple calculation that doesn't terminate on its own
        _ = 1234567 * 7654321 
    print(f"[{time.strftime('%H:%M:%S')}] CPU-bound task finished.")

# Example usage (synchronous)
# print("Starting CPU-bound execution:")
# blocking_cpu_task(3)
# print("CPU-bound execution finished.")