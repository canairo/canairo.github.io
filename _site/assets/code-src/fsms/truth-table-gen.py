
limit = 2**4
primes = [2]
for i in range(3, limit):
    for _ in range(2, i):
        if i % _ == 0: break
    else:
        primes.append(i)

primes.append(2)
mappings = {0:2}

for i in range(len(primes) - 1):
    mappings[primes[i]] = primes[i + 1]

for i in range(limit):
    if i not in mappings:
        mappings[i] = False

print(mappings)

import graphviz

states = {
    0: 2, 2: 3, 3: 5, 5: 7, 7: 11, 11: 13, 13: 2,
}

dot = graphviz.Digraph(comment='FSM')

for state, next_state in states.items():
    dot.node(str(state))  # create node
    if next_state is False:
        dot.node(str(state), shape='doublecircle', style='filled', color='lightgray')
    else:
        dot.edge(str(state), str(next_state))

dot.attr(rankdir='LR')
dot.render('fsm', format='png', view=True)

