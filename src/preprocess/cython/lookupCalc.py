import os



def lookup_16bit_to_8bit ():
	h = open('lookup_16bit_to_8bit', 'w')
	for i in range(65536): h.write(str(int(round(float(i) / 65536 * 255))) + '\n')
	h.close()


def main():
	filelist = os.listdir('.')
	if 'lookup_16bit_to_8bit' not in filelist: lookup_16bit_to_8bit()


main()