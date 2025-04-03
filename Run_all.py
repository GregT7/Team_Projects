import subprocess
import os

# Path to the virtual environment's Python
venv_python = "./venv/bin/python"

try:
    print("🚀 Running classify_driver.py in virtual environment...")
    subprocess.run([venv_python, "demo_driver.py"], check=True)

    print("✅ demo_driver.py finished.")
    subprocess.run(["python", "Rename.py"], check=True)
    print("📡 Running Transmitter_final.py using global/default Python...")
    subprocess.run(["python", "Transmitter_final.py"], check=True)

    print("✅ Transmitter_final.py finished.")

except subprocess.CalledProcessError as e:
    print(f"❌ Command failed with return code {e.returncode}")
