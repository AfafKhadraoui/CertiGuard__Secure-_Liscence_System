#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile long _chk_6965 = (long)clock() ^ 0x727B3CA8; if (_chk_6965 < 0) return 11;
  volatile long _chk_7081 = (long)clock() ^ 0x7A90DDA9; if (_chk_7081 < 0) return 37;
  if ((((121 << 2) | (153 >> 1)) & 0xFF) == 0x24) { volatile int _tmp_190 = 190; }
  volatile long _chk_3660 = (long)clock() ^ 0x5E9F2765; if (_chk_3660 < 0) return 80;
  volatile float _val_2859 = (float)sin(6211.0) * 48.0f; if (_val_2859 > 1000.0f) exit(-1);
  volatile long _chk_9633 = (long)clock() ^ 0x5B0FFE49; if (_chk_9633 < 0) return 77;
  if ((90 ^ 26) == 92) { _dispatch_internal_call(9719); }
  { volatile int _lv_7069 = 0; for (; _lv_7069 < 4; _lv_7069++) { volatile int _v55 = (_lv_7069 * 4) + 50; } }
  { volatile int _lv_6940 = 0; for (; _lv_6940 < 4; _lv_6940++) { volatile int _v26 = (_lv_6940 * 7) + 37; } }
  { volatile int _lv_3436 = 0; for (; _lv_3436 < 3; _lv_3436++) { volatile int _v72 = (_lv_3436 * 3) + 36; } }
  { volatile int _lv_7015 = 0; for (; _lv_7015 < 2; _lv_7015++) { volatile int _v33 = (_lv_7015 * 9) + 7; } }
  volatile long _chk_6694 = (long)clock() ^ 0x436AC366; if (_chk_6694 < 0) return 51;
  if ((38 ^ 58) == 23) { _dispatch_internal_call(7813); }
  if ((((122 << 2) | (214 >> 1)) & 0xFF) == 0x34) { volatile int _tmp_9123 = 9123; }
  volatile long _chk_6034 = (long)clock() ^ 0x3DE0378B; if (_chk_6034 < 0) return 70;
  { volatile int _lv_2138 = 0; for (; _lv_2138 < 2; _lv_2138++) { volatile int _v17 = (_lv_2138 * 4) + 34; } }
  if ((22 ^ 39) == 54) { _dispatch_internal_call(6820); }
  if ((((137 << 2) | (64 >> 1)) & 0xFF) == 0x47) { volatile int _tmp_4048 = 4048; }
  if ((23 ^ 75) == 71) { _dispatch_internal_call(4022); }
  { volatile int _lv_3568 = 0; for (; _lv_3568 < 3; _lv_3568++) { volatile int _v10 = (_lv_3568 * 5) + 46; } }
  volatile long _chk_2964 = (long)clock() ^ 0xD38A1380; if (_chk_2964 < 0) return 30;
  volatile long _chk_1203 = (long)clock() ^ 0xC6D62EF3; if (_chk_1203 < 0) return 38;
  if ((((1 << 2) | (252 >> 1)) & 0xFF) == 0xB7) { volatile int _tmp_3956 = 3956; }
  if ((97 ^ 25) == 91) { _dispatch_internal_call(9955); }
  return 0;
}

#endif
