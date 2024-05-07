import asyncio
import logging
import subprocess
from asyncio import QueueEmpty
from typing import Optional

from bleak import BleakClient

READ_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"

ReadTimeout = 5

async def run_bluetoothctl(command: str):
    subprocess.run("bluetoothctl", input=command.encode("ascii"), stdout=subprocess.DEVNULL)
    await asyncio.sleep(1)


class TransportBLE():
    def __init__(self, mac_addr: str):
        self._mac_addr = mac_addr
        self._client: Optional[BleakClient] = None

        self._read_queue = asyncio.Queue(maxsize=1024 * 1024)
        self._read_event = asyncio.Event()

    async def start(self):
        client = BleakClient(self._mac_addr)

        await run_bluetoothctl(f"disconnect {self._mac_addr}")
        await run_bluetoothctl(f"power on")

        await client.connect()
        await client.start_notify(READ_CHAR_UUID, self._on_data)

        self._client = client

        await asyncio.sleep(2)

    def close(self):
        if self._client is not None:
            self._client.disconnect()

    async def write(self, data: bytes):
        await self._client.write_gatt_char("0000ffe1-0000-1000-8000-00805f9b34fb", data, response=False)

    async def read(self, size: int) -> bytes:
        return await asyncio.wait_for(self._read_inner(size), ReadTimeout)

    def flush_input(self):
        while True:
            try:
                self._read_queue.get_nowait()
            except QueueEmpty:
                return

    async def _read_inner(self, size: int) -> bytes:
        data = [await self._read_queue.get()]
        for _ in range(size - 1):
            try:
                data.append(self._read_queue.get_nowait())
            except QueueEmpty:
                break
        return bytes(data)

    def _on_data(self, _: int, data: bytearray):
        for byte in data:
            self._read_queue.put_nowait(byte)
        self._read_event.set()


__all__ = [
    "TransportBLE",
]
