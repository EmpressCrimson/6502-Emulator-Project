#Reminder 

#Might wanna change the checkregzero Func and where its used, to reduce LOC and repetitions

#EndReminder
from pathlib import Path
from tkinter import *
from tkinter import ttk
import EmulatorDashboard
#import numpy as np

MemorySize = 65536
Stacksize = 256

#It feels nice writing actual code after a long time of just scripting, makes me feel less of a fraud as a "programmer"

class GUI():
    def __init__(self):
        root = Tk()
        root.title("6502 Emulator (wow)")
        mainframe = ttk.Frame(root, padding=(3,3,12,12), height=500, width=500)
        mainframe.grid(sticky=(N, W, E, S))

        hexDumpLabel = ttk.Label(mainframe, border=2,padding=(3,3,3,3), relief=SUNKEN)
        hexDumpLabel.place(anchor=SW, width=100, height=10)

        root.mainloop()


class CPU(): #Reasoning is that I don't want to use global variables so I am just putting everything in a CPU class, only problem is I wasn't planning this :P
    def __init__(self):
        self.Running = True

        self.ProgramCounter = 0x0200 #After stack memory
        
        self.Registers = { #all variables
            "A" : 0,
            "S" : 0x01FF,
            "X" : 0,
            "Y" : 0,
        }
        
        self.StatusRegister = bytearray(1)
        self.StatusRegister = 32 #00100000
        
        #self.StatusRegisters = { #one byte var
        #     "Negative" : 0,
        #     "Overflow" : 0,
        #     "Break" : 0,
        #     "Decimal" : 0,
        #     "Interrupt disable" : 0,
        #     "Zero" : 0,
        #     "Carry" : 0,
        #}
        
    def SetRunning(self, boolVal):
        self.Running = boolVal
    
    def IncrementPC(self, value=0x0001):
        self.ProgramCounter += value
    
    def SetPC(self, value):
        self.ProgramCounter = value

    def Step(self, RAMObject): #I forgot why these two exist simultaneously
        Value = hex(RAMObject.Read(self.ProgramCounter))
        self.IncrementPC()
        #print("value:" + Value)
        return Value
    
    def setStatusFlag(self, flags): #OR
        self.StatusRegister = self.StatusRegister | (flags | 0x20)
        
    def clearStatusFlag(self, flags): #AND
        self.StatusRegister = self.StatusRegister & ((~flags) | 0x20)

    def CheckStatusReg(self, flags):
        if self.StatusRegister & flags == 0:
            return False
        else:
            return True
        
    def GetStatusReg(self):
        return self.StatusRegister
    
    def IncDecRegister(self, register, value):
        self.Registers[register] += value

    def GetReg(self,register):
        return self.Registers[register]
    
    #def SetFlag(self, flag, value):
    #    self.StatusRegisters[3] = value

    #def GetFlag(self, 3):
    #    return self.StatusRegisters[3]

    def GetPC(self):
        return self.ProgramCounter
    
    def CheckRegZero(self, reg):
        if self.GetReg(reg) == 0:
            self.setStatusFlag(0x02)
        else:
            self.clearStatusFlag(0x02)

    def CheckRegNegative(self, reg):
        if self.GetReg(reg) < 0:
            self.setStatusFlag(0x80)
        else:
            self.clearStatusFlag(0x80)

    def transferRegister(self, dest, val):
        self.Registers[dest] = self.Registers[val]
        self.CheckRegZero(val)
        self.CheckRegNegative(val)

    #region

    def NOP(self):
        #print("nop")
        return 0

    def BRK(self):
        self.SetRunning(False)
        self.setStatusFlag(0x10)
        #print(self.StatusRegister)
        #print("break")

    def INX(self):  
        self.IncDecRegister("X", 0x01)
        self.CheckRegNegative("X")
        self.CheckRegZero("X")

    def INY(self):
        self.IncDecRegister("Y", 0x01)
        self.CheckRegNegative("Y")
        self.CheckRegZero("Y")

    def DEX(self):
        self.IncDecRegister("X", -0x01)
        self.CheckRegNegative("X")
        self.CheckRegZero("X")

    def DEY(self):
        self.IncDecRegister("Y", -0x01)
        self.CheckRegNegative("Y")
        self.CheckRegZero("Y")

    def LDAImmediate(self):
        #self.Registers["A"] = self.Step(RAM)
        self.Registers["A"] = RAM.Read(self.ProgramCounter)
        #print(self.Registers["A"])
        self.CheckRegZero("A")
        self.CheckRegNegative("A")
    
    def LDAZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["A"] = RAM.Read(address)
        #print(self.Registers["A"])
        self.CheckRegZero("A")
        self.CheckRegNegative("A")

    def LDXImmediate(self):
        #self.Registers["X"] = self.Step(RAM)
        self.Registers["X"] = RAM.Read(self.ProgramCounter)
        #print(self.Registers["X"])
        self.CheckRegZero("X")
        self.CheckRegNegative("X")
    
    def LDXZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["X"] = RAM.Read(address)
        #print(self.Registers["X"])
        self.CheckRegZero("X")
        self.CheckRegNegative("X")

    def LDYImmediate(self):
        #self.Registers["Y"] = self.Step(RAM)
        self.Registers["Y"] = RAM.Read(self.ProgramCounter)
        #print(self.Registers["Y"])
        self.CheckRegZero("Y")
        self.CheckRegNegative("Y")
    
    def LDYZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["Y"] = RAM.Read(address)
        #print(self.Registers["Y"])
        self.CheckRegZero("Y")
        self.CheckRegNegative("Y")

    def BNE(self):
        address = RAM.Read(self.ProgramCounter)
        if address & 0x80: #check if signed, if so turn negative
            address -= 0x100
        if not (self.StatusRegister & 0x40): #why was this 0x02
            self.ProgramCounter += (address)
        #print("bne")
    
    def BEQ(self):
        address = RAM.Read(self.ProgramCounter)
        if address & 0x80: #check if signed, if so turn negative
            address -= 0x100
        if self.StatusRegister & 0x40:
            self.ProgramCounter += (address)

    def STAZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        RAM.Write(address, False, self.Registers["A"]) #fix the ZeroPageage so its actually ZeroPageage

    def STAAbsoluteX(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        RAM.Write(address+self.Registers["X"], False, self.Registers["A"])
        #print(address, address+self.Registers["X"])

    def STAAbsolute(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        RAM.Write(address, False, self.Registers["A"])
        #print(address, address+self.Registers["X"])

    def LDAAbsoluteX(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        self.Registers["A"] = RAM.Read(address+self.Registers["X"])
        self.CheckRegZero("A")
        self.CheckRegNegative("A")
        
    def CMPAbsoluteX(self):
        address = RAM.Read(self.ProgramCounter+1) #cant believe I missed that a high and low byte exists
        address = address<<8 | RAM.Read(self.ProgramCounter)
        Register_A = self.Registers["A"]
        Compare_Value = RAM.Read((address+self.Registers["X"]) & 0xFFFF) #0xFFFF is for caution I think so I am adding it just in case
        result = (Register_A - Compare_Value) & 0xFF
        flags = 0 #turns out I need to clear my flags first
        self.clearStatusFlag(0x83)
        if Register_A >= Compare_Value: #turns out this is supposed to compare register A and the compared value not the result itself, smth about carrying over
            flags += 0x01 #FORGOT THE = SIGN AND I WONDER WHY IT DOESNT WORK

            if Register_A == Compare_Value:
                flags += 0x02

        if result & 0x80: #I am going to check neg values with this from now on hopefully
            flags += 0x80

        self.setStatusFlag(flags)
        print(self.StatusRegister)

    def BCS(self):
        if self.StatusRegister & 0x01: #Forgot to erase the "not", forgot why it was there but it was needed that I know
            offset = RAM.Read(self.ProgramCounter)
            if offset & 0x80: #check if signed, if so turn negative
                offset -= 0x100
            self.ProgramCounter += (offset)

    def TAY(self):
        self.transferRegister("Y", "A")

    def TYA(self):
        self.transferRegister("A", "Y")

    def TXA(self):
        self.transferRegister("A", "X")

    # def TransferRegs(self, origin, dest):
    #     self.Registers[dest] = self.Registers[origin]
    #     self.CheckRegZero(origin)
    #     if self.GetReg(origin) < 0:
    #         self.setStatusFlag(0x80)

    def RTS(self):
        address = RAM.Read(self.Registers["S"]+1)
        address = address<<8 | RAM.Read(self.Registers["S"])
        self.ProgramCounter = address + 1
        self.Registers["S"] += 0x02


    def BPL(self):
        if self.CheckStatusReg(0x80):
            offset = RAM.Read(self.ProgramCounter)
            self.ProgramCounter += offset

    def ASL(self):
        addressToShift = RAM.Read(self.ProgramCounter) + self.GetReg("X")
        valueToShift = RAM.Read(addressToShift)
        shiftedValue = valueToShift << 1
        RAM.Write(addressToShift, 0, shiftedValue)

        self.setStatusFlag(valueToShift >> 7 << 4) #shift right so only bit 7 is left then pad it until it represents the Carry flag
        if shiftedValue == 0:
            self.setStatusFlag(0x40) #set Zero flag
            self.clearStatusFlag(0x80) #clear Negative flag
        else:
            self.setStatusFlag(shiftedValue >> 7 << 7) #Get bit 7 then pad until it is in the position of the Negative flag
            self.clearStatusFlag(0x40) #clear Zero flag
    
    def ORA(self):
        addressOfComparingValue = RAM.Read(self.ProgramCounter) + self.GetReg("X")
        self.Registers["A"] = self.GetReg("A") | RAM.Read(addressOfComparingValue)
        #add indirect accessing

    def STAIndirectY(self):
        addressToStoreValue = RAM.Read(self.ProgramCounter) + self.GetReg("Y")
        RAM.Write(addressToStoreValue, 0, self.GetReg("A"))

    def INCZeroPage(self):
        adress = RAM.Read(self.ProgramCounter)
        newValueForAdress = RAM.Read(adress) + 1
        RAM.Write(adress, 0, newValueForAdress)
        if newValueForAdress == 0:
            self.setStatusFlag(0x40) #set Zero flag
            self.clearStatusFlag(0x80) #clear Negative flag
        else:
            self.setStatusFlag(newValueForAdress >> 7 << 4) #Get bit 7 then pad until it is in the position of the Carry flag
            self.clearStatusFlag(0x40) #clear Zero flag
    #endregion


class MemoryObject(): #Ram class
    def __init__(self, Memsize):
        super().__init__
        self.Memory = bytearray(Memsize)
        self.Memory.replace(bytes(1), bytes(b"0"))
        self.AdressStart = int(512)

    def Read(self, Address):
        return self.Memory[Address]

    def Write(self, Address, size, value):
        self.Memory[Address] = value

    def Load(self, loadAddress, value):
        self.Memory[loadAddress:len(value)-1] = value #the absence of len(value)-1 makes it so that the rest of the bytearray is set to nil as value doesn't exist after its length
        print(value)

    def FormatToHexDump(self, data):
        listOfRows = []
        #print(data.count("\\x"))
        #byteData = data.split("\\x")
        #separator = " "
        #byteData = separator.join(byteData) #I WROTE DATA INSTEAD OF BYTEDATA THE NAME CONVENTION IS BITING ME IN THE ASS
        #byteData = byteData[1:] #remove the whitespace at the beginning
        #print(data.count("00"))
        for rowCount in range(1, int((MemorySize)/16)+1):
            rowdata = data[((rowCount-1)*16):(rowCount*16)]
            ##rowdata = byteData[(rowCount-1)*16*3:(rowCount*16*3)-1] #YESSSSSSS I FIGURED IT OUT THERE IS ONLY 1 SPACE NOT 2 SO HEX+WHITESPACE IS 3
            rowdata = " ".join(f"{b:02X}" for b in rowdata)
            rownumber = (rowCount-1)*16
            listOfRows.append("0x{address:04x} | {bytes}".format(address = rownumber, bytes = rowdata))
            #print("0x{address:04x} |{bytes}".format(address = rownumber, bytes = rowdata))
        return listOfRows
        #for i in range(0, MemorySize/16):
            

    def HexDump(self): #Took a bit due to some stupid mistakes and oversights, I thought the data wasn't transfering but turns out I wasn't sending everything
        #Wasn't sending because I was sending the first 65536 characters BUT \x prefixes were included in that (also a byte is made of 2 hex characters), which
        #led to the data getting cut in quarter
        #completeDumpList = []
        memData = self.Memory #65536 bytes to go
        print(len(memData))
        #for i in range(1, int((MemorySize)+1)):
            #dataToFormat = memData[:MemorySize]
        dumpList = self.FormatToHexDump(memData)
        #completeDumpList.extend(dumpList)

        with open("HexDump.txt", "w") as f:
            for v in dumpList:
               f.write("\n"+v)
        f.close()



    # def Hexdump(self):
    #     numOfLoops = int((MemorySize/16)/2048) + 1 #split the hexdump into 2048 segments due to string limit, setup the rownumber loop accordingly
    #     for x in range(0,numOfLoops):
    #         message = f"Hexdump ({x+1}): "
    #         for rownumber in range(int(MemorySize/16)):
    #             message += f"\n {rownumber} | " + (" ".join(str(self.Memory[16*rownumber:(rownumber*16)+16], ).lstrip("bytearray(b'").rstrip("')").split(r'\x')))
    #         #message += " ".join(self.Memory[16*rownumber:(rownumber*16)+15])
    #     #print(message)
    #     return message
    #     #return self.Memory.hex()

# def ReadMachineCode(): #Please name the binary data file to "binarydata.txt" or it won't work.
#     with open(Path(__file__).parent.resolve().joinpath("binarydata.txt"), "rb") as f:
#         read_data = f.readlines()
#         #print(read_data)
#     f.closed
#     MemLocation = 0x0100
#     for line in read_data:
#         #for opcode in opcodes:
#             #print(opcode, type(opcode))
#         line.rstrip(bytes("\r\n", "utf-8"))
#         Addresses = line.rstrip(bytes("\r\n", "utf-8")).split()
#         for address in Addresses:
#             RAM.Write(MemLocation, False, bytes(address))
#             MemLocation += 0x0001 #GUESS WHO FORGOT TO STEP THE MEMORY LOCATION AND STARTED CHASING GHOSTS

# def ReadMachineCode():
#     with open(Path(__file__).parent.resolve().joinpath("code.prg"), "rb") as f:
#         read_data = f.read()
#     f.closed
#     print(read_data)
#     data = read_data.replace(b'\n',b' ')
#     offset = 0
#     for byte in data.split(b'\\x'):
#         print(byte)
#         #print(byte)
#         RAM.Write(0x0200+offset, False, int(byte, 2))
#         offset += 0x0001

def ReadMachineCode():
    
    # with open(Path(__file__).parent.resolve().joinpath("code.prg"), "rb") as f:
    #     read_data = str(f.read())
    # f.closed
    # read_data = read_data.split('\\x')
    # read_data.remove("b'")
    # for i in range(0, len(read_data)):
    #     read_data[i] = read_data[i][:2]

    # offset = 0
    # startAddress = int(read_data[1] + read_data[0])
    # CPU.SetPC(startAddress)
    # print(startAddress)
    # print(CPU.GetPC())
    # for i in range(2, len(read_data)):
    #     RAM.Write(startAddress+offset, False, int(read_data[i], 16))
    #     offset += 0x0001
    with open("code.prg", "rb") as f:
    # PRG header: 2-byte little-endian address
        load_address = int.from_bytes(f.read(2), "little")

    # load the rest directly into RAM at that address
 
        RAM.Load(load_address, f.read())


def UpdateGUI():
    EmulatorMenu.set_pc(CPU.GetPC())
    EmulatorMenu.set_a(CPU.GetReg("A"))
    EmulatorMenu.set_x(CPU.GetReg("X"))
    EmulatorMenu.set_y(CPU.GetReg("Y"))
    EmulatorMenu.set_sp(CPU.GetReg("S"))
    EmulatorMenu.set_status(CPU.GetStatusReg())   # N, B, D, C set
    EmulatorMenu.update()

CPU = CPU()
RAM = MemoryObject(MemorySize)
EmulatorMenu =  EmulatorDashboard.EmulatorDashboard()


    #0xc8 : {
        #"Func" : CPU.INY,
        #"Size" : 1,
        #"Flags" : {"Negative", "Zero"}
    #},

#region CallTable List
CallTable = [None]*256  #(function, size, flags in byte)
CallTable[0xea] = (CPU.NOP, 1, 0x00)

CallTable[0x00] = (CPU.BRK, 1, 0x10)

CallTable[0xe8] = (CPU.INX, 1, 0x82)

CallTable[0xc8] = (CPU.INY, 1, 0x82)

CallTable[0xca] = (CPU.DEX, 1, 0x82)

CallTable[0x88] = (CPU.DEY, 1, 0x82)

CallTable[0xa9] = (CPU.LDAImmediate, 2, 0x82)

CallTable[0xa5] = (CPU.LDAZeroPage, 2, 0x82)

CallTable[0xa2] = (CPU.LDXImmediate, 2, 0x82)

CallTable[0xa6] = (CPU.LDXZeroPage, 2, 0x82)
    
CallTable[0xa0] = (CPU.LDYImmediate, 2, 0x82)

CallTable[0xa4] = (CPU.LDYZeroPage, 2, 0x82)

CallTable[0xd0] = (CPU.BNE, 2, 0x00)

CallTable[0xf0] = (CPU.BEQ, 2, 0x00)

CallTable[0x85] = (CPU.STAZeroPage, 2, 0x00)

CallTable[0x8D] = (CPU.STAAbsolute, 3, 0x00)

CallTable[0xBD] = (CPU.LDAAbsoluteX, 3, 0x82)

CallTable[0xDD] = (CPU.CMPAbsoluteX, 3, 0x83)

CallTable[0xB0] = (CPU.BCS, 2, 0x00)

CallTable[0xA8] = (CPU.TAY, 1, 0x82)

CallTable[0x9D] = (CPU.STAAbsoluteX, 3, 0x00)

CallTable[0x98] = (CPU.TYA, 1, 0x82)

CallTable[0x60] = (CPU.RTS, 1, 0x00)

CallTable[0x10] = (CPU.BPL, 2, 0x00)

CallTable[0x16] = (CPU.ASL, 2, 0xd0)

CallTable[0x01] = (CPU.ORA, 2, 0xC0)

CallTable[0x91] = (CPU.STAIndirectY, 2, 0x00)

CallTable[0xE6] = (CPU.INCZeroPage, 2, 0xC0)

CallTable[0x8A] = (CPU.TXA, 1, 0xC0)
#endregion


# def InitCallTable(): #Function for organizational purposes
#     CallTable[0xea] = CPU.NOP
#     CallTable[0x00] = CPU.BRK
#     CallTable[0xe8] = CPU.INX
#     CallTable[0xc8] = CPU.INY
#     CallTable[0xca] = CPU.DEX
#     CallTable[0x88] = CPU.DEY
#     CallTable[0xA9] = CPU.LDAImmediate
#     CallTable[0xA5] = CPU.LDAZeroPage
#     CallTable[0xA2] = CPU.LDXImmediate
#     CallTable[0xA6] = CPU.LDXZeroPage
#     CallTable[0xA0] = CPU.LDYImmediate
#     CallTable[0xA4] = CPU.LDYZeroPage

# CallTable.insert(0xea, CPU.NOP)
#     CallTable.insert(0x00, CPU.BRK)
#     CallTable.insert(0xe8, CPU.INX)
#     CallTable.insert(0xc8, CPU.INY)
#     CallTable.insert(0xca, CPU.DEX)
#     CallTable.insert(0x88, CPU.DEY)

# RAM.Write(0x0100, False, 0xEA)
# RAM.Write(0x0100+0x0001, False, 0xEA)
# RAM.Write(0x0102, False, 0xE8)
# RAM.Write(0x0103, False, 0xC8)
# RAM.Write(0x0104, False, 0x00)

#InitCallTable()

ReadMachineCode()
print(RAM.HexDump())
cycles = 0

while CPU.Running:
    opcode = int(CPU.Step(RAM),16)
    #CPU.IncrementPC SINCE WHEN WAS IT LIKE THIS 20/02/2026
    CallTable[opcode][0]() #I spent like an hour just to learn I need to put parantheses here cause without them it just goes NOP and not NOP()
    #print(CallTable[opcode])
    CPU.IncrementPC(CallTable[opcode][1]-1) #Indexing error .d should've been 1 instead of 2
    UpdateGUI()
    cycles += 1
    #print("a")
    #print("stepped")


print(f'X: ' + str(CPU.GetReg("X")))
print(f'Y: ' + str(CPU.GetReg("Y")))
print(f'A:' + str(CPU.GetReg("A")))
print(f'StatusRegister ' + (str(bin(CPU.StatusRegister))))

print("program stopped")
#print(RAM.Hexdump())
print(cycles)
print(CPU.GetPC())