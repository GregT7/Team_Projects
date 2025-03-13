import os
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"
PAYLOAD_SIZE = 152  # Match this with sender's payload size

# Create receive folder if it doesn't exist
os.makedirs(RECEIVE_FOLDER, exist_ok=True)

# === Initialize RF24 ===
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(PAYLOAD_SIZE)
radio.setAutoAck(True)
radio.setRetries(5, 15)

radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

print("📡 Receiver is listening...")

# === Variables to manage file reception ===
current_file_data = bytearray()
current_filename = None
chunks = {}

try:
    while True:
        if radio.available():
            received_payload = radio.read(PAYLOAD_SIZE)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            # --- Handle START signal ---
            if message.startswith("START:"):
                current_filename = message.split(":", 1)[1].strip()
                current_file_data = bytearray()
                chunks = {}
                print(f"🚀 START receiving file: {current_filename}")

            # --- Handle END signal ---
            elif message.startswith("END:"):
                end_filename = message.split(":", 1)[1].strip()
                if current_filename == end_filename:
                    print(f"🏁 END receiving file: {current_filename}")

                    # Order and combine chunks
                    ordered_data = b''.join([chunks[i] for i in sorted(chunks.keys())]).rstrip(b'\0')

                    # Save assembled file
                    output_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(output_path, "wb") as f:
                        f.write(ordered_data)
                    print(f"✅ File saved: {output_path}")

                # Reset after completion
                current_filename = None
                current_file_data = bytearray()
                chunks = {}

            # --- Handle Data Chunks ---
            elif current_filename and len(received_payload) >= 2:
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data
                print(f"📥 Received chunk #{seq_num} of {current_filename}")

        time.sleep(0.01)  # Small delay to prevent CPU overuse

except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
