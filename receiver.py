from RF24 import RF24, rf24_datarate_e
import time

# Set up the RF24 communication
radio = RF24(17, 0)  # CE=GPIO22, CSN=SPI CE0 (GPIO8)
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.openReadingPipe(1, 0xF0F0F0F0E1)  # Unique pipe address
radio.startListening()

print("📡 Receiver is ready and listening...")

# Function to save the received image
def write_image(data):
    with open("received_image.jpg", "wb") as f:
        f.write(data)

# Listening loop
received_data = bytearray()
expected_chunks = None
received_chunks = 0

while True:
    if radio.available():
        buffer = bytearray(32)  # NRF24L01 payload size
        radio.read(buffer, 32)


        # First received packet contains the expected number of chunks
        if expected_chunks is None:
            try:
                expected_chunks = int(buffer.decode().strip('\0'))
                print(f"🛜 Expecting {expected_chunks} chunks...")
            except ValueError:
                print("⚠️ Failed to decode chunk count.")
            continue

        # Append received chunk to the image data
        received_data.extend(buffer)
        received_chunks += 1
        print(f"📦 Received chunk {received_chunks}/{expected_chunks}")

        # Once all chunks are received, save the image
        if received_chunks >= expected_chunks:
            print("✅ Image received successfully. Saving to file...")
            write_image(received_data)
            print("🖼️ Image saved as 'received_image.jpg'")
            break  # Exit loop after full image is received

    time.sleep(0.05)
