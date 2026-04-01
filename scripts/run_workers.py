#!/usr/bin/env python3
"""
Run 20 workers in parallel using subprocess
"""
import subprocess
import sys
import os

os.chdir(r"C:\NDT\PJ\MediSign_AI\scripts")

processes = []
for i in range(20):
    print(f"Starting worker {i}...")
    p = subprocess.Popen(
        [sys.executable, "convert_medical_multi.py", str(i), "20"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(p)

print(f"Started {len(processes)} workers")

# Wait for all
for i, p in enumerate(processes):
    p.wait()
    print(f"Worker {i} done")
