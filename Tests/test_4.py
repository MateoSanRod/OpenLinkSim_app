from typing import List
import numpy as np
def getMinimumSecondsRequired(N: int, R: List[int], A: int, B: int) -> int:
  time = 0
  i = 0
  pref = True if A > B else False
  for i in range(len(R)):
    if i == len(R)-1:
      return time
    if not pref and R[i+1]>2:
      while R[i] > R[i+1]:
        print(R[i], R[i+1])
        R[i] -= 1
        time += B
    else:
      while R[i] > R[i+1]:
        R[i] += 1
        time += A


N = 5
R = [2, 5, 3, 6, 5]
A = 1
B = 1
print(getMinimumSecondsRequired(N, R, A, B))
