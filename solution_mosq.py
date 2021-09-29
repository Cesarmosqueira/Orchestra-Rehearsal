from ortools.sat.python import cp_model

model = cp_model.CpModel()

compositions = 9
durations = [int(x) for x in "2 4 1 3 3 2 5 7 6".split()]

rules = [[c == 'x' for c in 'x xx xx x'],
         [c == 'x' for c in 'x xxxx x '],
         [c == 'x' for c in 'xx  x  x '],
         [c == 'x' for c in 'x   x x x'],
         [c == 'x' for c in ' x xxxx  ']]

players = []
for rule in rules:
    players += [[]]
    for i in range(len(rule)):
        if rule[i]:
            players[-1] += [i]



# Variables

# List where index is the composition and its value the order
order = [model.NewIntVar(0, compositions, f'x{i}') for i in range(compositions)]

# Constraints 
model.AddAllDifferent(order)
model.Add(order[1] < order[7])  # composition 2 before 8
model.Add(order[4]+1 == order[5]) # composition 6 immediately after 5



wts = [model.NewIntVar(0, sum(durations), f'wt{i}') for i in range(len(rules))]
m = 0
for w in wts:  # m = current player
    # find compositions in which m doesn't participate
    cw = 0 # current wait time for m
    for c in range(rules[m].index(True), compositions):
        # c = (first true to 9)
        if not rules[m][c] and any(rules[m][c+1:]):
            cw += durations[c]
            
        print(1 if rules[m][c] else 0, end= ' ')
    print(f' -> {cw}')

    # w should be the sum of the time where m doesn't participate 
    #                              and doesn't have to be present
    model.Add(w == cw)
    m += 1

model.Minimize(sum(wts))


solver = cp_model.CpSolver()
status = solver.Solve(model) 
solution = []

if status == cp_model.OPTIMAL:
    solution = [solver.Value(c) for c in order]

    print(f"Solution: {solution}")


print("Rules:")
for p in range(len(rules)):
    print(f'Player{p+1}: ', end='   ')
    for r in rules[p]: print('x' if r else '.', end = '   ')
    print()
print('Durations:', end='  ')
for d in durations: print(d, end='   ')
print()

print("Players")
for p in players: print(p)
print()


# pretty paint solution

print("Wait timess for:", solution)

wait_times = [0 for i in range(len(rules))]
for p in range(len(rules)):
    for i in range(rules[p].index(True), compositions):
        if not i in players[p] and any(rules[p][i+1:]):
            wait_times[p] += durations[i]

print(wait_times)
print(sum(wait_times))