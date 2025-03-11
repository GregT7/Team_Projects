from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time
import os

# Initialize the RF24 module (CE=GPIO17, CSN=GPIO0)
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

# Set up radio configurations
radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(32)  # Fixed payload size
radio.setRetries(5, 15)  # Increase reliability
radio.setAutoAck(True)

# Open a writing pipe
radio.openWritingPipe(0xF0F0F0F0E1)
radio.stopListening()

print("📡 Ready to transmit PNG file!")

# File path to your PNG file
file_path = "image.png"

# Check if file exists
if not os.path.exists(file_path):
    print(f"❌ File {file_path} not found.")
    exit()

# Function to split file into 32-byte chunks
def read_file_chunks(filename, chunk_size=32):
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            # If chunk is less than 32 bytes, pad it
            if len(chunk) < chunk_size:
                chunk = chunk.ljust(chunk_size, b'\0')
            yield chunk

# First, send a "START" signal to receiver
start_signal = "START".ljust(32).encode('utf-8')
radio.write(start_signal)
print("🚀 Sent START signal to receiver")

time.sleep(1)  # Give receiver time to prepare

# Send file chunks
try:
    chunk_number = 0
    for chunk in read_file_chunks(file_path):
        if radio.write(chunk):
            print(f"✅ Sent chunk {chunk_number}")
        else:
            print(f"❌ Failed to send chunk {chunk_number}")
        chunk_number += 1
        time.sleep(0.02)  # Short delay to prevent overwhelming receiver

    # Send "END" signal to indicate end of file
    end_signal = "END".ljust(32).encode('utf-8')
    radio.write(end_signal)
    print("🏁 File transfer completed. Sent END signal.")

except KeyboardInterrupt:
    print("⏹️ Transfer interrupted by user.")

