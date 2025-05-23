from RF24 import RF24, rf24_datarate_e
import time
import os

# Set up the RF24 communication
radio = RF24(17, 0)  # CE=GPIO22, CSN=SPI CE0 (GPIO8)
radio.begin()
radio.setPALevel(2)  # Set power level
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)  # Set data rate
radio.openWritingPipe(0xF0F0F0F0E1)  # Unique pipe address
radio.stopListening()
time.sleep(0.1)

# Function to send an image in chunks
def send_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    print(f"Sending {len(image_data)} bytes of image data...")

    # Send the total number of chunks first
    chunk_size = 32  # NRF24L01 max payload size
    total_chunks = (len(image_data) // chunk_size) + 1
    header = str(total_chunks).encode().ljust(chunk_size, b'\0')  # Pad to 32 bytes
    radio.write(header)
    time.sleep(0.2)  # Allow receiver to process header

    # Send the image data in chunks
    for i in range(0, len(image_data), chunk_size):
        chunk = image_data[i:i+chunk_size]
        radio.write(chunk)
        print(f"Sent chunk {i//chunk_size + 1} of {total_chunks}")
        time.sleep(0.05)  # Small delay for stability

    print("✅ Image transmission complete!")

# Specify the image to send
image_path = "/home/admin/darksaber/test.jpg"  # Change to your actual image file
send_image(image_path)
