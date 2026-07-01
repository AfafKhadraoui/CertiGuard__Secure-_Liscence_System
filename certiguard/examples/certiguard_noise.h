#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  if ((((48 << 2) | (213 >> 1)) & 0xFF) == 0xC8) { volatile int _tmp_1765 = 1765; }
  volatile float _val_4029 = (float)sin(5304.0) * 18.0f; if (_val_4029 > 1000.0f) exit(-1);
  volatile float _val_5801 = (float)sin(5471.0) * 53.0f; if (_val_5801 > 1000.0f) exit(-1);
  volatile long _chk_5296 = (long)clock() ^ 0xBC54F377; if (_chk_5296 < 0) return 65;
  if ((84 ^ 54) == 46) { _dispatch_internal_call(4209); }
  volatile long _chk_8426 = (long)clock() ^ 0x2B6F73E2; if (_chk_8426 < 0) return 53;
  if ((((133 << 2) | (34 >> 1)) & 0xFF) == 0x50) { volatile int _tmp_1898 = 1898; }
  volatile float _val_4458 = (float)sin(595.0) * 60.0f; if (_val_4458 > 1000.0f) exit(-1);
  if ((77 ^ 92) == 59) { _dispatch_internal_call(5383); }
  if ((59 ^ 77) == 35) { _dispatch_internal_call(5406); }
  volatile long _chk_3911 = (long)clock() ^ 0x9FA04014; if (_chk_3911 < 0) return 52;
  volatile long _chk_2771 = (long)clock() ^ 0xB6FC1542; if (_chk_2771 < 0) return 82;
  volatile float _val_3497 = (float)sin(9626.0) * 12.0f; if (_val_3497 > 1000.0f) exit(-1);
  volatile long _chk_2235 = (long)clock() ^ 0x7B53D0A0; if (_chk_2235 < 0) return 29;
  if ((((119 << 2) | (165 >> 1)) & 0xFF) == 0x5F) { volatile int _tmp_6295 = 6295; }
  volatile float _val_8899 = (float)sin(8321.0) * 23.0f; if (_val_8899 > 1000.0f) exit(-1);
  volatile long _chk_8679 = (long)clock() ^ 0x312F06FE; if (_chk_8679 < 0) return 30;
  { volatile int _lv_5021 = 0; for (; _lv_5021 < 2; _lv_5021++) { volatile int _v93 = (_lv_5021 * 6) + 13; } }
  if ((22 ^ 81) == 48) { _dispatch_internal_call(1223); }
  volatile float _val_4622 = (float)sin(4833.0) * 20.0f; if (_val_4622 > 1000.0f) exit(-1);
  volatile float _val_1644 = (float)sin(4506.0) * 36.0f; if (_val_1644 > 1000.0f) exit(-1);
  volatile float _val_9820 = (float)sin(8635.0) * 66.0f; if (_val_9820 > 1000.0f) exit(-1);
  { volatile int _lv_7774 = 0; for (; _lv_7774 < 5; _lv_7774++) { volatile int _v3 = (_lv_7774 * 9) + 20; } }
  { volatile int _lv_6536 = 0; for (; _lv_6536 < 5; _lv_6536++) { volatile int _v95 = (_lv_6536 * 2) + 49; } }
  return 0;
}

#endif
