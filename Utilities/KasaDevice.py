from kasa import Discover
import time
from Utilities.Logger import Logger

class KasaDevice:
    def __init__(self, ip_address="192.168.1.5"):
        self.ip_address = ip_address
        self.logger = Logger("KasaDevice")
    
    async def discover_devices(self):
        self.logger.debug("Discovering Kasa devices on the network...")
        devices = await Discover.discover()
        self.logger.debug(f"Found {len(devices)} devices")
        return devices
    
    async def print_all_devices(self):
        devices = await self.discover_devices()
        for addr, dev in devices.items():
            self.logger.info(f"{addr}: {dev}")
    
    async def turn_off(self):
        self.logger.info(f"Turning off device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        offstatus = await plug.turn_off()
        status = await plug.update()  # Fetch current state
        self.logger.debug(f"Device is on: {plug.is_on}")
        return plug.is_on
    
    async def turn_on(self):
        self.logger.info(f"Turning on device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        onstatus = await plug.turn_on()
        status = await plug.update()  # Fetch current state
        self.logger.debug(f"Device is on: {plug.is_on}")
        return plug.is_on
    
    async def restart_device(self):
        self.logger.info(f"Restarting device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        await plug.turn_off()
        self.logger.info("Waiting 5 seconds before turning on...")
        time.sleep(5)
        self.logger.info("Turning on the device...")
        await plug.turn_on()
        status = await plug.update()
        return status
