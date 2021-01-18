import asyncio
from bleak import BleakScanner, BleakClient

received = asyncio.Event()


def notify_callback(sender: int, data: bytearray):
    global received
    print("received: {}: {}".format(sender, data))
    received.set()


async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == 'SldrOne':
            async with BleakClient(d.address) as client:
                print('Connecting to: {}'.format(d))
                print('connected: {}'.format(await client.connect()))
                IO_CTRL_CHARACTERISTIC_UUID = "7da5b2e6-071c-4601-9fde-ecaf291d0a04"
                IO_CTRL_READ_CHARACTERISTIC_UUID = "eaa8212a-3551-4e98-adeb-0b68957a215a"
                READ_CHARACTERISTIC_UUID = "c2720639-bdfc-4b8e-896d-b5bea0479976"
                WRITE_CHARACTERISTIC_UUID = "5a861ccb-687b-459a-af01-347792f07a0c"
                print('registering callback on READ_CHARACTERISTIC_UUID')
                asyncio.ensure_future(client.start_notify(READ_CHARACTERISTIC_UUID, notify_callback))
                print('registering callback on IO_CTRL_READ_CHARACTERISTIC_UUID')
                asyncio.ensure_future(client.start_notify(IO_CTRL_READ_CHARACTERISTIC_UUID, notify_callback))
                print('getting services')
                services = await client.get_services()
                print('writing')
                await client.write_gatt_char(IO_CTRL_CHARACTERISTIC_UUID, bytes(b'\x04\x09\x0c\xb0\x00\xc9')) #BT_ATT_OP_WRITE_REQ
                print('wrote')
                await asyncio.sleep(60)
                await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())