from kasa import Discover
import time
import os
from Utilities.Logger import Logger

class KasaDevice:
    def __init__(self, ip_address="192.168.1.5"):
        self.ip_address = ip_address
        self.logger = Logger("KasaDevice")
        self.audit_mode = os.getenv("AUDIT_MODE", "False").lower() in ("true", "1", "t", "yes")
        if self.audit_mode:
            self.logger.info("Running in AUDIT MODE - no actual device interactions will occur")
    
    async def discover_devices(self):
        if self.audit_mode:
            self.logger.debug("[AUDIT] Simulating device discovery...")
            return {"192.168.1.5": "Simulated Kasa device"}
        
        self.logger.debug("Discovering Kasa devices on the network...")
        devices = await Discover.discover()
        self.logger.debug(f"Found {len(devices)} devices")
        return devices
    
    async def print_all_devices(self):
        devices = await self.discover_devices()
        for addr, dev in devices.items():
            self.logger.info(f"{addr}: {dev}")
    
    async def turn_off(self):
        if self.audit_mode:
            self.logger.info(f"[AUDIT] Simulating turning off device at {self.ip_address}")
            return False  # Simulating device is off
        
        self.logger.info(f"Turning off device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        offstatus = await plug.turn_off()
        status = await plug.update()  # Fetch current state
        self.logger.debug(f"Device is on: {plug.is_on}")
        return plug.is_on
    
    async def turn_on(self):
        if self.audit_mode:
            self.logger.info(f"[AUDIT] Simulating turning on device at {self.ip_address}")
            return True  # Simulating device is on
        
        self.logger.info(f"Turning on device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        onstatus = await plug.turn_on()
        status = await plug.update()  # Fetch current state
        self.logger.debug(f"Device is on: {plug.is_on}")
        return plug.is_on
    
    async def restart_device(self):
        if self.audit_mode:
            self.logger.info(f"[AUDIT] Simulating restart of device at {self.ip_address}")
            self.logger.info("[AUDIT] Simulating turning off device...")
            self.logger.info("[AUDIT] Waiting 5 seconds before simulating turn on...")
            time.sleep(5)
            self.logger.info("[AUDIT] Simulating turning on device...")
            return {"system": {"get_sysinfo": {"relay_state": 1}}}  # Simulated status response
        
        self.logger.info(f"Restarting device at {self.ip_address}")
        plug = await Discover.discover_single(self.ip_address)
        await plug.turn_off()
        self.logger.info("Waiting 5 seconds before turning on...")
        time.sleep(5)
        self.logger.info("Turning on the device...")
        await plug.turn_on()
        status = await plug.update()
        return status
