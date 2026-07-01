#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile long _chk_3152 = (long)clock() ^ 0xFB6E06E8; if (_chk_3152 < 0) return 93;
  volatile long _chk_1275 = (long)clock() ^ 0x582B5ABE; if (_chk_1275 < 0) return 72;
  volatile float _val_2120 = (float)sin(4198.0) * 99.0f; if (_val_2120 > 1000.0f) exit(-1);
  { volatile int _lv_4805 = 0; for (; _lv_4805 < 3; _lv_4805++) { volatile int _v88 = (_lv_4805 * 7) + 45; } }
  if ((((238 << 2) | (221 >> 1)) & 0xFF) == 0x57) { volatile int _tmp_1810 = 1810; }
  { volatile int _lv_4010 = 0; for (; _lv_4010 < 4; _lv_4010++) { volatile int _v65 = (_lv_4010 * 10) + 8; } }
  volatile long _chk_4349 = (long)clock() ^ 0xAD22D87F; if (_chk_4349 < 0) return 44;
  if ((((23 << 2) | (94 >> 1)) & 0xFF) == 0x5B) { volatile int _tmp_1756 = 1756; }
  volatile long _chk_6945 = (long)clock() ^ 0x2AFFABE9; if (_chk_6945 < 0) return 19;
  if ((50 ^ 42) == 100) { _dispatch_internal_call(3354); }
  volatile float _val_3808 = (float)sin(899.0) * 100.0f; if (_val_3808 > 1000.0f) exit(-1);
  volatile long _chk_8218 = (long)clock() ^ 0xBC454859; if (_chk_8218 < 0) return 5;
  if ((74 ^ 64) == 34) { _dispatch_internal_call(1467); }
  if ((((88 << 2) | (196 >> 1)) & 0xFF) == 0x67) { volatile int _tmp_4453 = 4453; }
  if ((((228 << 2) | (178 >> 1)) & 0xFF) == 0x9B) { volatile int _tmp_7916 = 7916; }
  if ((80 ^ 45) == 81) { _dispatch_internal_call(2139); }
  if ((((79 << 2) | (118 >> 1)) & 0xFF) == 0xEA) { volatile int _tmp_74 = 74; }
  { volatile int _lv_8847 = 0; for (; _lv_8847 < 5; _lv_8847++) { volatile int _v5 = (_lv_8847 * 2) + 44; } }
  { volatile int _lv_8246 = 0; for (; _lv_8246 < 5; _lv_8246++) { volatile int _v49 = (_lv_8246 * 10) + 37; } }
  { volatile int _lv_1664 = 0; for (; _lv_1664 < 3; _lv_1664++) { volatile int _v58 = (_lv_1664 * 5) + 1; } }
  if ((((10 << 2) | (219 >> 1)) & 0xFF) == 0x73) { volatile int _tmp_7660 = 7660; }
  volatile float _val_9075 = (float)sin(3302.0) * 16.0f; if (_val_9075 > 1000.0f) exit(-1);
  volatile long _chk_1783 = (long)clock() ^ 0xDF8764BB; if (_chk_1783 < 0) return 67;
  if ((9 ^ 33) == 83) { _dispatch_internal_call(1685); }
  return 0;
}

#endif
