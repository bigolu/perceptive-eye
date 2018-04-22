#pragma once

extern "C" {
  int getNumDetect(void *img, int width, int height);
  void copyAndClean(void *__ids__, void *__buf__);
}
