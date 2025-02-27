from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# Initialize the RF24 module (CE=GPIO17, CSN=GPIO0)
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

# Set up radio configurations
radio.setPALevel(RF24_PA_LOW)  # Use RF24_PA_HIGH if range is an issue
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)  # Must match sender’s channel
radio.setPayloadSize(32)  # Must match sender’s payload size

# Open a reading pipe (must match sender’s writing pipe)
radio.openReadingPipe(1, 0xF0F0F0F0E1)

# Set as a receiver
radio.startListening()

# Flush any old data from buffer
radio.flush_rx()

print("📡 Receiver is ready and listening...")

file_name = "received_messages.txt"

try:
    while True:
        if radio.available():
            # Prepare a 32-byte buffer
            received_message = radio.read(32)
            

            # Decode and strip null padding
            message = received_message.decode("utf-8").strip("\0")

            if message:
                print(f"📥 Received: {message}")
                with open(file_name, "a") as f:
                    f.write(message + "\n")

                if message == "hello":
                    print("✅ 'hello' message received!")
except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")
