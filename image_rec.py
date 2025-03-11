import os
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"

if not os.path.exists(RECEIVE_FOLDER):
    os.makedirs(RECEIVE_FOLDER)

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

# Variables to handle current file
current_file_data = bytearray()
current_filename = None
chunks = {}

try:
    while True:
        if radio.available():
            received_payload = radio.read(32)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            # Detect start of file
            if message.startswith("START:"):
                current_filename = message.split(":", 1)[1].strip()
                current_file_data = bytearray()
                chunks = {}
                print(f"🚀 START receiving file: {current_filename}")

            # Detect end of file
            elif message.startswith("END:"):
                end_filename = message.split(":", 1)[1].strip()
                if current_filename == end_filename:
                    print(f"🏁 END receiving file: {current_filename}")

                    # Order chunks and assemble file
                    ordered_data = b''.join([chunks[i] for i in sorted(chunks.keys())]).rstrip(b'\0')

                    # Save file
                    output_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(output_path, "wb") as f:
                        f.write(ordered_data)
                    print(f"✅ File saved: {output_path}")

                current_filename = None
                current_file_data = bytearray()
                chunks = {}

            # Receiving chunks
            elif current_filename:
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data
                print(f"📥 Received chunk #{seq_num} of {current_filename}")

        time.sleep(0.01)  # Avoid CPU overuse

except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
