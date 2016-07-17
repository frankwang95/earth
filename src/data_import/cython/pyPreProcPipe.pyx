cimport numpy as np



cdef extern from "cPreProcPipe.h":
	void cBilinearInter (np.uint16_t* inArr, np.uint16_t* outArr, int n, int m)


cdef extern from "cPreProcPipe.h":
	void cLuminosityBlend (np.uint16_t* color, np.uint16_t* grey, int n, int m)


cdef extern from "cPreProcPipe.h":
	void cAdjustLevels (np.uint16_t* inArr, int n, int m)


cdef extern from "cPreProcPipe.h":
	void c16to8 (np.uint16_t* inArr, np.uint8_t* outArr, int n, int m)


cdef extern from "cPreProcPipe.h":
	void cWrite3x3 (np.uint8_t* inArr, int n, int m, char* path)


def pyBilinearInter(inArr, outArr):
	return cBilinearInter (
		<np.uint16_t*> np.PyArray_DATA(inArr),
		<np.uint16_t*> np.PyArray_DATA(outArr),
		inArr.shape[0],
		inArr.shape[1]
	)


def pyLuminosityBlend(color, grey):
	return cLuminosityBlend (
		<np.uint16_t*> np.PyArray_DATA(color),
		<np.uint16_t*> np.PyArray_DATA(grey),
		color.shape[0],
		color.shape[1]
	)


def pyAdjustLevels (inArr):
	return cAdjustLevels (
		<np.uint16_t*> np.PyArray_DATA(inArr),
		inArr.shape[0],
		inArr.shape[1]
	)


def py16to8 (inArr, outArr):
	return c16to8 (
		<np.uint16_t*> np.PyArray_DATA(inArr),
		<np.uint8_t*> np.PyArray_DATA(outArr),
		inArr.shape[0],
		inArr.shape[1]
	)
