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

# Buffer to store chunks
chunks = {}
receiving = False

try:
    while True:
        if radio.available():
            received_payload = radio.read(32)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message == "START":
                print("🚀 START signal received. Beginning reception...")
                chunks = {}
                receiving = True

            elif message == "END":
                print("🏁 END signal received. Reassembling file...")

                # Reassemble data based on chunk numbers
                ordered_chunks = [chunks[i] for i in sorted(chunks.keys())]

                # Concatenate and strip padding
                file_data = b''.join(ordered_chunks).rstrip(b'\0')

                # Save to file
                with open(ZIP_RECEIVED_FILE, "wb") as f:
                    f.write(file_data)
                print(f"✅ Saved as {ZIP_RECEIVED_FILE}")

                # Extract zip
                with zipfile.ZipFile(ZIP_RECEIVED_FILE, 'r') as zip_ref:
                    zip_ref.extractall(EXTRACT_FOLDER)
                print(f"📂 Extracted files to {EXTRACT_FOLDER}")

                os.remove(ZIP_RECEIVED_FILE)
                print("🧹 Temporary ZIP file removed.")
                break  # Done

            elif receiving:
                # Extract sequence number and chunk
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data
                print(f"📥 Received chunk #{seq_num}")

        time.sleep(0.01)  # Avoid CPU hogging

except KeyboardInterrupt:
    print("⏹️ Reception interrupted by user.")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
