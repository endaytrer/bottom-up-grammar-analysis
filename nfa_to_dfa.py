def hash_of_set():
    return hash()


def e_close(states: set[int], transitions: list[dict[int, set[int]]]):
    temp: set[int] = set()
    new_temp: set[int] = states
    while new_temp != temp:
        temp = new_temp
        for ele in temp:
            try:
                new_temp = new_temp.union(transitions[ele][-1])
            except:
                pass
    return temp


# 输入-1号转移为e转移

def nfa_to_dfa(start: int, alphabet_size: int, transitions: list[dict[int, set[int]]]):
    new_transitions: list[tuple[set[int], list[set[int]]]] = []
    e_close_start = e_close({start}, transitions)
    undetermined_stack: list[set[int]] = []
    determined_array: list[set[int]] = []
    undetermined_stack.append(e_close_start)
    while len(undetermined_stack) > 0:
        temp = undetermined_stack.pop()
        determined_array.append(temp)
        temp_ans = []
        for input in range(alphabet_size):
            ans_set: set[int] = set()
            for state in temp:
                try:
                    ans_set = ans_set.union(transitions[state][input])
                except:
                    pass
            ans_set = e_close(ans_set, transitions)
            temp_ans.append(ans_set)
            if len(ans_set) > 0:
                try:
                    undetermined_stack.index(ans_set)
                except:
                    try:
                        determined_array.index(ans_set)
                    except:
                        undetermined_stack.append(ans_set)
        new_transitions.append((temp, temp_ans))
    return new_transitions


nfa = [{1: {1}}, {0: {8}, 1: {2, 5}}, {0: {3}}, {1: {4}},
       {-1: {1}, 0: {4}}, {0: {6}, 1: {1}}, {1: {7}}, {0: {5}}]
a = nfa_to_dfa(0, 2, nfa)
print(a)
