import fileinput

instruction_list = []
disassembler_list = []
adrs_list = []
register_list = 32*[0]
all_list = []

data_dict = {}
execution_dict = {}
instruction_dict = {}
disassembler_dict = {}
all_dict = {}

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
    cat1_l = []
    cat1_instr = category_1[i[25:30]]
    cat1_rs1 = i[12:17]
    cat1_offset = i[0:7] + i[20:25]
    cat1_rs2 = i[7:12]
    if cat1_instr == "sw":
      cat1_decoded = f"{cat1_instr} x{int(cat1_rs1, 2)}, {signed_convert(cat1_offset)}(x{int(cat1_rs2, 2)})"
      all_list.append([cat1_instr, f"x{int(cat1_rs1, 2)}", signed_convert(cat1_offset), f"x{int(cat1_rs2, 2)}"])
    else:
      cat1_decoded = f"{cat1_instr} x{int(cat1_rs1, 2)}, x{int(cat1_rs2, 2)}, #{signed_convert(cat1_offset)}"
      all_list.append([cat1_instr, f"x{int(cat1_rs1, 2)}", f"x{int(cat1_rs2, 2)}", signed_convert(cat1_offset)])
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
    all_list.append([cat2_instr, f"x{int(cat2_rd, 2)}", f"x{int(cat2_rs1, 2)}", f"x{int(cat2_rs2, 2)}"])
    disassembler_list.append(cat2_decoded)
    #print(cat2_decoded)


  elif i[30:32] == "10":
    cat3_instr = category_3[i[25:30]]
    cat3_offset = i[0:12]
    cat3_rd = i[20:25]
    cat3_rs1 = i[12:17]
    if cat3_instr in ["andi", "ori", "sll"]:
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, x{int(cat3_rs1, 2)}, #{int(cat3_offset, 2)}"
      all_list.append([cat3_instr, f"x{int(cat3_rd, 2)}", f"x{int(cat3_rs1, 2)}", int(cat3_offset, 2)])
    elif cat3_instr == "lw":
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, {int(cat3_offset, 2)}(x{int(cat3_rs1, 2)})"
      all_list.append([cat3_instr, f"x{int(cat3_rd, 2)}", int(cat3_offset, 2), f"x{int(cat3_rs1, 2)}"])
    else:
      cat3_decoded = f"{cat3_instr} x{int(cat3_rd, 2)}, x{int(cat3_rs1, 2)}, #{signed_convert(cat3_offset)}"
      all_list.append([cat3_instr, f"x{int(cat3_rd, 2)}", f"x{int(cat3_rs1, 2)}", signed_convert(cat3_offset)])
    disassembler_list.append(cat3_decoded)
    #print(cat3_decoded)


  elif i[30:32] == "11":
    cat4_instr = category_4[i[25:30]]
    if cat4_instr == "break":
      disassembler_list.append(f"{cat4_instr}")
      all_list.append(["break"])
      break_flag = 1
      break_index = instruction_list.index(i)
      break
    else:
      cat4_rd = i[20:25]
      cat4_offset = i[0:20]
      cat4_decoded = f"{cat4_instr} x{int(cat4_rd, 2)}, #{signed_convert(cat4_offset)}"
      all_list.append([cat4_instr, f"x{int(cat4_rd, 2)}", signed_convert(cat4_offset)])
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

for i, j in zip(instruction_list, disassembler_list):
  adrs_list.append(temp_address)
  temp_address += 4

for i,j in zip(adrs_list, instruction_list):
  instruction_dict[i] = j

for i,j in zip(adrs_list, disassembler_list):
  disassembler_dict[i] = j

for i,j in zip(adrs_list, all_list):
  all_dict[i] = j

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

parse_list = []
for i,j in zip(adrs_list, disassembler_list):
  j = j + ", " +str(i)
  parse_list.append(j)


adrs = 256
for i,j in zip(adrs_list, parse_list):
  execution_dict[i] = j

l = []

# Category-1 functions

def beq_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] == register_list[s2]:
    adrs += (offset*2)
  else:
    adrs += 4
  return adrs

def bne_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] != register_list[s2]:
    adrs += (offset*2)
  else:
    adrs += 4
  return adrs

def blt_f(s1: int, s2: int, offset: int, adrs: int):
  if register_list[s1] < register_list[s2]:
    adrs += (offset*2)
  else:
    adrs += 4
  return adrs

def sw_f(s1: int, s2: int, offset: int, adrs: int):
  data_dict[register_list[s2] + offset] = register_list[s1]


# Category-2 functions

def add_f(d: int, s1: int, s2: int, adrs: int,):
  register_list[d] = register_list[s1] + register_list[s2]

def sub_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] - register_list[s2]

def or_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] | register_list[s2]

def and_f(d: int, s1: int, s2: int, adrs: int):
  register_list[d] = register_list[s1] & register_list[s2]


# Category-3 funtions

def addi_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] + offset

def andi_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] & offset

def ori_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] | offset

def sll_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] << offset

def sra_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = register_list[s] >> offset

def lw_f(d: int, s: int, offset: int, adrs: int):
  register_list[d] = data_dict[register_list[s] + offset]


# Category-4 functions

def jal_f(d: int, offset: int, adrs: int):
  register_list[d] = adrs + 4
  adrs = adrs + 2*(offset)
  return adrs

def break_f(none):
  return none

def write_sim(pi, pa1, pm, pom, pa2, poa2, pa3, poa3):

    global fetch_wait
    global fetch_execute
    global count

    c = count
    w = fetch_wait
    e = fetch_execute

    simulation_file.write(f"--------------------\n")
    simulation_file.write(f"Cycle\t{c}:\n\n")

    simulation_file.write(f"IF Unit:\n")
    if w != 0:
      simulation_file.write(f"\tWaiting: [{disassembler_dict[w]}]\n")
    else:
      simulation_file.write(f"\tWaiting:\n")
    if e != 0:
      simulation_file.write(f"\tExecuted: [{disassembler_dict[e]}]\n")
    else:
      simulation_file.write(f"\tExecuted:\n")

    simulation_file.write(f"Pre-Issue Queue:\n")
    for i in range(0,4):
      if i < len(pi):
        simulation_file.write(f"\tEntry {i}: [{disassembler_dict[pi[i]]}]\n")
      else:
        simulation_file.write(f"\tEntry {i}:\n")

    simulation_file.write(f"Pre-ALU1 Queue:\n")
    for i in range(0,2):
      if i < len(pa1):
        simulation_file.write(f"\tEntry {i}: [{disassembler_dict[pa1[i]]}]\n")
      else:
        simulation_file.write(f"\tEntry {i}:\n")

    if len(pm) > 0:
      simulation_file.write(f"Pre-MEM Queue: [{disassembler_dict[pm[0]]}]\n")
    else:
      simulation_file.write("Pre-MEM Queue:\n")
    if len(pom) > 0:
      simulation_file.write(f"Post-MEM Queue: [{disassembler_dict[pom[0]]}]\n")
    else:
      simulation_file.write("Post-MEM Queue:\n")

    if len(pa2) > 0:
      simulation_file.write(f"Pre-ALU2 Queue: [{disassembler_dict[pa2[0]]}]\n")
    else:
      simulation_file.write("Pre-ALU2 Queue:\n")
    if len(poa2) > 0:
      simulation_file.write(f"Post-ALU2 Queue: [{disassembler_dict[poa2[0]]}]\n")
    else:
      simulation_file.write("Post-ALU2 Queue:\n")


    if len(pa3) > 0:
      simulation_file.write(f"Pre-ALU3 Queue: [{disassembler_dict[pa3[0]]}]\n")
    else:
      simulation_file.write("Pre-ALU3 Queue:\n")
    if len(poa3) > 0:
      simulation_file.write(f"Post-ALU3 Queue: [{disassembler_dict[poa3[0]]}]\n")
    else:
      simulation_file.write("Post-ALU3 Queue:\n")

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


adrs = 256
src_list = []
dst_list = []

count = 0

pre_issue = []

pre_alu_1 = []
pre_alu_2 = []
pre_alu_3 = []

pre_mem = []
post_alu_2 = []
post_alu_3 = []

post_mem = []

src_dict = {}
des_dict = {}
temp_des_list = []

fetch_flag = 1
fetch_wait = 0
fetch_execute = 0


def check_raw(adrs):
  raw_list = []
  for i in des_dict.keys():
    if i < adrs:
      raw_list.append(des_dict[i])

  if (all_dict[adrs][0] in ["jal", "beq", "bne", "blt"]):
    if (all_dict[adrs][1] in des_dict.values()) or (all_dict[adrs][2] in des_dict.values()):
      return True
  elif (all_dict[adrs][0] == "lw") and (all_dict[adrs][-1] in raw_list):
    return True
  elif (all_dict[adrs][0] == "sw") and (all_dict[adrs][1] in raw_list):
    return True
  elif (all_dict[adrs][0] in ["add","addi","sub","and", "or", "andi", "ori", "sll", "sra"]) and ((all_dict[adrs][2] in raw_list) or (all_dict[adrs][3] in raw_list)):
    return True
  return False


def check_war(adrs):
  war_list = []
  for i in src_dict.keys():
    if (i < adrs) and (i in pre_issue):
      for j in src_dict[i]:
        war_list.append(j)
  if (all_dict[adrs][0] == "lw") and (all_dict[adrs][1] in war_list):
    return True
  elif (all_dict[adrs][0] in ["add","addi","sub","and", "or", "andi", "ori", "sll", "sra"]) and ((all_dict[adrs][1] in war_list)):
    return True
  return False


def check_waw(adrs):
  waw_list = []
  for i in des_dict.keys():
    if i < adrs:
      waw_list.append(j)
  if (all_dict[adrs][0] == "lw") and (all_dict[adrs][1] in waw_list):
    return True
  elif (all_dict[adrs][0] in ["add","addi","sub","and", "or", "andi", "ori", "sll", "sra"]) and ((all_dict[adrs][1] in waw_list)):
    return True
  return False

waw_list = []

# Pipeline components ----------------------------------------------------------

# ---- fetch beigns ------------------------------------------------------------
def fetch(adrs:int):

  global fetch_flag
  global fetch_wait
  global fetch_execute
  global count
  global temp_des_list
  global pre_issue,l

  fetch_flagger = 0

  for i in range(1000):

    write_back(post_mem,post_alu_2,post_alu_3)

    if fetch_wait and not check_raw(fetch_wait):
        fetch_flagger = 1
        fetch_flag=0
        updated_address = cycle(fetch_wait)
        adrs = updated_address
        fetch_execute = fetch_wait
        fetch_wait = 0
        if all_dict[fetch_execute][0] == "break":
            break

    waw_list = pre_issue.copy()
    pre_issue = l.copy()
    
    if fetch_flag == 1:
      if all_dict[adrs][0] == "break":
        break

      if (all_dict[adrs][0] in ["jal", "beq", "bne", "blt"]) and len(pre_issue)<4:
        if check_raw(adrs) == True:
          fetch_wait = adrs
          fetch_flag = 0
        else:
          fetch_flagger = 1
          fetch_execute = adrs
          updated_address = cycle(adrs)
          adrs = updated_address
          fetch_wait = 0
          fetch_flag = 0
          if all_dict[adrs][0] == "break":
            break

      elif (all_dict[adrs][0] not in ["jal", "beq", "bne", "blt"]) and len(pre_issue)<4:
        if all_dict[adrs][0] == "break":
            break
        pre_issue.append(adrs)
        waw_list.append(adrs)

        # raw area
        if all_dict[adrs][0] != "sw":
          des_dict[adrs] = all_dict[adrs][1]
        # war-waw area
        if all_dict[adrs][0] == "sw":
          src_dict[adrs] = [all_dict[adrs][1], all_dict[adrs][-1]]
        elif all_dict[adrs][0] == "lw":
          src_dict[adrs] = [all_dict[adrs][1]]
        else:
          if all_dict[adrs][0] in ["andi", "ori", "sll", "sra", "addi"]:
            src_dict[adrs] = [all_dict[adrs][2]]
          else:
            src_dict[adrs] = [all_dict[adrs][2],all_dict[adrs][3]]

        adrs+=4
    
    if fetch_flag == 1:
      if (all_dict[adrs][0] in ["jal", "beq", "bne", "blt"]) and len(pre_issue)<4:
        if check_raw(adrs) == True:
          fetch_wait = adrs
          fetch_flag = 0
        else:
          fetch_flagger = 1
          fetch_execute = adrs
          updated_address = cycle(adrs)
          adrs = updated_address
          fetch_wait = 0
          fetch_flag = 0
          if all_dict[adrs][0] == "break":
            break

      elif (all_dict[adrs][0] not in ["jal", "beq", "bne", "blt"]) and len(pre_issue)<4:
        if all_dict[adrs][0] == "break":
            break

        pre_issue.append(adrs)
        waw_list.append(adrs)
        if all_dict[adrs][0] != "sw":
          des_dict[adrs] = all_dict[adrs][1]
        adrs+=4

    pre_issue = waw_list
    count += 1
    write_sim(pre_issue, pre_alu_1, pre_mem, post_mem, pre_alu_2, post_alu_2, pre_alu_3, post_alu_3)

    if len(temp_des_list)>0:
      for i in temp_des_list:
        del des_dict[i]
      temp_des_list = []

    if fetch_flagger:
      fetch_flag = 1
      fetch_execute = 0
# ---- fetch ends --------------------------------------------------------------


def issue(pre_issue):
  global count,l
  l = pre_issue.copy()
  for j in range(0,4):
    if len(pre_issue) > 0:
      for i in pre_issue:
        if (all_dict[i][0] in ["lw", "sw"]) and (len(pre_alu_1)<1) and (check_raw(i) != True) and (check_war(i) != True):
          pre_alu_1.append(i)
          pre_issue.remove(i)
        if (all_dict[i][0] in ["add", "sub", "addi"]) and (len(pre_alu_2)<1) and (len(post_alu_2)<1) and (check_raw(i) != True) and (check_war(i) != True):
          pre_alu_2.append(i)
          pre_issue.remove(i)
        if (all_dict[i][0] in ["and", "or", "andi", "ori", "sll", "sra"]) and (len(pre_alu_3)<1)and (len(post_alu_3)<1) and (check_raw(i) != True) and (check_war(i) != True):
          pre_alu_3.append(i)
          pre_issue.remove(i)
        

def alu(pre_alu_1: list, pre_alu_2: list, pre_alu_3: list):
  global count
  if len(pre_alu_1) > 0:
    pre_mem.append(pre_alu_1[0])
    pre_alu_1.remove(pre_alu_1[0])
  if len(pre_alu_2) > 0:
    post_alu_2.append(pre_alu_2[0])
    pre_alu_2.remove(pre_alu_2[0])
  if len(pre_alu_3) > 0:
    post_alu_3.append(pre_alu_3[0])
    pre_alu_3.remove(pre_alu_3[0])

  issue(pre_issue)


def mem(pre_mem: list):
  global count
  if len(pre_mem) > 0:
    if all_dict[pre_mem[0]][0] == "sw":
      cycle(pre_mem[0])
      pre_mem.remove(pre_mem[0])
    else:
      post_mem.append(pre_mem[0])
      pre_mem.remove(pre_mem[0])

  alu(pre_alu_1, pre_alu_2, pre_alu_3)


def write_back(post_mem: list, post_alu_2: list, post_alu_3: list):
  global count

  if len(post_mem) > 0:
    cycle(post_mem[0])
    temp_des_list.append(post_mem[0])
    post_mem.remove(post_mem[0])
  if len(post_alu_2) > 0:
    cycle(post_alu_2[0])
    temp_des_list.append(post_alu_2[0])
    post_alu_2.remove(post_alu_2[0])
  if len(post_alu_3) > 0:
    cycle(post_alu_3[0])
    temp_des_list.append(post_alu_3[0])
    post_alu_3.remove(post_alu_3[0])

  mem(pre_mem)


def cycle(adrs: int):
  instr = execution_dict[adrs]
  temp = parse_instruction(instr)
  #l.append(temp)
  ans = eval(temp)
  return ans

fetch(adrs)

for i in all_dict:
  if all_dict[i] == ["break"]:
    fetch_execute = i
count += 1
write_sim(pre_issue, pre_alu_1, pre_mem, post_mem, pre_alu_2, post_alu_2, pre_alu_3, post_alu_3)
#write_sim([], [], [], [], [], [], [], [])

simulation_file.close()