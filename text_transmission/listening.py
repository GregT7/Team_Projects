from RF24 import RF24, rf24_datarate_e
import time

# Set up the RF24 communication on the receiver
radio = RF24(17, 0)  # CE=GPIO17, CSN=GPIO0
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.setChannel(76)  # Explicitly set channel
radio.setPayloadSize(32)  # Use fixed payload size of 32 bytes

# Open reading pipe on the agreed address
radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

print("📡 Receiver is ready and listening...")

file_name = "received_messages.txt"

try:
    while True:
        if radio.available():
            # Prepare a buffer for a 32-byte payload
            received_message = bytearray(32)
            radio.read(len(received_message))  # The radio fills the buffer in place
            # Decode and strip any null padding
            message = received_message.decode('utf-8').strip('\0')
            print(f"📥 Received: {message}")
            with open(file_name, "a") as f:
                f.write(message + "\n")
            if message == "hello":
                print("✅ 'hello' message received!")
except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")
