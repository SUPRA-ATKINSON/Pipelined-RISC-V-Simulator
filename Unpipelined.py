import fileinput


instruction_list = []
disassembler_list = []

register_list = 32*[0]
data_dict = {}
adrs_list = []

execution_dict = {}
instruction_dict = {}
disassembler_dict = {}

with fileinput.input(encoding="utf-8") as file:
    for line in file:
        instruction_list.append(line.strip())


decoded_dict = {}
for i in instruction_list:
  decoded_dict[i] = ""

break_flag = 0


category_1 = {"00000":"beq",
              "00001":"bne",
              "00010":"blt",
              "00011":"sw"}

category_2 = {"00000":"add",
              "00001":"sub",
              "00010":"and",
              "00011":"or"}

category_3 = {"00000":"addi",
              "00001":"andi",
              "00010":"ori",
              "00011":"sll",
              "00100":"sra",
              "00101":"lw"}

category_4 = {"00000":"jal",
              "11111":"break"}


def signed_convert(binary_str):
    decimal_value = int(binary_str, 2)
    if binary_str[0] == '1':
        decimal_value -= 2 ** len(binary_str)
    return decimal_value


# DISASSEMBLER MAIN LOGIC ------------------------------------------------------
for i in instruction_list:


  if i[30:32] == "00":
    cat1_instr = category_1[i[25:30]]
    cat1_rs1 = i[12:17]
    cat1_offset = i[0:7] + i[20:25]
    cat1_rs2 = i[7:12]
    if cat1_instr == "sw":
      cat1_decoded = f"{cat1_instr} x{int(cat1_rs1, 2)}, {signed_convert(cat1_offset)}(x{int(cat1_rs2, 2)})"
    else:
      cat1_decoded = f"{cat1_instr} x{int(cat1_rs1, 2)}, x{int(cat1_rs2, 2)}, #{signed_convert(cat1_offset)}"
    disassembler_list.append(cat1_decoded)
    #print(cat1_decoded)

    # left shift, sign extend
    shifted_binary_string = format(int(cat1_offset, 2) << 1, '012b')
    sign_extended_binary_string = shifted_binary_string[0] * 20 + shifted_binary_string


  elif i[30:32] == "01":
    cat2_instr = category_2[i[25:30]]
    cat2_rd = i[20:25]
    cat2_rs1 = i[12:17]
    cat2_rs2 = i[7:12]
    cat2_decoded = f"{cat2_instr} x{int(cat2_rd, 2)}, x{int(cat2_rs1, 2)}, x{int(cat2_rs2, 2)}"
    disassembler_list.append(cat2_decoded)
    #print(cat2_decoded)


  elif i[30:32] == "10":
    cat3_instr = category_3[i[25:30]]
    cat3_offset = i[0:12]
    cat3_rd = i[20:25]
    cat3_rs1 = i[12:17]
    if cat3_instr in ["andi", "ori", "sll"]:
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, x{int(cat3_rs1, 2)}, #{int(cat3_offset, 2)}"
    if cat3_instr == "lw":
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, {int(cat3_offset, 2)}(x{int(cat3_rs1, 2)})"
    else:
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, x{int(cat3_rs1, 2)}, #{signed_convert(cat3_offset)}"
    disassembler_list.append(cat3_decoded)
    #print(cat3_decoded)


  elif i[30:32] == "11":
    cat4_instr = category_4[i[25:30]]
    if cat4_instr == "break":
      disassembler_list.append(f"{cat4_instr}")
      break_flag = 1
      break_index = instruction_list.index(i)
      break
    else:
      cat4_rd = i[20:25]
      cat4_offset = i[0:20]
      cat4_decoded = f"{cat4_instr} x{int(cat4_rd, 2)}, #{signed_convert(cat4_offset)}"
      disassembler_list.append(cat4_decoded)
      #print(cat4_decoded)

if break_flag == 1:
  for i in range(break_index+1, len(instruction_list)):
    data_value = signed_convert(instruction_list[i])
    data_dict[256+4*i] = data_value
    disassembler_list.append(str(data_value))
    #print(data_value)


# File write
start_address = 256
temp_address = start_address

disassembly_file = open("disassembly.txt", "w")

for i, j in zip(instruction_list, disassembler_list):
  adrs_list.append(temp_address)
  content = f"{i}\t{str(temp_address)}\t{j}\n"
  disassembly_file.write(content)
  temp_address += 4

disassembly_file.close()



for i,j in zip(adrs_list, instruction_list):
  instruction_dict[i] = j

for i,j in zip(adrs_list, disassembler_list):
  disassembler_dict[i] = j


import re

def parse_instruction(instruction):
    parts = instruction.split()
    opcode = parts[0].lower()  # Get the opcode in lowercase

    if opcode == 'beq':
        rs1, rs2, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'beq_f({rs1}, {rs2}, {imm}, {adrs})'

    elif opcode == 'sw':
        pattern = r"sw x(\d+), (\d+)\(x(\d+)\), (\d+)"
        match = re.match(pattern, instruction)
        if match:
          num1 = int(match.group(1))
          num2 = int(match.group(3))
          num3 = int(match.group(2))
          num4 = int(match.group(4))
        return f"sw_f({num1}, {num2}, {num3}, {num4})"

    elif opcode == 'blt':
        rs1, rs2, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'blt_f({rs1}, {rs2}, {imm}, {adrs})'

    elif opcode == 'bne':
        rs1, rs2, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'bne_f({rs1}, {rs2}, {imm}, {adrs})'

    elif opcode == 'add':
        rd, rs1, rs2, adrs = map(lambda x: int(x.strip('x,')), parts[1:])
        return f'add_f({rd}, {rs1}, {rs2}, {adrs})'

    elif opcode == 'sub':
        rd, rs1, rs2, adrs = map(lambda x: int(x.strip('x,')), parts[1:])
        return f'sub_f({rd}, {rs1}, {rs2}, {adrs})'

    elif opcode == 'and':
        rd, rs1, rs2, adrs = map(lambda x: int(x.strip('x,')), parts[1:])
        return f'and_f({rd}, {rs1}, {rs2}, {adrs})'

    elif opcode == 'or':
        rd, rs1, rs2, adrs = map(lambda x: int(x.strip('x,')), parts[1:])
        return f'or_f({rd}, {rs1}, {rs2}, {adrs})'

    elif opcode == 'addi':
        rd, rs1, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'addi_f({rd}, {rs1}, {imm}, {adrs})'

    elif opcode == 'andi':
        rd, rs1, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'andi_f({rd}, {rs1}, {imm}, {adrs})'

    elif opcode == 'ori':
        rd, rs1, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'ori_f({rd}, {rs1}, {imm}, {adrs})'

    elif opcode == 'sll':
        rd, rs1, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'sll_f({rd}, {rs1}, {imm}, {adrs})'

    elif opcode == 'sra':
        rd, rs1, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'sra_f({rd}, {rs1}, {imm}, {adrs})'

    elif opcode == 'lw':
        pattern = r"lw x(\d+), (\d+)\(x(\d+)\), (\d+)"
        match = re.match(pattern, instruction)
        if match:
          num1 = int(match.group(1))
          num2 = int(match.group(3))
          num3 = int(match.group(2))
          num4 = int(match.group(4))
        return f"lw_f({num1}, {num2}, {num3}, {num4})"

    elif opcode == 'jal':
        rd, imm, adrs = map(lambda x: int(x.strip('x,#')), parts[1:])
        return f'jal_f({rd}, {imm}, {adrs})'

    else:
        return "invalid"


def write_sim(a,b,c):
    simulation_file.write(f"--------------------\n")
    simulation_file.write(f"Cycle\t{a}:\t{b}\t{c}")
    simulation_file.write('\n')
    simulation_file.write(f"Registers")
    simulation_file.write('\n')
    for i in range(0, 32, 8):
      simulation_file.write(f"x{i:02d}:\t")
      for j in range(8):
        simulation_file.write(f"{register_list[i + j]}\t")
      simulation_file.write('\n')
    simulation_file.write(f"Data")
    simulation_file.write('\n')
    my_list = list(data_dict.values())
    prefix = list(data_dict.keys())[0]
    chunk_size = 8
    for i in range(0, len(my_list), chunk_size):
        chunk = my_list[i:i+chunk_size]
        simulation_file.write(f"{prefix}:\t")

        for item in chunk:
            simulation_file.write(f"{item}\t")

        simulation_file.write('\n')
        prefix += 32

simulation_file = open("simulation.txt", "w")

# Category-1 functions

def beq_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] == register_list[s2]:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    adrs += (offset*2)
    cycle(adrs)
  else:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    cycle(adrs+4)

def bne_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] != register_list[s2]:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    adrs += (offset*2)
    cycle(adrs)
  else:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    cycle(adrs+4)

def blt_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] < register_list[s2]:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    adrs += (offset*2)
    cycle(adrs)
  else:
    write_sim(len(l), adrs, disassembler_dict[adrs])
    cycle(adrs+4)

def sw_f(s1: int, s2: int, offset: int, adrs: int):
  data_dict[register_list[s2] + offset] = register_list[s1]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)


# Category-2 functions

def add_f(d: int, s1: int, s2: int, adrs: int,):
  register_list[d] = register_list[s1] + register_list[s2]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def sub_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] - register_list[s2]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def or_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] | register_list[s2]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def and_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] & register_list[s2]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)


# Category-3 funtions

def addi_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] + offset
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def andi_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] & offset
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def ori_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] | offset
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def sll_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] << offset
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def sra_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] >> offset
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)

def lw_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = data_dict[register_list[s] + offset]
  write_sim(len(l), adrs, disassembler_dict[adrs])
  cycle(adrs+4)


# Category-4 functions

def jal_f(d: int, offset: int, adrs: int):
  register_list[d] = adrs + 4
  write_sim(len(l), adrs, disassembler_dict[adrs])
  adrs = adrs + 2*(offset)
  cycle(adrs)

def break_f(none):
  return none


parse_list = []
for i,j in zip(adrs_list, disassembler_list):
  j = j + ", " +str(i)
  parse_list.append(j)


adrs = 256
for i,j in zip(adrs_list, parse_list):
  execution_dict[i] = j

l = []
def cycle(adrs):
  instr = execution_dict[adrs]
  # parse the instruction
  if instr[0:5] == "break":
    write_sim(len(l)+1, adrs, disassembler_dict[adrs])
    return 0
  else:
    temp = parse_instruction(instr)
    l.append(temp)
    eval(temp)



cycle(256)
simulation_file.close()