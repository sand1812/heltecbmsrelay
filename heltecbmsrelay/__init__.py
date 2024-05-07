import argparse
import json
import asyncio
from .Transports import TransportBLE

async def doit():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device",
                        help="MAC Address",
                        type=str, required=True)
    parser.add_argument("--json", help="JSON output instead of Pretty Output", action="store_true")
    parser.add_argument("--debug", help="Enable debug", action="store_true")
    args = parser.parse_args()

    if args.debug : DEBUG=1    
    
    transport = TransportBLE(args.device)
    await transport.start()
    client = HeltecBMSClient(transport)    

    try:            
        infos = await client.read_infos()
        if args.json:
            print(json.dumps(infos, indent = 4))
        else :
            print("SoC = %d%%" % infos["soc"])
            print("Battery Voltage = %.2fV" % infos["vbat"])
            print("Current = %.2fA" % infos["current"])
            print("Temp1 = %.2f°C" % infos["t1"])
            print("Temp2 = %.2f°C" % infos["t2"])
            print("Cell1 Voltage = %.4fV" % infos["cell1"])
            print("Cell2 Voltage = %.4fV" % infos["cell2"])
            print("Cell3 Voltage = %.4fV" % infos["cell3"])
            print("Cell4 Voltage = %.4fV" % infos["cell4"])
            print("Cell5 Voltage = %.4fV" % infos["cell5"])
            print("Cell6 Voltage = %.4fV" % infos["cell6"])
            print("Cell7 Voltage = %.4fV" % infos["cell7"])
            print("Cell8 Voltage = %.4fV" % infos["cell8"])
            print("Cell9 Voltage = %.4fV" % infos["cell9"])
            print("Cell10 Voltage = %.4fV" % infos["cell10"])
            print("Cell11 Voltage = %.4fV" % infos["cell11"])
            print("Cell12 Voltage = %.4fV" % infos["cell12"])
            print("Cell13 Voltage = %.4fV" % infos["cell13"])
            print("Cell14 Voltage = %.4fV" % infos["cell14"])
            print("Cell15 Voltage = %.4fV" % infos["cell15"])
            print("Cell16 Voltage = %.4fV" % infos["cell16"])
        
    except asyncio.exceptions.TimeoutError:
        print("timeout")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(doit())

def main() :
     asyncio.run(doit())
