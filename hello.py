from RF24 import RF24
import time

# Set up the RF24 communication
radio = RF24(17, 0)  # CE=GPIO22, CSN=SPI CE0 (GPIO8)
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(RF24.RF24_2MBPS)  # Set data rate
radio.openWritingPipe(0xF0F0F0F0E1)  # Unique pipe address
radio.stopListening()
time.sleep(0.1)

# Send "hello"
message = "hello".encode()  # Convert string to bytes
if radio.write(message):
    print("✅ Sent: 'hello'")
else:
    print("❌ Failed to send")
