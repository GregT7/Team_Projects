from RF24 import RF24, rf24_datarate_e
import time

# Set up the RF24 communication on the sender
radio = RF24(17, 0)  # CE=GPIO17, CSN=GPIO0
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.setChannel(76)  # Must match the receiver's channel
radio.setPayloadSize(32)  # Use fixed payload size of 32 bytes

# Open writing pipe on the same address used by the receiver
radio.openWritingPipe(0xF0F0F0F0E1)
radio.stopListening()

# Allow the radio to settle before transmitting
time.sleep(0.1)

# Prepare the message to send.
# The library may automatically pad the message to 32 bytes.
message = "hello".encode('utf-8')
if radio.write(message):
    print("✅ Sent: 'hello'")
else:
    print("❌ Failed to send")
