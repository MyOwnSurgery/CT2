import numpy as np
import bitarray as ba


class CyclicCode:

    def __init__(self, k=7, n=15, g=(1, 0, 0, 0, 1, 0, 1, 1, 1)):
        self.k = k
        self.n = n
        self.g = g

    def xor(self, a, b):
        return [1 if a[j] != b[j] else 0 for j in range(self.n)]

    def multiply(self, a):
        c = [0] * self.n
        for i in range(self.k):
            if a[i] == 1:
                g_stub = list(self.g)
                g_stub = [0] * i + g_stub + [0] * (self.n - self.k - i)
                c = self.xor(c, g_stub)
        return c

    def remainder(self, c):
        r = np.full(self.n, 0)
        for i in range(self.n):
            r[i] = c[i]
        i = self.n - 1
        while i >= self.n - self.k:
            if (r[i]):
                r[i - (self.n - self.k):i + 1] = r[i - (self.n - self.k):i + 1] ^ self.g
            i = i - 1
        return r[0:len(self.g) - 1]

    def encode(self, a):
        c = [0] * self.n
        c[self.n - self.k:self.n] = a
        r = self.remainder(c)
        c[0:self.n - self.k] = r
        return c

    def make_table(self, t):
        syndromes = {}
        for err in self.get_lines():
            if self.wt(err) <= t:
                synd = self.remainder(err)
                syndromes[tuple(synd)] = err
        return syndromes

    def wt(self, err):
        num = [int(i) for i in err if int(i) == 1]
        return len(num)

    def get_lines(self):
        l = []
        for x in range(2 ** self.n - 1):
            n = ""
            while x > 0:
                y = str(x % 2)
                n = y + n
                x = int(x / 2)
            for i in range(self.n - len(n)):
                n = '0' + n
            l.append(n)
        last = '1'
        first = '0'
        for i in range(0,self.n-1):
            last += '1'
            first += '0'
        l.append(last)
        l[0] = first
        return l

    def code_decode(self,path):
        bits = ba.bitarray()
        with open(path, 'rb') as fh2:
            a = bits.fromfile(fh2)
        print(bits)
        j = 0
        coded = []
        i = 0
        nulls = 0
        while j < len(bits):
            a = list(bits[j:j + self.k])
            if len(a) < self.k:
                while len(a) != self.k:
                    nulls = nulls + 1
                    a.append(False)
            b = np.zeros(self.k)

            for k in range(0, self.k):
                if a[k]:
                    b[k] = 1
                else:
                    b[k] = 0

            coded[i:i + self.n] = self.encode(b)

            j = j + self.k
            i = i + self.n

        j = 0
        i = 0
        res = []
        table = self.make_table(2)
        coded[8] = 1
        while j < len(coded):
            string = coded[j:j + self.n]
            rem = self.remainder(string)
            if np.count_nonzero(rem) == 0:
                new_str = string[self.k+1:self.n]
                res[i:i + self.k] = new_str
            else:
                table_res = table[tuple(rem)]
                rem_list = list(table_res)
                remlist = [int(n) for n in rem_list]

                new_str = self.xor(string, remlist)
                res[i:i + self.k] = new_str[self.k+1:self.n]

            j = j + self.n
            i = i + self.k
        res = res[0:len(res)-nulls]
        bits2 = ba.bitarray()
        bits2.extend(res)
        with open('text_decode.txt', 'wb') as fh:
            bits2.tofile(fh)
        print(bits2)

cyclic = CyclicCode()
cyclic.code_decode('D:\\PycharmProjects\\CT\\text.txt')


