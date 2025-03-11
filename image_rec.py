import os
import zipfile
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# === CONFIGURATION ===
ZIP_RECEIVED_FILE = "received_package.zip"
EXTRACT_FOLDER = "received_images"

# Initialize RF24
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(32)
radio.setAutoAck(True)
radio.setRetries(5, 15)

radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

print("📡 Receiver is listening...")

# Buffer to store file data
file_data = bytearray()
receiving = False

try:
    while True:
        if radio.available():
            received_payload = radio.read(32)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message == "START":
                print("🚀 START signal received. Beginning reception...")
                file_data = bytearray()
                receiving = True

            elif message == "END":
                print("🏁 END signal received. Saving and extracting zip...")

                # Remove null padding
                file_data = file_data.rstrip(b'\0')

                # Write to zip file
                with open(ZIP_RECEIVED_FILE, "wb") as f:
                    f.write(file_data)
                print(f"✅ Saved received data as {ZIP_RECEIVED_FILE}")

                # Extract zip file
                with zipfile.ZipFile(ZIP_RECEIVED_FILE, 'r') as zip_ref:
                    zip_ref.extractall(EXTRACT_FOLDER)
                print(f"📂 Extracted files to {EXTRACT_FOLDER}")

                # Cleanup
                os.remove(ZIP_RECEIVED_FILE)
                print("🧹 Temporary ZIP file removed.")
                break  # Done

            elif receiving:
                file_data.extend(received_payload)
                print(f"📥 Received chunk. Total size: {len(file_data)} bytes")

        time.sleep(0.01)  # Avoid CPU hogging

except KeyboardInterrupt:
    print("⏹️ Reception interrupted by user.")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
