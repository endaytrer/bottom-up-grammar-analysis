import csv

from Parser import Parser


class LR1_Parser(Parser):
    # [generationId, dotIndex, input_char[terminal]]
    states: list[dict[tuple[int, int], set[str]]] = []

    def __init__(self, grammar: tuple[tuple[str, str]] or None):
        self.prepare(grammar)
        # generate first set and follow set

        self._generate_first_follow()

        # generate dfa
        self._generate_dfa()

    def _generate_dfa(self):
        initial = {(0, 0): {'#'}}
        visited = []
        stack = [self.closure(initial, visited)]
        while len(stack) > 0:
            index = stack.pop()
            state = self.states[index]
            visited[index] = True
            valid_input: dict[str, set[tuple[int, int]]] = {}
            for item in state:
                generation_right = self.grammar[item[0]][1]
                if len(generation_right) == item[1]:
                    continue
                next_input = generation_right[item[1]]
                if next_input not in valid_input.keys():
                    valid_input[next_input] = set()
                valid_input[next_input].add(item)
            for input in valid_input.keys():
                kernel: dict[tuple[int, int], set[str]] = {}
                for item in valid_input[input]:
                    if (item[0], item[1] + 1) not in kernel.keys():
                        kernel[(item[0], item[1] + 1)] = set()
                    kernel[(item[0], item[1] + 1)] = kernel[(item[0],
                                                             item[1] + 1)].union(state[item])
                closure_id = self.closure(kernel, visited)
                self.dfa[(index, input)] = closure_id
                if not visited[closure_id] and closure_id not in stack:
                    stack.append(closure_id)

    def closure(self, kernel: dict[tuple[int, int], set[str]], visited: list[bool]) -> int:
        original_kernel: dict[tuple[int, int], set[str]] = {}
        while kernel != original_kernel:
            original_kernel = kernel.copy()
            for item in original_kernel:
                generation_right = self.grammar[item[0]][1]
                if len(generation_right) == item[1]:
                    continue
                next_input = generation_right[item[1]]
                if next_input in self.non_terminal:
                    remained = self.grammar[item[0]][1][item[1] + 1:]
                    if len(remained) > 0:
                        if remained not in self.first.keys():
                            self.get_first(remained)
                        input_set = self.first[remained]
                        if "" in self.first[remained]:
                            input_set.discard("")
                            input_set = input_set.union(
                                original_kernel[item])
                    else:
                        input_set = original_kernel[item]
                    for i in range(len(self.grammar)):
                        generation = self.grammar[i]
                        if generation[0] == next_input:
                            if (i, 0) not in kernel.keys():
                                kernel[(i, 0)] = set()
                            kernel[(i, 0)] = kernel[(i, 0)].union(input_set)
        for i in range(len(self.states)):
            state = self.states[i]
            if state == kernel:
                return i
        self.states.append(kernel)
        visited.append(False)
        return len(self.states) - 1

    def print_states(self):
        for i in range(len(self.states)):
            print('State', i)
            self._print_state(self.states[i])
            print()

    def _print_state(self, state: dict[tuple[int, int], set[str]]):
        for item in state:
            generation = self.grammar[item[0]]
            dot_pnt = item[1]
            print(generation[0], '->', generation[1]
                  [0:dot_pnt] + '·' + generation[1][dot_pnt:], ',', state[item])

    def get_parsing_table(self, filepath: str, ignore_conflict: bool=False):
        with open(filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([''] + list(self.terminal) +
                            list(self.non_terminal[1:]))
            characters = self.terminal + self.non_terminal[1:]
            terminal_len = len(self.terminal)
            for i in range(len(self.states)):
                state = self.states[i]
                row = [i] + [''] * len(characters)
                for j in range(len(characters)):
                    char = characters[j]
                    if (i, char) in self.dfa.keys():
                        if j < terminal_len:
                            row[j + 1] = 's' + str(self.dfa[(i, char)])
                        else:
                            row[j + 1] = self.dfa[(i, char)]
                for item in state:
                    if len(self.grammar[item[0]][1]) == item[1]:
                        for input in state[item]:
                            index = self.terminal.index(input)
                            if row[index + 1] != '':
                                if row[index + 1][0] == 's' and not ignore_conflict:
                                    raise Exception("移进-归约冲突")
                                else:
                                    raise Exception("归约-归约冲突")
                            if item[0] == 0 and input == '#':
                                row[index + 1] += 'acc'
                            else:
                                row[index + 1] += 'r' + str(item[0])
                writer.writerow(row)


grammar = (
    ("E", "E+T"),
    ("E", "T"),
    ("T", "TF"),
    ("T", "F"),
    ("F", "F*"),
    ("F", "(E)"),
    ("F", "a"),
    ("F", "b"),
    ("F", "^")
)
# grammar = (
#     ("E", "AA"),
#     ("A", "aA"),
#     ("A", "b")
# )
parser = LR1_Parser(None)
parser.print_states()
parser.get_parsing_table('parsing_lr1.csv')
