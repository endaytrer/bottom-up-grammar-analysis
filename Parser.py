import abc


class Parser(abc.ABC):
    grammar: tuple[tuple[str, str]]

    terminal: tuple[str]
    non_terminal: tuple[str]

    first: dict[str, set] = {}
    follow: dict[str, set] = {"Σ": set(("#"))}
    dfa: dict[tuple[int, str], int] = {}

    def prepare(self, grammar):

        # extend grammar
        if grammar is None:
            grammar = Parser.input_grammar()
        extended_grammar = (('Σ', grammar[0][0]), *grammar)
        self.grammar = extended_grammar

        # define terminals and non-terminals

        temp_terminal = ['#']
        temp_non_terminal = []
        for generation in self.grammar:
            if generation[0] not in temp_non_terminal:
                temp_non_terminal.append(generation[0])

        self.non_terminal = tuple(temp_non_terminal)

        for generation in self.grammar:
            if '' not in temp_terminal and generation[1] == '':
                temp_terminal.append('')
            for char in generation[1]:
                if char not in self.non_terminal and char not in temp_terminal:
                    temp_terminal.append(char)
        self.terminal = tuple(temp_terminal)

    def input_grammar():
        grammar = []
        inp = input(
            'Please enter grammar ("!" means epsilon, "->" means derive, leave empty to end):\n')
        while len(inp) > 0:
            generation = inp.split('->')
            if generation[1] == '!':
                generation[1] = ''
            grammar.append(tuple(generation))
            inp = input()
        return tuple(grammar)

    def get_first(self, symbol: str):
        if symbol in self.first.keys():
            return
        self.first[symbol] = set()
        if symbol in self.terminal:
            return
        if len(symbol) == 0:
            self.first[symbol].add('')
            return
        if len(symbol) == 1:
            for generation in self.grammar:
                if generation[0] != symbol:
                    continue
                if generation[1] not in self.first.keys():
                    self.get_first(generation[1])
                if not self.first[generation[1]].issubset(self.first[symbol]):
                    self.first[symbol] = self.first[symbol].union(
                        self.first[generation[1]])
            return

        i = 0
        while i < len(symbol):
            char = symbol[i]
            if char not in self.first.keys():
                self.get_first(char)
            if not self.first[char].issubset(self.first[symbol]):
                self.first[symbol] = self.first[symbol].union(self.first[char])
            if "" not in self.first[char]:
                break
            else:
                self.first[symbol].discard('')
            i += 1
        if i == len(symbol):
            self.first[symbol].add('')
        return

    def get_follow(self, symbol):
        if symbol not in self.follow.keys():
            self.follow[symbol] = set()
        for generation in self.grammar:
            if symbol not in generation[1]:
                continue
            for i in range(len(generation[1])):
                if generation[1][i] == symbol:
                    next = i + 1
                    while next < len(generation[1]):
                        char = generation[1][next]
                        self.follow[symbol] = self.follow[symbol].union(
                            self.first[char])
                        if "" not in self.first[char]:
                            break
                        next += 1
                    if next == len(generation[1]):
                        if generation[0] not in self.follow.keys():
                            self.get_follow(generation[0])
                        self.follow[symbol] = self.follow[symbol].union(
                            self.follow[generation[0]])

    def _generate_first_follow(self):
        for char in self.terminal:
            self.first[char] = set([char])
        for generation in self.grammar:
            self.get_first(generation[0])
            self.get_first(generation[1])
        for char in self.non_terminal:
            self.get_follow(char)

    @abc.abstractmethod
    def _generate_dfa(self):
        pass

    @abc.abstractmethod
    def closure(self, kernel):
        pass

    @abc.abstractmethod
    def print_states(self):
        pass

    @abc.abstractmethod
    def _print_state(self, state):
        pass

    @abc.abstractmethod
    def get_parsing_table(self, filepath: str):
        pass
