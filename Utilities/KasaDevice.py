from kasa import Discover, Module
import time

class KasaDevice:
    def __init__(self, ip_address="192.168.1.5"):
        self.ip_address = ip_address
    
    async def discover_devices(self):
        devices = await Discover.discover()
        return devices
    
    async def print_all_devices(self):
        devices = await self.discover_devices()
        for addr, dev in devices.items():
            print(f"{addr}: {dev}")
    
    async def turn_off(self):
        plug = await Discover.discover_single(self.ip_address)
        offstatus = await plug.turn_off()
        status = await plug.update()  # Fetch current state
        print(plug.is_on)
        return plug.is_on
    
    async def turn_on(self):
        plug = await Discover.discover_single(self.ip_address)
        onstatus = await plug.turn_on()
        status = await plug.update()  # Fetch current state
        print(plug.is_on)
        return plug.is_on
    
    async def restart_device(self):
        plug = await Discover.discover_single(self.ip_address)
        await plug.turn_off()
        print("Waiting 5 seconds before turning on...")
        time.sleep(5)
        print("Turning on the device...")
        await plug.turn_on()
        status = await plug.update()
        return status
