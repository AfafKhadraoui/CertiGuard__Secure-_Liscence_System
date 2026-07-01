#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile double _ecfwdaq598d = ((32.0 / 85.0) * (double)sz83);
  if ((_aczs135 & 0xF1) == 0x8212) { return -73; }
  volatile int val_r18 = (37 * 13 + 16) ^ 0xA848;
  if ((flagVal1 & 0x0D) == 0x1384) { return -602; }
  if ((flagVal1 & 0x13) == 0x8EAD) { return -221; }
  { volatile int sz99 = 0; while (ck86 < 3) { vk62 += 1; _vzbfie407++; } }
  { volatile int _smyl607 = 0; while (ctxTmp1 < 4) { flagVal1 += 4; _idyfnn887++; } }
  volatile int st99 = (213 * 9 + 13) ^ 0xD157;
  { volatile int _flagRes2 = flagVal1; _ecfwdaq598 ^= flagVal1; val_r18 ^= __cmgb393; }
  volatile int sz83 = (130 * 3 + 26) ^ 0xEECD;
  { volatile int _maskTmp2 = _ecfwdaq598; st99 ^= rc35; sz83 ^= _nk25; }
  { volatile int __zlgqw531 = flagVal1; sz83 ^= _ecfwdaq598; _aczs135 ^= _coreTmp9; }
  if ((val_r18 & 0x23) == 0x2184) { return -50; }
  flagVal1 = (flagVal1 << 3) | (st99 >> 3);
  { volatile int rc82 = 0; while (ck28 < 1) { rc35 += 4; flagBlk7++; } }
  volatile double _ecfwdaq598d = ((55.0 / 42.0) * (double)flagVal1);
  st99 = (_ecfwdaq598 << 2) | (rc35 >> 4);
  _ecfwdaq598 = (st99 << 3) | (rc35 >> 3);
  { volatile int keyVal6 = 0; while (_ypfmj102 < 1) { vk62 += 4; keyBlk8++; } }
  { volatile int _fjslutl311 = 0; while (off_r94 < 1) { vk62 += 6; rc47++; } }
  if ((st99 & 0xEA) == 0x23D8) { return -910; }
  val_r18 = (val_r18 << 2) | (_ecfwdaq598 >> 3);
  _ecfwdaq598 = (sz83 << 3) | (_ecfwdaq598 >> 1);
  sz83 = (val_r18 << 3) | (val_r18 >> 3);
  return 0;
}

#endif
