import asyncio
import socket
import threading
from bleak import BleakClient

VGATE_ADDRESS = "A7057982-60F3-8958-FB7D-AA4A8604228C"

NOTIFY_UUID = "00002af0-0000-1000-8000-00805f9b34fb"
WRITE_UUID  = "00002af1-0000-1000-8000-00805f9b34fb"

TCP_HOST = "localhost"
TCP_PORT = 35000

class VgateBridge:

    def __init__(self):
        self.client     = None
        self.tcp_conn   = None
        self.loop       = None
        self.connected  = False

    def handle_notification(self, sender, data):
        """Vgate sent data → forward to python-obd via TCP."""
        if self.tcp_conn:
            try:
                self.tcp_conn.sendall(data)
            except Exception as e:
                print(f"TCP send error: {e}")

    def tcp_listener(self):
        """Wait for python-obd to connect on TCP, then forward its
        commands to the Vgate over BLE."""
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((TCP_HOST, TCP_PORT))
        server.listen(1)

        print(f"Bridge ready — waiting for python-obd on "
              f"{TCP_HOST}:{TCP_PORT}...")

        self.tcp_conn, addr = server.accept()
        print(f"python-obd connected from {addr}")

        while True:
            try:
                data = self.tcp_conn.recv(1024)
                if not data:
                    break

                # Forward command to Vgate over BLE
                asyncio.run_coroutine_threadsafe(
                    self.client.write_gatt_char(
                        WRITE_UUID,
                        data,
                        response=False
                    ),
                    self.loop
                ).result(timeout=5)

            except Exception as e:
                print(f"TCP receive error: {e}")
                break

    async def run(self):
        self.loop = asyncio.get_event_loop()

        print(f"Connecting to IOS-Vlink...")

        async with BleakClient(
            VGATE_ADDRESS,
            timeout=20
        ) as client:

            self.client    = client
            self.connected = True
            print(f"BLE connected to Vgate")

            # Subscribe to receive data from Vgate
            await client.start_notify(
                NOTIFY_UUID,
                self.handle_notification
            )
            print(f"Subscribed to notifications")

            # Start TCP bridge in background thread
            tcp_thread = threading.Thread(
                target=self.tcp_listener,
                daemon=True
            )
            tcp_thread.start()

            # Keep the BLE connection alive indefinitely
            print("\nBridge is running.")
            print("Now run vgate_test.py in a new terminal tab.\n")

            while self.connected:
                await asyncio.sleep(0.1)

if __name__ == "__main__":
    bridge = VgateBridge()
    asyncio.run(bridge.run())