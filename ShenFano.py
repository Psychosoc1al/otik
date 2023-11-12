from collections import Counter


class Tree:
    count = 1

    def __init__(self, left, right):
        self._left = left
        self._right = right
        self._index = Tree.count
        Tree.count += 1

    def __lt__(self, other: 'Tree'):
        return self._index < other.index

    # Создал для того, чтобы была нумерация у узлов дерева для сортировки
    @property
    def index(self):
        return self._index

    # Левая ветка, 0
    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    # Правая ветка, 1
    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    # Создаёт словарь, где ключ - символ, значение - его код
    def get_table(self) -> dict:
        return dict(self.__get_array(''))

    # Используется в методе выше
    def __get_array(self, code):
        if type(self._left) != Tree and type(self._right) != Tree:
            return (self._left, code + '0'), (self._right, code + '1')
        if type(self._left) != Tree:
            return (self._left, code + '0'), *(self._right.__get_array(code + '1'))
        if type(self._right) != Tree:
            return *(self._left.__get_array(code + '0')), (self._right, code + '1')
        else:
            return *(self._left.__get_array(code + '0')), *(self._right.__get_array(code + '1'))

    # Генерирует дерево по списку пар (символ, количество)
    # Возвращает корень дерева
    @staticmethod
    def generate_tree(array):
        l = len(array)
        arr = sorted(array, key=lambda x: (x[1], int(ord(x[0])) + l), reverse=True)
        return Tree.__recursion(arr)

    @staticmethod
    def __recursion(array):
        if len(array) == 1:
            return array[0][0]
        else:
            min = sum([x[1] for x in array])
            i = 1
            while min > abs(sum([x[1] for x in array[i:]]) - sum([x[1] for x in array[:i]])):
                min = abs(sum([x[1] for x in array[i:]]) - sum([x[1] for x in array[:i]]))
                i += 1
            i -= 1
            arr1 = array[:i]
            arr2 = array[i:]
            return Tree(Tree.__recursion(array[:i]), Tree.__recursion(array[i:]))


# Кодирует сообщение по алгоритму Шеннона-Фано
# На входе - сообщение в символах
# На выходе - сообщение в бинарном виде
def encode_haf_mes(message):
    counter = Counter(message)
    table = list(map(tuple, [(x, counter[x]) for x in counter]))
    tree = Tree.generate_tree(table)
    table = tree.get_table()
    message1 = ''
    for i in message:
        message1 = message1 + table[i]
    return message1


# Декодирует сообщение по алгоритму Шеннона-Фано
# На входе - сообщение в бинарном виде и таблица частот
# На выходе - сообщение в символах
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


if __name__ == '__main__':
    with open('picture.bmp', 'rb') as f:
        message = f.read()
    message = ''.join([chr(x) for x in message])
    # message = "3242567520675462"
    print(message)
    c = Counter(message)
    table = list(map(tuple, [(x, c[x]) for x in c]))
    print(decode_haf_mes(encode_haf_mes(message), [(x, c[x]) for x in c]))
