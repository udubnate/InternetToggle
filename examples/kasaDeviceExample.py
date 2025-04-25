import asyncio
import time
from Utilities.KasaDevice import KasaDevice

# Main execution
async def main():
    # Create instance of KasaDevice with default IP
    kasa = KasaDevice()
    await kasa.restart_device()

# Uncomment to discover and list all devices
# async def list_all():
#     kasa = KasaDevice()
#     await kasa.print_all_devices()
# asyncio.run(list_all())

# Run the main function
asyncio.run(main())