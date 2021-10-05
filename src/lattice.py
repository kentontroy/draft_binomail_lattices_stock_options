#!/usr/bin/python

from __future__ import division
from warnings import filterwarnings
from scipy.stats import binom
import collections
import math

filterwarnings("ignore")

INITIAL_STOCK_PRICE = 54
STRIKE_PRICE = 50
UP = 1.2
DOWN = 0.8
PERIODS = 5
RISK_FREE_RATE = 1 + 0.005/12
EARLY_EXERCISE_PUTS = []

def createLattice(s0, k, u, d, n, r, isForCall=True):
  if not isForCall:
    del EARLY_EXERCISE_PUTS[:]

  s = []
  s.append(s0)

  o_map = {}
  prob = []
  prob.append(1)

  ind = 1
  for i in range(1, n+1):
    for j in reversed(range(0, i+1)):
     s_val = s0 * (u**j) * (d**(i-j))
     s.append(s_val)

     prob_val = binom.pmf(j,i,0.4)
     prob.append(prob_val)
     if i==n:
       if isForCall:
         o_map[ind] = max(s_val - k, 0)
       else:
        o_map[ind] = max(k - s_val, 0)

     ind = ind + 1

  o = [0] * len(s)
  RISK_NEUTRAL_PROB = (RISK_FREE_RATE - d) / (u - d)
  periods = n
  while periods >= 0:
    for i in o_map:
      o[i] = o_map[i]
    o_map = createLattice_Helper(o_map, RISK_FREE_RATE, RISK_NEUTRAL_PROB, isForCall, k, s) 
    periods = periods - 1
  return s, o, prob

def createGraphSpec(s, o, p, showOptions=False, showEarlyExercise=False, showProb=False):
  spec = "digraph Binomial_Lattice {\n"
  spec = spec + "\t node[shape=plaintext];\n"
  spec = spec + "\t rankdir=LR;\n"
  spec = spec + "\t edge[arrowhead=none];\n"
  if not showOptions:
    for i in range(len(s)):
      node = "\t node{0}".format(i)
      label = "[label=\"{0}\"];\n".format(round(s[i],2))
      spec = spec + node + label
    if showProb:
      for i in range(len(s)):
        node = "\t node{0}".format(i)
        label = "[label=\"{0}\n{1}\"];\n".format(round(s[i],2),round(prob[i],3))
        spec = spec + node + label
    else:
      for i in range(len(s)):
        node = "\t node{0}".format(i)
        if not showEarlyExercise:
          label = "[label=\"{0}\n{1}\"];\n".format(round(s[i],2),round(o[i],2))

  else:
    if i in EARLY_EXERCISE_PUTS:
      label = "[label=\"{0}\n{1}\",shape=box];\n".format(round(s[i],2),round(o[i],2))
    else:
      label = "[label=\"{0}\n{1}\"];\n".format(round(s[i],2),round(o[i],2))

    spec = spec + node + label

  nLevels = int((math.sqrt(8*len(s)+1)-1)/2 - 1)
  k = 0
  for i in range(0, nLevels+1):
    j = i
    while(j > 0):
      spec = spec + "\t node{0}->node{1};\n".format(k, k+i)
      spec = spec + "\t node{0}->node{1};\n".format(k, k+i+1)
      k = k + 1
      j = j - 1

 return spec + "}"

if __name__=='__main__':
  price_values, put_values, prob = createLattice(INITIAL_STOCK_PRICE, STRIKE_PRICE, UP, DOWN, PERIODS,
    RISK_FREE_RATE, False)

  spec = createGraphSpec(price_values, put_values, prob, True, True)

  f = open('put_lattice.dot', 'w')
  f.write(spec)
  f.close()
