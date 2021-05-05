# Program that will generate a cat program in DFA-er
with open('cat', 'w') as f:
	for i in range(0,256):
		f.write('..')
		f.write(bin(i))
		f.write('.')
		for j in range(0,256):
			f.write('-')
			f.write(bin(j))
			f.write('-')
			f.write(bin(j))
			f.write('-')
	f.write('!-')