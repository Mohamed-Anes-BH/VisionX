# Check if 4 persons can finish within 18 seconds
# Tasks:
# A: dur=8, preds=[]
# B: dur=2, preds=[]
# C: dur=6, preds=[B]
# D: dur=8, preds=[B]
# E: dur=5, preds=[B]
# F: dur=5, preds=[B]
# G: dur=8, preds=[A, E]
# H: dur=8, preds=[A, F]
# I: dur=2, preds=[G, H, C, D]
# J: dur=10, preds=[E, F]

# Total work:
# Sum of durations = 8 + 2 + 6 + 8 + 5 + 5 + 8 + 8 + 2 + 10 = 62 person-seconds.
# With P persons in 18 seconds, max capacity = 18 * P.
# For P = 3: 3 * 18 = 54 < 62 -> IMPOSSIBLE!
# For P = 4: 4 * 18 = 72 >= 62 -> Mathematically possible if no bottleneck!
# For P = 5: 5 * 18 = 90.

# Let's test if P=4 can schedule all tasks without exceeding 18 seconds:
from itertools import permutations

# Let's simulate minute by minute / second by second with 4 persons:
# Second 0 to 2 (2s):
# Can run: A, B. (Needs 2 persons). 2 persons idle.
# Work done: A (2s), B (2s -> DONE). Total work = 4.

# Second 2 to 7 (5s):
# Available: A (needs 6s), E (needs 5s), F (needs 5s), C (needs 6s), D (needs 8s).
# Active with 4 persons:
# Person 1: A (runs 2..7, needs 1s left at t=7)
# Person 2: E (runs 2..7 -> DONE at t=7)
# Person 3: F (runs 2..7 -> DONE at t=7)
# Person 4: D (runs 2..7, 5s done, needs 3s left) or C.
# If Person 4 runs D: D has 3s left. C has not started (needs 6s).

# Second 7 to 8 (1s):
# Available: A (needs 1s), D (needs 3s), C (needs 6s), J (needs 10s).
# Note: G and H cannot start yet because A is not finished until t=8!
# Active with 4 persons:
# Person 1: A (runs 7..8 -> DONE at t=8)
# Person 2: J (runs 7..8, 1s done, needs 9s left)
# Person 3: D (runs 7..8, 6s done, needs 2s left)
# Person 4: C (runs 7..8, 1s done, needs 5s left)

# Second 8 to 16 (8s):
# At t=8, A, E, F are done!
# So G (8s) and H (8s) can START at t=8!
# Notice: G and H are CRITICAL: to finish at t=16, G and H MUST run continuously from 8 to 16!
# So Person 1 takes G [8, 16] (8s -> DONE at 16)
# Person 2 takes H [8, 16] (8s -> DONE at 16)
# Now we have 2 persons left (Person 3 and Person 4) for:
# - J: needs 9s! But window is from 8 to 18 (10s)! J can finish by 8 + 9 = 17s!
# - D: needs 2s! (runs 8..10 -> DONE at 10)
# - C: needs 5s! (runs 10..15 -> DONE at 15)
# Let's check Person 3 and Person 4:
# Person 3: runs J from 8 to 17 (9s) -> DONE at t=17!
# Person 4: runs D from 8 to 10 (2s) -> D is DONE at t=10!
# Then Person 4 runs C from 10 to 15 (5s) -> C is DONE at t=15!

# Second 16 to 18 (2s):
# At t=16: G, H, D, C are all DONE!
# Task I (Baisser la voiture, 2s) can run from 16 to 18!
# Person 1 (or 2, or 4) runs I from 16 to 18 -> DONE at t=18!
# Person 3 finishes J at t=17!
# At t=18, ALL 10 TASKS ARE FINISHED!
print("SCHEDULING WITH 4 PERSONS IS FEASIBLE IN 18 SECONDS!")

