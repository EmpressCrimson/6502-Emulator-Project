#Reminder 

#Might wanna change the checkregzero Func and where its used, to reduce LOC and repetitions

#EndReminder
from pathlib import Path
#import numpy as np

MemorySize = 65536
Stacksize = 256

#It feels nice writing actual code after a long time of just scripting, makes me feel less of a fraud as a "programmer"


class CPU(): #Reasoning is that I don't want to use global variables so I am just putting everything in a CPU class, only problem is I wasn't planning this :P
    def __init__(self):
        self.Running = True

        self.ProgramCounter = 0x0100 #After stack memory
        
        self.Registers = { #all variables
            "A" : 0,
            "S" : 0x00,
            "X" : 0,
            "Y" : 0x00,
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

    def Step(self, RAMObject): #I forgot why these two exist simultaneously
        Value = hex(RAMObject.Read(self.ProgramCounter))
        self.IncrementPC()
        print("value:" + Value)
        return Value
    
    def SetStatusReg(self, flags): #OR
        self.StatusRegister = self.StatusRegister | (flags+0x20)
        
    def ClearStatusReg(self, flags): #AND
        self.StatusRegister = self.StatusRegister & (255-flags)
    
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
            self.SetStatusReg(0x02)
        else:
            self.ClearStatusReg(0x02)
    #region

    def NOP(self):
        print("nop")
        return 0

    def BRK(self):
        self.SetRunning(False)
        self.SetStatusReg(0x10)
        print(self.StatusRegister)
        print("break")

    def INX(self):  
        self.IncDecRegister("X", 0x01)
        if self.GetReg("X") > -1:
            self.ClearStatusReg(0x80)
            #self.StatusRegisters["Negative"] = 0
        self.CheckRegZero("X")

    def INY(self):
        self.IncDecRegister("Y", 0x01)
        if self.GetReg("X") > 0:
            self.ClearStatusReg(0x80)
        self.CheckRegZero("Y")

    def DEX(self):
        self.IncDecRegister("X", -0x01)
        if self.GetReg("X") < 0:
            self.SetStatusReg(0x80)
        self.CheckRegZero("X")

    def DEY(self):
        self.IncDecRegister("Y", -0x01)
        if self.GetReg("Y") < 0:
            self.SetStatusReg(0x80)
        self.CheckRegZero("Y")

    def LDAImmediate(self):
        #self.Registers["A"] = self.Step(RAM)
        self.Registers["A"] = RAM.Read(self.ProgramCounter)
        print(self.Registers["A"])
        self.CheckRegZero("A")
    
    def LDAZeroP(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["A"] = RAM.Read(address)
        print(self.Registers["A"])
        self.CheckRegZero("A")

    def LDXImmediate(self):
        #self.Registers["X"] = self.Step(RAM)
        self.Registers["X"] = RAM.Read(self.ProgramCounter)
        print(self.Registers["X"])
        self.CheckRegZero("X")
    
    def LDXZeroP(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["X"] = RAM.Read(address)
        print(self.Registers["X"])
        self.CheckRegZero("X")

    def LDYImmediate(self):
        #self.Registers["Y"] = self.Step(RAM)
        self.Registers["Y"] = RAM.Read(self.ProgramCounter)
        print(self.Registers["Y"])
        self.CheckRegZero("Y")
    
    def LDYZeroP(self):
        address = RAM.Read(self.ProgramCounter)
        self.Registers["Y"] = RAM.Read(address)
        print(self.Registers["Y"])
        self.CheckRegZero("Y")

    def BNE(self):
        address = RAM.Read(self.ProgramCounter)
        if (self.StatusRegister&0x02) == 0:
            self.ProgramCounter = (Stacksize-1) + address-1 #-1 cause while Running increments PC by 1 AFTER setting the PC
        print("bne")
    
    def BEQ(self):
        address = RAM.Read(self.ProgramCounter)
        if (self.StatusRegister&0x02) == 1:
            self.ProgramCounter = (Stacksize-1) + address-1
        print("beq")



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

    def Hexdump(self):
        return self.Memory.hex()

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

def ReadMachineCode():
    with open(Path(__file__).parent.resolve().joinpath("binarydata.txt"), "rb") as f:
        read_data = f.read()
    f.closed
    data = read_data.replace(b'\r\n',b' ')
    offset = 0
    for byte in data.split(b' '):
        print(byte)
        RAM.Write(0x0100+offset, False, int(byte, 2))
        offset += 0x0001


CPU = CPU()
RAM = MemoryObject(MemorySize)

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

CallTable[0xa5] = (CPU.LDAZeroP, 2, 0x82)

CallTable[0xa2] = (CPU.LDXImmediate, 2, 0x82)

CallTable[0xa6] = (CPU.LDXZeroP, 2, 0x82)
    
CallTable[0xa0] = (CPU.LDYImmediate, 2, 0x82)

CallTable[0xa4] = (CPU.LDYZeroP, 2, 0x82)

CallTable[0xd0] = (CPU.BNE, 2, 0x00)

CallTable[0xf0] = (CPU.BEQ, 2, 0x00)
#endregion


# def InitCallTable(): #Function for organizational purposes
#     CallTable[0xea] = CPU.NOP
#     CallTable[0x00] = CPU.BRK
#     CallTable[0xe8] = CPU.INX
#     CallTable[0xc8] = CPU.INY
#     CallTable[0xca] = CPU.DEX
#     CallTable[0x88] = CPU.DEY
#     CallTable[0xA9] = CPU.LDAImmediate
#     CallTable[0xA5] = CPU.LDAZeroP
#     CallTable[0xA2] = CPU.LDXImmediate
#     CallTable[0xA6] = CPU.LDXZeroP
#     CallTable[0xA0] = CPU.LDYImmediate
#     CallTable[0xA4] = CPU.LDYZeroP

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
# print(RAM.Hexdump())
print(RAM.Hexdump())

while CPU.Running:
    opcode = int(CPU.Step(RAM),16)
    CPU.IncrementPC
    CallTable[opcode][0]() #I spent like an hour just to learn I need to put parantheses here cause without them it just goes NOP and not NOP()
    CPU.IncrementPC(CallTable[opcode][1]-1) #Indexing error .d should've been 1 instead of 2
    print("stepped")

print(f'X: ' + str(CPU.GetReg("X")))
print(f'Y: ' + str(CPU.GetReg("Y")))
print(f'A:' + str(CPU.GetReg("A")))
print(f'StatusRegister ' + (str(bin(CPU.StatusRegister))))

print("program stopped")