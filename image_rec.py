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
radio.setPayloadSize(32)
radio.setAutoAck(True)
radio.setRetries(5, 15)  # Optional but improves reliability

# Open a reading pipe (must match the sender's writing pipe)
radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

print("📡 Receiver is ready and listening...")

# File to save the received image
output_file_path = "received_image.png"

# Buffer to store incoming file data
file_data = bytearray()
receiving = False

try:
    while True:
        if radio.available():
            received_payload = radio.read(32)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message == "START":
                print("🚀 Start signal received. Beginning file reception...")
                file_data = bytearray()  # Clear buffer
                receiving = True

            elif message == "END":
                print("🏁 End signal received. Writing file to disk...")

                # Remove trailing null bytes if any (for the last chunk)
                file_data = file_data.rstrip(b'\0')

                # Write the received data to a file
                with open(output_file_path, "wb") as f:
                    f.write(file_data)

                print(f"✅ File saved as {output_file_path}")
                break  # Exit the loop after receiving complete file

            elif receiving:
                # Append chunk to buffer
                file_data.extend(received_payload)
                print(f"📥 Received chunk. Total size: {len(file_data)} bytes")

        time.sleep(0.01)  # Small delay to avoid hogging CPU

except KeyboardInterrupt:
    print("⏹️ Receiver stopped by user.")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
