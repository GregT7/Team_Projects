from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# Initialize the RF24 module (CE=GPIO17, CSN=GPIO0)
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

# Set up radio configurations
radio.setPALevel(RF24_PA_LOW)  # Use RF24_PA_HIGH for long range
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Fastest transmission speed
radio.setChannel(76)  # Ensure the receiver is on the same channel
radio.setPayloadSize(32)  # Fixed payload size

# Open a writing pipe (must match the receiver’s reading pipe)
radio.openWritingPipe(0xF0F0F0F0E1)

# Set as a transmitter
radio.stopListening()

print("📡 Sender is ready to transmit!")

# Allow NRF24L01 to stabilize
time.sleep(0.1)

# Messages to send
messages = ["hello", "how are you?", "this is a test", "bye"]

try:
    while True:
        for message in messages:
            encoded_msg = message.ljust(32).encode("utf-8")  # Ensure 32-byte payload
            if radio.write(encoded_msg):
                print(f"✅ Sent: {message}")
            else:
                print("❌ Failed to send")
            
            time.sleep(2)  # Wait before sending the next message
except KeyboardInterrupt:
    print("⏹️ Sender stopped by user.")
