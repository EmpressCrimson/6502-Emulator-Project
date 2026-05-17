from pathlib import Path
from tkinter import *
from tkinter import ttk
import EmulatorDashboard

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
        
        self.ProgramCounter = 0

        self.Registers = { #all variables
            "A" : 0,
            "S" : 0x01FF,
            "X" : 0,
            "Y" : 0,
        }
        
        self.StatusRegister = bytearray(1)
        self.StatusRegister = 32 #00100000
        
        
    def SetRunning(self, boolVal):
        self.Running = boolVal
    
    def IncrementPC(self, value=0x0001):
        self.ProgramCounter += value

    def OffsetPC(self):
        offset = RAM.Read(self.ProgramCounter)
        self.ProgramCounter += (offset)
    
    def SetPC(self, value):
        self.ProgramCounter = value

    def Step(self, RAMObject): #I forgot why these two exist simultaneously
        Value = hex(RAMObject.Read(self.ProgramCounter))
        self.IncrementPC()
        return Value
    
    def setStatusFlag(self, flags): #OR
        self.StatusRegister = self.StatusRegister | (flags | 0x20)
        
    def clearStatusFlag(self, flags): #AND
        self.StatusRegister = self.StatusRegister & ((~flags) | 0x20)

    def CheckStatusReg(self, flags):
        return self.StatusRegister & flags
        
    def GetStatusReg(self):
        return self.StatusRegister
    
    def IncDecRegister(self, register, value):
        self.SetReg(register, value)

    def GetReg(self,register):
        return self.Registers[register]
    
    def SetReg(self, register, value):
        self.Registers[register] = value

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

    def CheckRegZeroOrNeg(self, register):
        self.CheckRegZero(register)
        self.CheckRegNegative(register)

    def transferRegister(self, dest, val):
        self.GetReg(dest, self.GetReg(val))
        self.CheckRegZeroOrNeg(val)

    #region opcode Functions

    def NOP(self):
        return 0

    def BRK(self):
        self.SetRunning(False)
        self.setStatusFlag(0x10)

    def INX(self):  
        self.IncDecRegister("X", 0x01)
        self.CheckRegZeroOrNeg("X")

    def INY(self):
        self.IncDecRegister("Y", 0x01)
        self.CheckRegZeroOrNeg("Y")

    def DEX(self):
        self.IncDecRegister("X", -0x01)
        self.CheckRegZeroOrNeg("X")

    def DEY(self):
        self.IncDecRegister("Y", -0x01)
        self.CheckRegZeroOrNeg("Y")

    def LDAImmediate(self):
        self.SetReg("A", RAM.Read(self.ProgramCounter))
        self.CheckRegZeroOrNeg("A")
    
    def LDAZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.SetReg("A", RAM.Read(address))
        self.CheckRegZeroOrNeg("A")

    def LDXImmediate(self):
        self.SetReg("X", RAM.Read(self.ProgramCounter))
        self.CheckRegZeroOrNeg("X")
    
    def LDXZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.SetReg("X", RAM.Read(address))
        self.CheckRegZeroOrNeg("X")

    def LDYImmediate(self):
        self.SetReg("Y", RAM.Read(self.ProgramCounter))
        self.CheckRegZeroOrNeg("Y")
    
    def LDYZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        self.SetReg("Y", RAM.Read(address))
        self.CheckRegZeroOrNeg("Y")

    def BNE(self):
        self.OffsetPC()
    
    def BEQ(self):
        self.OffsetPC()

    def STAZeroPage(self):
        address = RAM.Read(self.ProgramCounter)
        RAM.Write(address, self.GetReg("A")) #fix the ZeroPageage so its actually ZeroPageage

    def STAAbsoluteX(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        registerValue = self.GetReg("X")
        RAM.Write(address+registerValue, registerValue)

    def STAAbsolute(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        RAM.Write(address, self.GetReg("A"))

    def LDAAbsoluteX(self):
        address = RAM.Read(self.ProgramCounter+1)
        address = address<<8 | RAM.Read(self.ProgramCounter)
        self.SetReg("A", RAM.Read(address+self.GetReg("A")))
        self.CheckRegZeroOrNeg("A")
        
    def CMPAbsoluteX(self): 
        address = RAM.Read(self.ProgramCounter+1) #cant believe I missed that a high and low byte exists
        address = address<<8 | RAM.Read(self.ProgramCounter)
        Register_A = self.GetReg("A")
        Compare_Value = RAM.Read((address+self.GetReg("X")) & 0xFFFF) #0xFFFF is for caution I think so I am adding it just in case
        result = (Register_A - Compare_Value) & 0xFF
        flags = 0 #turns out I need to clear my flags first
        self.clearStatusFlag(0x83)
        if Register_A >= Compare_Value: #turns out this is supposed to compare register A and the compared value not the result itself, smth about carrying over
            flags += 0x01 #FORGOT THE = SIGN AND I WONDER WHY IT DOESNT WORK

            if Register_A == Compare_Value:
                flags += 0x02

        if result & 0x80: #I am going to check neg values with this from now on hopefully *OPTIMIZATION* Could turn this to flags | (result & 0x80)
            flags += 0x80

        self.setStatusFlag(flags)
        print(self.StatusRegister)

    def BCS(self):
        if self.StatusRegister & 0x01: #Forgot to erase the "not", forgot why it was there but it was needed that I know
            self.OffsetPC()

    def TAY(self):
        self.transferRegister("Y", "A")

    def TYA(self):
        self.transferRegister("A", "Y")

    def TXA(self):
        self.transferRegister("A", "X")

    def RTS(self):
        register_S = self.GetReg("S")
        address = RAM.Read(register_S+1)
        address = address<<8 | RAM.Read(register_S)
        self.ProgramCounter = address + 1
        self.IncDecRegister("S", 0x02)

    def BPL(self):
        if self.CheckStatusReg(0x80):
            self.OffsetPC()

    def ASL(self):
        addressToShift = RAM.Read(self.ProgramCounter) + self.GetReg("X")
        valueToShift = RAM.Read(addressToShift)
        shiftedValue = valueToShift << 1
        RAM.Write(addressToShift, shiftedValue)

        self.setStatusFlag(valueToShift >> 7 << 4) #shift right so only bit 7 is left then pad it until it represents the Carry flag
        if shiftedValue == 0:
            self.setStatusFlag(0x40) #set Zero flag
            self.clearStatusFlag(0x80) #clear Negative flag
        else:
            self.setStatusFlag(shiftedValue >> 7 << 7) #Get bit 7 then pad until it is in the position of the Negative flag
            self.clearStatusFlag(0x40) #clear Zero flag
    
    def ORA(self):
        addressOfComparingValue = RAM.Read(self.ProgramCounter) + self.GetReg("X")
        self.SetReg("A", self.GetReg("A") | RAM.Read(addressOfComparingValue))
        #add indirect accessing

    def STAIndirectY(self):
        addressToStoreValue = RAM.Read(self.ProgramCounter) + self.GetReg("Y")
        RAM.Write(addressToStoreValue, self.GetReg("A"))

    def INCZeroPage(self):
        adress = RAM.Read(self.ProgramCounter)
        newValueForAdress = RAM.Read(adress) + 1
        RAM.Write(adress, newValueForAdress)
        if newValueForAdress == 0:
            self.setStatusFlag(0x40) #set Zero flag
            self.clearStatusFlag(0x80) #clear Negative flag
        else:
            self.setStatusFlag(newValueForAdress >> 7 << 4) #Get bit 7 then pad until it is in the position of the Carry flag
            self.clearStatusFlag(0x40) #clear Zero flag

    def JSR(self):
        register_S = self.GetReg("S")
        RAM.Write(register_S, (self.ProgramCounter+2)>>8)
        RAM.Write(register_S-1, (self.ProgramCounter+2)&0x0F)
        self.IncDecRegister("S", -0x02)

    
    #endregion


class MemoryObject(): #Ram class
    def __init__(self, Memsize):
        super().__init__
        self.Memory = bytearray(Memsize)
        self.Memory.replace(bytes(1), bytes(b"0"))
        self.AdressStart = int(512)

    def Read(self, Address):
        return self.Memory[Address]

    def Write(self, Address, value):
        self.Memory[Address] = value

    def Load(self, loadAddress, value):
        self.Memory[loadAddress:len(value)-1] = value #the absence of len(value)-1 makes it so that the rest of the bytearray is set to nil as value doesn't exist after its length
        print(value)

    def FormatToHexDump(self, data):
        listOfRows = []
        for rowCount in range(1, int((MemorySize)/16)+1):
            rowdata = data[((rowCount-1)*16):(rowCount*16)]
            ##rowdata = byteData[(rowCount-1)*16*3:(rowCount*16*3)-1] #YESSSSSSS I FIGURED IT OUT THERE IS ONLY 1 SPACE NOT 2 SO HEX+WHITESPACE IS 3
            rowdata = " ".join(f"{b:02X}" for b in rowdata) #directly format the data and turn into string
            rownumber = (rowCount-1)*16
            listOfRows.append("0x{address:04x} | {bytes}".format(address = rownumber, bytes = rowdata))
        return listOfRows          

    def HexDump(self): #Took a bit due to some stupid mistakes and oversights, I thought the data wasn't transfering but turns out I wasn't sending everything
        #Wasn't sending because I was sending the first 65536 characters BUT \x prefixes were included in that (also a byte is made of 2 hex characters), which
        #led to the data getting cut in quarter
        memData = self.Memory #65536 bytes to go
        print(len(memData))
        dumpList = self.FormatToHexDump(memData)

        with open("HexDump.txt", "w") as f:
            for v in dumpList:
               f.write("\n"+v)
        f.close()


def ReadMachineCode(): #Read PRG File and load to memory
    with open("code.prg", "rb") as f:
    # PRG header: 2-byte little-endian address
        load_address = int.from_bytes(f.read(2), "little")

    # load the rest directly into RAM at that address
        RAM.Load(load_address, f.read())
        CPU.SetPC(load_address)


def UpdateGUI(): #GUI stuff
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

CallTable[0x20] = (CPU.JSR, 3, 0x00)
#endregion

ReadMachineCode()
cycles = 0

while CPU.Running:
    opcode = int(CPU.Step(RAM),16)
    #CPU.IncrementPC SINCE WHEN WAS IT LIKE THIS 20/02/2026
    #CallTable[opcode][0]() #I spent like an hour just to learn I need to put parantheses here cause without them it just goes NOP and not NOP()
    operationDict = CallTable[opcode]
    
    if operationDict is None:
        print("Opcode " + hex(opcode) + " does not exist!" )
        opcode = 0
        CallTable[0][0]()

    else:
        operationDict[0]()

    CPU.IncrementPC(CallTable[opcode][1]-1) #Indexing error .d should've been 1 instead of 2
    UpdateGUI()
    cycles += 1
    print(opcode)

print(RAM.HexDump())

print(f'X: ' + str(CPU.GetReg("X")))
print(f'Y: ' + str(CPU.GetReg("Y")))
print(f'A:' + str(CPU.GetReg("A")))
print(f'StatusRegister ' + (str(bin(CPU.StatusRegister))))

print("program stopped")
print(cycles)
print(CPU.GetPC())