#!/usr/bin/env python
import sys
import os
import asyncio
from heltecbmsrelay import TransportBLE
from heltecbmsrelay import HeltecBMSClient

async def doit(mac):
    transport = TransportBLE(mac)
    await transport.start()
    client = HeltecBMSClient(transport)
    last_datas = await client.read_infos()
    print(last_datas)


if __name__ == "__main__" :
    mac=sys.argv[1]
    asyncio.run(doit(mac))
