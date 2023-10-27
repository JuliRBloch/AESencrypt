import serial
import time

class ArduinoCommunicator:
    def __init__(self, port='COM4', baud_rate=115200):
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # A short delay after initializing the connection
        self._read_from_arduino()  # Clear out initial messages

    def send_data(self, data):
        self.ser.write(data.encode())
        return self._read_from_arduino()

    def _read_from_arduino(self):
        responses = []
        start_time = time.time()
        while True:
            # If more than 5 seconds have passed, break out of the loop
            if time.time() - start_time > 5:
                break
            raw_data = self.ser.readline()
            try:
                response = raw_data.decode().strip()
            except UnicodeDecodeError:
                response = raw_data.hex()  # or whatever alternate strategy you prefer
            if response:
                responses.append(response)
        return responses


    def close(self):
        self.ser.close()
        
    # Add these methods for the context manager protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()



def main():
    # Initialize the ArduinoCommunicator
    with ArduinoCommunicator() as arduino:
        # We don't really need the initialization message(s) based on the Arduino code provided.
        action = input("Choose an action: (E)ncrypt or (D)ecrypt? ").strip().lower()

        if action == 'e':
            # Encrypt
            message = input("Enter the message you want to encrypt (16 characters): ")
            if len(message) != 16:
                print("The message must be exactly 16 characters long.")
                return

            # Set the state matrix
            responses = arduino.send_data("0" + message)
            for resp in responses:
                print(resp)

            # Send encrypt command
            responses = arduino.send_data("1")
            for resp in responses:
                print(resp)

            # Get the encrypted result
            responses = arduino.send_data("2")
            for resp in responses:
                if all(c in string.printable for c in resp):  # import string at the top
                    print("Decrypted message from Arduino:", resp)
                else:
                    print("Hexadecimal output from Arduino:", resp)

        elif action == 'd':
            # Decrypt
            message = input("Enter the message you want to decrypt (16 bytes in HEX format, 32 characters): ")
            if len(message) != 32:
                print("The message must be exactly 32 characters long in HEX format.")
                return

            # Set the state matrix
            responses = arduino.send_data("0" + message)
            for resp in responses:
                print(resp)

            # Send decrypt command
            responses = arduino.send_data("3")
            for resp in responses:
                print(resp)

            # Get the decrypted result
            responses = arduino.send_data("2")
            for resp in responses:
                print("Decrypted message from Arduino:", resp)

        else:
            print("Invalid choice.")

    
    arduino.close()

if __name__ == "__main__":
    main()





