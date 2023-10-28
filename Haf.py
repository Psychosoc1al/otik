from collections import Counter

import private as private


class Tree:
    count = 1

    def __init__(self, left, right):
        self._left = left
        self._right = right
        self._index = Tree.count
        Tree.count += 1

    def __lt__(self, other: 'Tree'):
        return self._index < other.index

    @property
    def index(self):
        return self._index

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    def get_table(self):
        return dict(self.__get_array(''))

    def __get_array(self, code):
        if type(self._left) != Tree and type(self._right) != Tree:
            return (self._left, code + '0'), (self._right, code + '1')
        if type(self._left) != Tree:
            return (self._left, code + '0'), *(self._right.__get_array(code + '1'))
        if type(self._right) != Tree:
            return *(self._left.__get_array(code + '0')), (self._right, code + '1')
        else:
            return *(self._left.__get_array(code + '0')), *(self._right.__get_array(code + '1'))

    @staticmethod
    def generate_tree(array):
        arr = list(filter(lambda x: x[1] != 0, array))
        l = len(arr)
        while len(arr) > 1:
            arr = sorted(arr, key=lambda x: (x[1], (int(ord(x[0])) + l) if (type(x[0]) != Tree) else x[0].index), reverse=True)
            s = Tree(arr[-2][0], arr[-1][0])
            count = arr[-2][1] + arr[-1][1]
            arr = arr[:-2]
            arr.append((s, count))
        return arr[0][0]


def encode_haf_mes(message):
    print(message)
    counter = Counter(message)
    table = list(map(tuple, [(x, counter[x]) for x in counter]))
    tree = Tree.generate_tree(table)
    table = tree.get_table()
    message1 = ''
    for i in message:
        message1 = message1 + table[i]
    return message1


def decode_haf_mes(message1, table):
    message2 = ''
    tree = Tree.generate_tree(table)
    t = tree
    for i in message1:
        if i == '0':
            t = t.left
        else:
            t = t.right
        if type(t) != Tree:
            message2 += t
            t = tree

    return message2