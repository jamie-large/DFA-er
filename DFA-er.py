#!/usr/bin/env/python
# DFA-er interpreter
# Written by Jamie Large in March 2021
# Version 1.0
import sys

DFA = dict()
starting_state = None

# A state in the DFA with:
# name - some nonnegative integer
# accepting - whether or not the state is accepting
# paths - the transitions from this state
class State:
	def __init__(self, name, accepting=False):
		self.name = name
		self.accepting = accepting
		self.paths = dict()

	def add_path(self, symbol, destination):
		self.paths[symbol] = destination

def main():
	code = ""
	# Get the code, either as input from the user until they send EOF or from the specified file
	if (len(sys.argv) == 1):
		str_buf = []
		for line in sys.stdin:
			str_buf.append(line)
		code = ''.join(str_buf)
	else:
		try:
			with open(sys.argv[1], 'r') as f:
				code = f.read()
		except:
			print('Error reading file: ' + sys.argv[1])

	# Split the code between making the DFA and running the DFA
	parts = code.split('!', 1)
	if (len(parts) == 1):
		parts.append('')

	make_DFA(parts[0])
	run_DFA(parts[1])


# Construct the DFA from the string code
def make_DFA(code):
	c = 0
	current_state = None

	while (True):
		# If we've reached the end, stop
		if (c >= len(code)):
			return

		# If the current character is not . or -, just skip over it
		if (code[c] not in '.-'):
			c += 1
			continue

		# If we are creating a new state
		elif (code[c] == '.'):
			if (c == len(code) - 1):
				return
			c += 1

			# determine if accepting state
			accepting = False
			if (code[c] == '.'):
				accepting = True
				c += 1

			# gather the state's name
			name, offset = read_binary(code[c:], '.')
			if (name == -1):
				return
			c += offset

			# If the state already exists, get it, otherwise create it
			# Set the current state to be this state
			if (name in DFA):
				current_state = DFA[name]
				current_state.accepting = accepting
			else:
				current_state = State(name, accepting)
				if (len(DFA) == 0):
					global starting_state
					starting_state = current_state
				DFA[name] = current_state
			continue
		
		# If we are creating a new transition
		elif (code[c] == '-'):
			c += 1

			# If there are no states yet, create one
			if (current_state is None):
				current_state = State(0, False)
				DFA[0] = current_state
				starting_state = DFA[0]
			
			# gather the symbol the transition occurs on
			symbol, offset = read_binary(code[c:], '-')
			if (symbol == -1):
				return
			c += offset

			# gather the name of the destination the transition goes to
			destination_name, offset = read_binary(code[c:], '-')
			if (destination_name == -1):
				return
			c += offset
			
			# Find the actual state that is the destination, otherwise create it
			destination = None
			if (destination_name in DFA):
				destination = DFA[destination_name]
			else:
				destination = State(destination_name)
				DFA[destination_name] = destination

			current_state.add_path(symbol, destination)
			continue

# Run the DFA in the manner specified by the string code
def run_DFA(code):
	if starting_state is None:
		return
	c = 0
	current_state = starting_state
	output_string = []
	if (current_state.name <= 0x10FFFF):
		output_string.append(chr(current_state.name))
	else:
		output_string.append(str(current_state.name))
	while (True):
		# If we've reached the end, stop
		if (c >= len(code)):
			break

		# If the current character is not . or -, just skip over it
		if (code[c] not in '.-'):
			c += 1
			continue

		# If the code is manually passing input
		elif (code[c] == '.'):
			if (c == len(code) - 1):
				break
			c += 1
			# gather the input
			symbol, offset = read_binary(code[c:], '.')
			if (symbol == -1):
				break
			c += offset

			# change the state accordingly, add new state to output buffer
			if (symbol in current_state.paths):
				current_state = current_state.paths[symbol]
				if (current_state.name <= 0x10FFFF):
					output_string.append(chr(current_state.name))
				else:
					output_string.append(str(current_state.name))
			else:
				return
			continue

		# If the code is asking for user input, add it to the code to be read
		elif (code[c] == '-'):
			c += 1
			str_buf = []
			for line in sys.stdin:
				str_buf.append(line)
			ch_buf = []
			for ch in ''.join(str_buf):
				ch_buf.append(str(bin(ord(ch))))
			additional_code = '.' + '..'.join(ch_buf) + '.' if len(ch_buf) > 0 else ''
			code = additional_code + code[c:]
			c = 0
			continue

	if (current_state.accepting):
		print(''.join(output_string))

	


# Reads binary from code string until it encounters stop_char
# Returns -1 if it never encounters stop_char, otherwise converts binary to an int
# Returns 0 if it doesn't encounter any binary before stop_char
def read_binary(code, stop_char):
	c = 0
	binary_string = []
	while (True):
		if (c == len(code)):
			return -1

		if (code[c] == '0' or code[c] == '1'):
			binary_string.append(code[c])

		if (code[c] == stop_char):
			c += 1
			break
		c += 1

	result = int(''.join(binary_string), 2) if (len(binary_string) > 0) else 0

	return result, c

# Prints the structure of the DFA (useful for debugging)
def print_DFA():
	for state in DFA:
		if (DFA[state] == starting_state):
			print("STARTING STATE")
		print("state name: " + str(DFA[state].name))
		print("accepting: " + str(DFA[state].accepting))
		print("state paths: ")
		for path in DFA[state].paths:
			print("\t" + str(path) + ": " + str(DFA[state].paths[path].name))
		print()



main()