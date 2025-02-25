from RF24 import RF24
import time

# Set up the RF24 communication
radio = RF24(17, 0)  # CE=GPIO22, CSN=SPI CE0 (GPIO8)
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.openReadingPipe(1, 0xF0F0F0F0E1)  # Unique pipe address
radio.startListening()

print("📡 Receiver is ready and listening...")

# Listening loop
while True:
    if radio.available():
        received_message = bytearray(32)  # NRF24L01 payload size
        radio.read(received_message, 32)
        message = received_message.decode().strip("\0")  # Decode and remove padding

        print(f"📥 Received: {message}")

        if message == "hello":
            print("✅ 'hello' message received!")

    time.sleep(0.05)
