import sys
import os
import asyncio
import io
import struct
from dataclasses import dataclass
from typing import List
import time
import argparse
import json
from .Transports import TransportBLE

class ReadException(Exception):
    pass

START_MARK = 0x01
READ_COMMAND = 0x03
DEBUG = 0

def calc_crc(data: bytes) -> int:
    return 0xffff - sum(data) + 1


def gettemp(h,l): # high byte, low byte
    t = (h*256 + l) / 10.0 - 40
    decimal = t - round(t)
    return round(t)-decimal

class HeltecBMSClient:
    def __init__(self, transport):
        self._transport = transport

    async def read_infos(self,cmd=None) :
        if cmd == None :
            datas = {'timestamp': time.time()}
            for i in [0,7,14,21,28,35,42,48] :
                if DEBUG: print("Command %d : "%i)
                raw_datas = await self._send_command(i)
                datas.update(await self.read_result(i))
        return datas

    async def read_result_00(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)                        
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))                    
        vbat = (ar[8]*256+ar[9])/100.0
        current = float((ar[10]*256+ar[11])-10000)/10.0
        t1 = gettemp(ar[12], ar[13]) #float(ar[12]*256+ar[13])/10.0-40
        t2 = gettemp(ar[14], ar[15]) #float(ar[14]*256+ar[15])/10.0-40
        uptime = int(ar[4]*256+ar[5])
        
        datas = {"uptime": uptime,
                 "vbat":vbat,
                 "current":current,
                 "t1":t1,
                 "t2":t2}
        return datas



    async def read_result_07(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        cell_high=v8/1000.0
        t3 = gettemp(ar[10], ar[11])  #float(ar[10]*256+ar[11])/10.0-40
        t4 = gettemp(ar[12], ar[13])  #float(ar[12]*256+ar[13])/10.0-40        
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        if DEBUG: print("v6 = %d %d" % (ar[10], ar[11]))
        datas = {"cell_high" : cell_high,
                 "t3": t3,
                 "t4": t4}
        return datas


    async def read_result_0e(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
 
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        cell_low=v2/1000.0
        soc = v4
        bat_capa = v5/100.0
        bat_remain = v6/100.0
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {"cell_low" : cell_low,
                 "bat_capa" : bat_capa,
                 "bat_remain" : bat_remain,
                 "soc":v4}
        return datas


    async def read_result_15(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        cell1 = v4/1000.0
        cell2 = v5/1000.0
        cell3 = v6/1000.0
        cell4 = v7/1000.0
        cell5 = v8/1000.0        
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {"cell1":cell1,
                 "cell2":cell2,
                 "cell3":cell3,
                 "cell4":cell4,
                 "cell5":cell5}
        return datas

    async def read_result_1c(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = float(ar[0]*256+ar[1])
        v2 = float(ar[2]*256+ar[3])
        v3 = float(ar[4]*256+ar[5])
        v4 = float(ar[6]*256+ar[7])
        v5 = float(ar[8]*256+ar[9])
        v6 = float(ar[10]*256+ar[11])
        v7 = float(ar[12]*256+ar[13])
        v8 = float(ar[14]*256+ar[15])
        cell6 = v2/1000.0
        cell7 = v3/1000.0
        cell8 = v4/1000.0
        cell9 = v5/1000.0
        cell10 = v6/1000.0
        cell11 = v7/1000.0
        cell12 = v8/1000.0
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {"cell6":cell6,
                 "cell7":cell7,
                 "cell8":cell8,
                 "cell9":cell9,
                 "cell10":cell10,
                 "cell11":cell11,
                 "cell12":cell12}
        return datas


    async def read_result_23(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        cell13 = v2/1000.0
        cell14 = v3/1000.0
        cell15 = v4/1000.0
        cell16 = v5/1000.0
        
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {"cell13":cell13,
                 "cell14":cell14,
                 "cell15":cell15,
                 "cell16":cell16}
        return datas
    

    async def read_result_2a(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 14 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = 0
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {}
        return datas

    async def read_result_30(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {}
        return datas

    
    async def read_result_xx(self) :
        start_mark = await self._read(1)
        if start_mark[0] != START_MARK:
            raise ReadException()        

        i = 0
        s=""
        sx=""
        ar=[]
        while i < 16 :
            data =  await self._read(1)
            s=s+"%3d "%int(data[0])
            sx=sx+"%x "%int(data[0])
            ar.append(int(data[0]))
            i=i+1
        crc = await self._read(2)
        v1 = int(ar[0]*256+ar[1])
        v2 = int(ar[2]*256+ar[3])
        v3 = int(ar[4]*256+ar[5])
        v4 = int(ar[6]*256+ar[7])
        v5 = int(ar[8]*256+ar[9])
        v6 = int(ar[10]*256+ar[11])
        v7 = int(ar[12]*256+ar[13])
        v8 = int(ar[14]*256+ar[15])
        if DEBUG: print("v1 = %d - v2 = %d - v3 = %d - v4 = %d - v5 = %d - v6 = %d - v7 = %d - v8 = %d" % (v1,v2,v3,v4,v5,v6,v7,v8))
        datas = {}
        return datas
    
    
    
    async def read_result(self,cmd) :
        if cmd == 0 :
            r = await self.read_result_00()
            return r
        if cmd == 7 :
            r = await self.read_result_07()
            return r
        if cmd == 0xe :
            r = await self.read_result_0e()
            return r
        if cmd == 0x15 :
            r = await self.read_result_15()
            return r
        if cmd == 0x1c :
            r = await self.read_result_1c()
            return r
        if cmd == 0x23 :
            r = await self.read_result_23()
            return r
        if cmd == 0x2a :
            r = await self.read_result_2a()
            return r
        if cmd == 0x30 :
            r = await self.read_result_30()
            return r

    
    def create_request(self,cmd):
        if cmd == 0x00 : req = b"\x01\x03\x10\x00\x00\x07\x00\xc8"
        if cmd == 0x07 : req = b"\x01\x03\x10\x07\x00\x07\xb1\x09"
        if cmd == 0x0e : req = b"\x01\x03\x10\x0e\x00\x07\x61\x0b"
        if cmd == 0x15 : req = b"\x01\x03\x10\x15\x00\x07\x11\x0c"
        if cmd == 0x1c : req = b"\x01\x03\x10\x1c\x00\x07\xc1\x0e"
        if cmd == 0x23 : req = b"\x01\x03\x10\x23\x00\x07\xf1\x02"
        if cmd == 0x2a : req = b"\x01\x03\x10\x2a\x00\x06\xe0\xc0"
        if cmd == 0x30 : req = b"\x01\x03\x10\x30\x00\x07\x00\xc7"         
        return req

    async def _read(self, size: int):
        remaining = size
        data = b""

        while len(data) < size:
            data += await self._transport.read(remaining)
            remaining -= len(data)

        return data
    
    async def _send_command(self, cmd) -> bytes:
        request = self.create_request(cmd)
        if DEBUG: print(request)
        await self._transport.write(request)
        self._transport.flush_input()

        return True

