import os
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# === CONFIGURATION ===
FOLDER_TO_SEND = "images"
PAYLOAD_SIZE = 32  # Max packet size to utilize
MAX_RETRIES = 300    # Maximum retries for each packet
INTER_PACKET_DELAY = 0.0001  # Delay between packets
CONTROL_SIGNAL_DELAY = .01  # Delay after control signals (START/END)
FILENAME_MAX_LEN = 32 - len("START:")  # Max filename length for control signals

# === Initialize RF24 ===
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(PAYLOAD_SIZE)
radio.setRetries(5, 15)
radio.setAutoAck(True)

radio.openWritingPipe(0xF0F0F0F0E1)
radio.stopListening()

print("📂 Ready to send images from folder:", FOLDER_TO_SEND)


# === Helper Function: Read file in chunks ===
def read_file_chunks(filename, chunk_size=PAYLOAD_SIZE - 2):  # 2 bytes reserved for chunk number
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


# === Helper Function: Safe filename truncation ===
def safe_filename(name, prefix="START:"):
    max_len = 32 - len(prefix)
    if len(name) > max_len:
        print(f"⚠️ Warning: File name '{name}' too long, truncating.")
        name = name[:max_len]
    return name


# === Helper Function: Send packet with retry ===
def send_with_retry(packet, description):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        if radio.write(packet):
            print(f"✅ {description}")
            return True
        retry_count += 1
        print(f"⚠️ Retry {retry_count}/{MAX_RETRIES} for {description}")
        time.sleep(0.1)  # Retry delay
    print(f"❌ Failed to send {description} after {MAX_RETRIES} retries")
    return False


# === Main Transmission Loop ===
try:
    for file_name in os.listdir(FOLDER_TO_SEND):
        full_path = os.path.join(FOLDER_TO_SEND, file_name)
        if not os.path.isfile(full_path):
            continue  # Skip non-files

        # Truncate filename safely for control signals
        safe_name = safe_filename(file_name)

        # --- Send START Signal ---
        start_signal = ("START:" + safe_name).ljust(32).encode('utf-8')
        if not send_with_retry(start_signal, f"START signal for {file_name}"):
            continue  # Skip file if failed to initiate
        time.sleep(CONTROL_SIGNAL_DELAY)

        # --- Send File Chunks ---
        chunk_number = 0
        for chunk in read_file_chunks(full_path):
            header = chunk_number.to_bytes(2, 'big')
            packet = header + chunk
            if len(packet) < PAYLOAD_SIZE:
                packet = packet.ljust(PAYLOAD_SIZE, b'\0')  # Pad to full size

            if not send_with_retry(packet, f"chunk #{chunk_number} of {file_name}"):
                print(f"⛔ Aborting file {file_name} due to repeated failures.")
                break  # Stop this file if chunk failed repeatedly

            chunk_number += 1
            time.sleep(INTER_PACKET_DELAY)  # Delay between packets

        # --- Send END Signal ---
        end_signal = ("END:" + safe_name).ljust(32).encode('utf-8')
        if send_with_retry(end_signal, f"END signal for {file_name}"):
            print(f"🏁 Finished sending file: {file_name}")
        else:
            print(f"⚠️ File {file_name} may not have been received correctly.")
        time.sleep(CONTROL_SIGNAL_DELAY)  # Space before next file

except KeyboardInterrupt:
    print("⏹️ Transmission interrupted by user.")
