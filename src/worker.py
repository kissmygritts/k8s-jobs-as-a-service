# worker.py
import os
import time
import subprocess

def main():
    job_id = os.environ.get('JOB_ID', 'unknown')
    message = os.environ.get('MESSAGE', 'Hello World')
    
    print(f"[Job {job_id}] Starting work...")
    print(f"[Job {job_id}] Processing message: {message}")
    
    # Simulate your fsim process
    # In your case, this would be:
    # subprocess.run(["fsim", "cmdx.cmdx"])
    
    print(f"[Job {job_id}] Simulating CPU-intensive work...")
    time.sleep(10)  # Simulate work
    
    print(f"[Job {job_id}] Work completed successfully!")
    print(f"[Job {job_id}] Results: Processed '{message}' in 10 seconds")

if __name__ == "__main__":
    main()