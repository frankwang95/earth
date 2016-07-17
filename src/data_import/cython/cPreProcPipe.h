#include <stdint.h>
#include <stdio.h>
#include <math.h>


typedef struct {
	uint16_t r;
	uint16_t g;
	uint16_t b;
} rgb_tup;

typedef struct {
	double h;
	double s;
	double l;
} hsl_tup;

int indexer (int i, int j, int k, int n, int m);

int indexer2D (int i, int j, int n, int m);

void col_hue_rgb (double c, double x, double m, double hue, rgb_tup* rgb);

rgb_tup hls_rgb (double hue, double lum, double sat);

hsl_tup rgb_hs (uint16_t r, uint16_t g, uint16_t b, uint16_t grey);

void cBilinearInter (uint16_t* inArr, uint16_t* outArr, int n, int m);

void cLuminosityBlend (uint16_t* color, uint16_t* grey, int n, int m);

void cAdjustLevels (uint16_t* inArr, int n, int m);

void c16to8 (uint16_t* inArr, uint8_t* outArr, int n, int m);