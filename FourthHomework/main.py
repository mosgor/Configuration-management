import struct
import yaml
import math
import sys


class Assembler:
	@staticmethod
	def assemble(input_file, binary_file, log_file):
		instructions = []
		with open(input_file, 'r') as file:
			lines = file.readlines()
		
		binary_instructions = []
		
		for line in lines:
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			
			parts = line.split()
			command = parts[0].lower()
			
			if command == "load":
				# A=9, B=Address, C=Constant
				A, B, C = 9, int(parts[1]), int(parts[2])
				instruction = (A << 28) | (B << 24) | C
				binary_instructions.append(struct.pack('<I', instruction))
				instructions.append({"command": "load", "A": A, "B": B, "C": C})
			
			elif command == "read":
				# A=1, B=Address, C=BaseAddress, D=Offset
				A, B, C, D = 1, int(parts[1]), int(parts[2]), int(parts[3])
				instruction = (A << 28) | (B << 24) | (C << 20) | (D << 15)
				binary_instructions.append(struct.pack('<I', instruction))
				instructions.append({"command": "read", "A": A, "B": B, "C": C, "D": D})
			
			elif command == "write":
				# A=5, B=Address, C=Source
				A, B, C = 5, int(parts[1]), int(parts[2])
				instruction = (A << 28) | (B << 24) | (C << 20)
				binary_instructions.append(struct.pack('<I', instruction))
				instructions.append({"command": "write", "A": A, "B": B, "C": C})
			
			elif command == "sqrt":
				# A=0, B=Destination, C=Source
				A, B, C = 0, int(parts[1]), int(parts[2])
				instruction = (A << 28) | (B << 24) | (C << 20)
				binary_instructions.append(struct.pack('<I', instruction))
				instructions.append({"command": "sqrt", "A": A, "B": B, "C": C})
		
		# Save binary file
		with open(binary_file, 'wb') as bin_file:
			bin_file.writelines(binary_instructions)
		
		# Save log file
		with open(log_file, 'w') as log:
			yaml.dump(instructions, log, allow_unicode=True)


class Interpreter:
	def __init__(self):
		self.memory = [0] * 256
		self.registers = [0] * 8
	
	def execute(self, binary_file, result_file, memory_range):
		with open(binary_file, 'rb') as file:
			instructions = file.read()
		
		for i in range(0, len(instructions), 4):
			instruction = struct.unpack('<I', instructions[i:i + 4])[0]
			self._execute_instruction(instruction)
		
		start, end = memory_range
		result = self.memory[start:end]
		
		with open(result_file, 'w') as file:
			yaml.dump({"memory": result}, file, allow_unicode=True)
	
	def _execute_instruction(self, instruction):
		A = (instruction >> 28) & 0xF
		B = (instruction >> 24) & 0xF
		
		if A == 9:  # Load
			C = instruction & 0xFFFFFF
			self.registers[B] = C
		elif A == 1:  # Read
			C = (instruction >> 20) & 0xF
			D = (instruction >> 15) & 0x1F
			address = self.registers[C] + D
			self.registers[B] = self.memory[address]
		elif A == 5:  # Write
			C = (instruction >> 20) & 0xF
			address = self.registers[B]
			self.memory[address] = self.registers[C]
		elif A == 0:  # Sqrt
			C = (instruction >> 20) & 0xF
			self.registers[B] = int(math.sqrt(self.registers[C]))


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description="Assembler and Interpreter for UVM.")
	subparsers = parser.add_subparsers(dest="mode")
	
	assemble_parser = subparsers.add_parser("assemble")
	assemble_parser.add_argument("input_file", help="Path to input assembly file", default="input.txt")
	assemble_parser.add_argument("binary_file", help="Path to output binary file", default="output.bin")
	assemble_parser.add_argument("log_file", help="Path to log file", default="log.yaml")
	
	interpret_parser = subparsers.add_parser("interpret")
	interpret_parser.add_argument("binary_file", help="Path to input binary file", default="output.bin")
	interpret_parser.add_argument("result_file", help="Path to result file", default="result.yaml")
	interpret_parser.add_argument("memory_range", nargs=2, type=int, help="Memory range to save (start end)")
	
	args = parser.parse_args()
	
	if args.mode == "assemble":
		Assembler.assemble(args.input_file, args.binary_file, args.log_file)
	elif args.mode == "interpret":
		interpreter = Interpreter()
		interpreter.execute(args.binary_file, args.result_file, args.memory_range)
