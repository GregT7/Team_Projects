from RF24 import RF24, rf24_datarate_e
import time

# Set up the RF24 communication
radio = RF24(17, 0)  # CE=GPIO17, CSN=GPIO0 (adjust GPIO pins if needed)
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.openReadingPipe(1, 0xF0F0F0F0E1)  # Unique pipe address
radio.startListening()

print("📡 Receiver is ready and listening...")

# Define the file to save messages
file_name = "received_messages.txt"

try:
    # Listening loop
    while True:
        if radio.available():
            received_message = bytearray(32)  # NRF24L01 payload size
            radio.read(len(received_message))  # Only pass the length to read
            message = received_message.decode().strip("\0")  # Decode and remove padding

            print(f"📥 Received: {message}")

            # Save the message to a file
            with open(file_name, "a") as f:
                f.write(message + "\n")  # Append the message with a newline

            if message == "hello":
                print("✅ 'hello' message received!")

except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")
