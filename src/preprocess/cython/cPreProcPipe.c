#include "cPreProcPipe.h"



int indexer (int i, int j, int k, int n, int m) {
	return(i * m * 3 + j * 3 + k);
}


int indexer2D (int i, int j, int n, int m) {
	return(i * m + j);
}


#define max(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a > _b ? _a : _b; })


#define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })



/****************** RGB-HSL CONVERSION FUNCTIONS ******************/

void col_hue_rgb (double c, double x, double m, double hue, rgb_tup* rgb) {
	double rf, gf, bf;
	rf = 0;
	gf = 0;
	bf = 0;

	if (hue < 0.0)
		hue += 1.0;
	else if (hue > 1.0)
		hue -= 1.0;
	if (hue < 0.0 || hue > 1.0)
		printf("getfucked\n");

	hue = hue * 360;

	if (hue < 60.0) {
		rf = c;
		gf = x;
	}	
	else if (hue >= 60 && hue < 120) {
		rf = x;
		gf = c;
	}
	else if (hue >= 120 && hue < 180) {
		gf = c;
		bf = x;
	}
	else if (hue >= 180 && hue < 240) {
		gf = x;
		bf = c;
	}
	else if (hue >= 240 && hue < 300) {
		rf = x;
		bf = c;
	}
	else {
		rf = c;
		bf = x;
	}

	rgb -> r = (uint16_t) ((rf + m) * 65535);
	rgb -> g = (uint16_t) ((gf + m) * 65535);
	rgb -> b = (uint16_t) ((bf + m) * 65535);
}


rgb_tup hls_rgb (double hue, double sat, double lum) {
	double c, x, m;
	rgb_tup rgb;

	if (sat == 0.0) {
		rgb.r = (uint16_t) (lum * 65535.0);
		rgb.g = (uint16_t) (lum * 65535.0);
		rgb.b = (uint16_t) (lum * 65535.0);
	}
	else {
		c = (1.0 - fabs(2.0 * lum - 1.0)) * sat;
		
		x = hue / (1.0/6.0);
		while (x >= 2)
			x = x - 2;
		x = c * (1.0 - fabs(x - 1.0));

		m = lum - c / 2.0;

		col_hue_rgb(c, x, m, hue, &rgb);
	}

	return(rgb);
}


hsl_tup rgb_hs (uint16_t r, uint16_t g, uint16_t b, uint16_t grey) {
	double l0 = (double) grey / 65535.0;
	double rf = (double) r / 65535.0;
	double gf = (double) g / 65535.0;
	double bf = (double) b / 65535.0;

	double max = max(max(rf, gf), bf);
	double min = min(min(rf, gf), bf);

	if (max == min) {
		hsl_tup hsl = {0.0, 0.0, l0};
		return(hsl);
	}

	double delta = max - min;
	double h, s;
	double l1 = (max + min) / 2.0;

	s = delta / (1.0 - fabs(2.0 * l1 - 1.0));

	if (rf == max) {
		h = (gf - bf) / delta;
		while (h >= 6.0) {
			h = h - 6.0;
		}
	}
	else if (gf == max)
		h = 2.0 + (bf - rf) / delta;
	else
		h = 4.0 + (rf - gf) / delta;
	h = h / 6.0;

	hsl_tup hsl = {h, s, l0};
	return(hsl);
}



/****************** MAIN LIBRARY FUNCTIONS ******************/

void cBilinearInter (uint16_t* inArr, uint16_t* outArr, int n, int m) {
	int i, j, nn, mm;
	nn = 2 * n - 1;
	mm = 2 * m - 1;
	for (i = 0; i < n; ++ i) {
		for (j = 0; j < m; ++j) {
			outArr[indexer(2 * i, 2 * j, 0, nn, mm)] = inArr[indexer(i, j, 0, n, m)];
			outArr[indexer(2 * i, 2 * j, 1, nn, mm)] = inArr[indexer(i, j, 1, n, m)];
			outArr[indexer(2 * i, 2 * j, 2, nn, mm)] = inArr[indexer(i, j, 2, n, m)];
		}
	}
	for (i = 1; i < n; ++ i) {
		for (j = 0; j < m; ++j) {
			outArr[indexer(2 * i - 1, 2 * j, 0, nn, mm)] = (inArr[indexer(i - 1, j, 0, n, m)] + inArr[indexer(i, j, 0, n, m)]) / 2;
			outArr[indexer(2 * i - 1, 2 * j, 1, nn, mm)] = (inArr[indexer(i - 1, j, 1, n, m)] + inArr[indexer(i, j, 1, n, m)]) / 2;
			outArr[indexer(2 * i - 1, 2 * j, 2, nn, mm)] = (inArr[indexer(i - 1, j, 2, n, m)] + inArr[indexer(i, j, 2, n, m)]) / 2;
		}
	}
	for (i = 0; i < nn; ++ i) {
		for (j = 1; j < m; ++j) {
			outArr[indexer(i, 2 * j - 1, 0, nn, mm)] = (outArr[indexer(i, 2 * j - 2, 0, nn, mm)] + outArr[indexer(i, 2 * j, 0, nn, mm)]) / 2;
			outArr[indexer(i, 2 * j - 1, 1, nn, mm)] = (outArr[indexer(i, 2 * j - 2, 1, nn, mm)] + outArr[indexer(i, 2 * j, 1, nn, mm)]) / 2;
			outArr[indexer(i, 2 * j - 1, 2, nn, mm)] = (outArr[indexer(i, 2 * j - 2, 2, nn, mm)] + outArr[indexer(i, 2 * j, 2, nn, mm)]) / 2;
		}
	}
}


void cLuminosityBlend (uint16_t* color, uint16_t* grey, int n, int m) {
	int i, j;
	for (i = 0; i < n; ++i) {
		for (j = 0; j < m; ++j) {
			hsl_tup hsl = rgb_hs(
				color[indexer(i, j, 0, n, m)],
				color[indexer(i, j, 1, n, m)],
				color[indexer(i, j, 2, n, m)],
				grey[indexer2D(i, j, n, m)]
			);
			rgb_tup rgb = hls_rgb(
				hsl.h,
				hsl.s,
				hsl.l
			);
			color[indexer(i, j, 0, n, m)] = rgb.r;
			color[indexer(i, j, 1, n, m)] = rgb.g;
			color[indexer(i, j, 2, n, m)] = rgb.b;
		}
	}
}


void cAdjustLevels (uint16_t* inArr, int n, int m) {
	int i, j, k;
	uint16_t work, min, max;

	min = 65535;
	max = 0;
	for (i = 0; i < n; ++i) {
		for (j = 0; j < m; ++j) {
			for (k = 0; k < 3; ++k) {
				work = inArr[indexer(i, j, k, n, m)];
				if (work > 0 && work < min)
					min = work;
				if (work > max && ((work - max) < 50 || work < 30000))
					max = work;
			}
		}
	}

	for (i = 0; i < n; ++i) {
		for (j = 0; j < m; ++j) {
			if (inArr[indexer(i, j, 0, n, m)] != 0)
				inArr[indexer(i, j, 0, n, m)] = (uint16_t) (((double) (inArr[indexer(i, j, 0, n, m)] - min) / (double) (max - min)) * 65535.0);
			if (inArr[indexer(i, j, 1, n, m)] != 0)
				inArr[indexer(i, j, 1, n, m)] = (uint16_t) (((double) (inArr[indexer(i, j, 1, n, m)] - min) / (double) (max - min)) * 65535.0);
			if (inArr[indexer(i, j, 1, n, m)] != 0)
				inArr[indexer(i, j, 2, n, m)] = (uint16_t) (((double) (inArr[indexer(i, j, 2, n, m)] - min) / (double) (max - min)) * 65535.0);
		}
	}
}


void c16to8 (uint16_t* inArr, uint8_t* outArr, int n, int m) {
	int i, j;
	double rf, gf, bf;
	for (i = 0; i < n; ++i) {
		for (j = 0; j < m; ++j) {
			rf  = (double) inArr[indexer(i, j, 0, n, m)] / 65535.0;
			gf  = (double) inArr[indexer(i, j, 1, n, m)] / 65535.0;
			bf  = (double) inArr[indexer(i, j, 2, n, m)] / 65535.0;

			outArr[indexer(i, j, 0, n, m)] = (uint8_t) (rf * 255.0);
			outArr[indexer(i, j, 1, n, m)] = (uint8_t) (gf * 255.0);
			outArr[indexer(i, j, 2, n, m)] = (uint8_t) (bf * 255.0);
		}
	}
}


void cWrite3x3 (uint16_t* inArr, int n, int m, char* path) {
	int i, j;
	char filepath[100];
	FILE* file;
	for (i = 0; i < n - 2; ++i) {
		for (j = 0; j < m - 2; ++j) {
			sprintf(filepath, "%s/%d-%d", path, i, j);
			file = fopen(filepath, "w");
			fprintf (file, "test");
			fclose(file);
		}
	}
}


int main() {
	return(0);
}