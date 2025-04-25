import asyncio
import time
from Utilities.KasaDevice import KasaDevice
import os
from dotenv import load_dotenv

print("hello")


# Main execution
async def main():
    # Create instance of KasaDevice with the specific IP
    kasa = KasaDevice(ip_address=os.getenv("KASA_PLUG_IP"))
    await kasa.restart_device()

# Uncomment to discover and list all devices
# async def list_all():
#     kasa = KasaDevice()
#     await kasa.print_all_devices()
# asyncio.run(list_all())

# Run the main function
asyncio.run(main())