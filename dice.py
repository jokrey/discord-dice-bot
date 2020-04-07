import operator
import random
from functools import reduce


class Dice:

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.range = abs(min - (max+1))
        if min > max:
            raise ValueError('min('+str(min)+') > max('+str(max)+')')

    @classmethod
    def withMinMax(cls, min, max):
        return cls(min, max)

    @classmethod
    def withRange(cls, range):
        return cls(1, range)

    def __str__(self):
        if self.min == 1:
            return 'D'+str(self.range)
        else:
            return 'D['+str(self.min)+'..'+str(self.max)+']'

    def generate_result(self):
        return DiceConfiguration.fromVariable(self).generate_random_results()[0]


D2 = Dice.withRange(2)
D3 = Dice.withRange(3)
D4 = Dice.withRange(4)
D6 = Dice.withRange(6)
D8 = Dice.withRange(8)
D10 = Dice.withRange(10)
D12 = Dice.withRange(12)
D16 = Dice.withRange(16)
D20 = Dice.withRange(20)
D24 = Dice.withRange(24)
D30 = Dice.withRange(30)
D100 = Dice.withRange(100)


class DiceConfiguration:
    def __init__(self, dice_list: [Dice]):
        self.dice = dice_list
        if len(dice_list) == 0:
            raise ValueError('no dice in dice configuration')


    @classmethod
    def fromList(cls, dice_list):
        return cls(dice_list)

    @classmethod
    def fromVariable(cls, *dice):
        return cls(dice)

    def __getitem__(self, item):
        return self.dice[item]

    def __len__(self):
        return len(self.dice)

    def __str__(self):
        return ('{' if len(self)>1 else '')+(','.join(((str(ds[0]) if len(ds) == 1 else str(len(ds)) + 'x' + str(ds[0])) for ds in self.grouped())))+('}' if len(self)>1 else '')

    def generate_random_results(self):
        results_list = []
        for dice in self.dice:
            results_list.append(random.randrange(dice.min, dice.max+1,1))
        return DiceResults(self, results_list)

    def grouped(self):
        grouped = []
        sublist = []
        for i, d in enumerate(self.dice):
            if i > 0 and d != self.dice[i-1]:
                grouped.append(sublist)
                sublist=[]
            sublist.append(d)
        grouped.append(sublist)
        return grouped


class DiceResults:
    def __init__(self, config : DiceConfiguration, results: [int]):
        self.config = config
        self.results = results
        if len(config) != len(results):
            raise ValueError('len(config)('+str(len(config))+') != len(results)('+str(len(results))+')')

    def __getitem__(self, item):
        return self.results[item]

    def __len__(self):
        return len(self.config)

    def __str__(self):
        grouped = self.config.grouped()
        ri = 0
        builder = ''
        for i, ds in enumerate(grouped):
            if len(ds) == 1:
                builder += str(ds[0]) + '=' + str(self.results[ri])
                ri += 1
            else:
                builder += str(len(ds)) + 'x' + str(ds[0]) + '={'
                for di in range(len(ds)):
                    builder += str(self.results[ri])
                    ri += 1
                    if di + 1 != len(ds):
                        builder += ','
                    else:
                        builder += '}'
            if i + 1 != len(grouped):
                builder += ','
        return builder

    def sum(self):
        return sum(self.results)

    def prod(self):
        return reduce(operator.mul, self.results, 1)

    def add_each(self, number):
        return [x + number for x in self.results]

    def mul_each(self, number):
        return [x * number for x in self.results]

    def minus_each(self, number):
        return [x - number for x in self.results]


def helper_trunc_until_first_number(s: str):
    while len(s) > 0 and not (s[0].isdigit() or s[0] == '-'):
        s = s[1:]
    return s
def helper_extract_number_until_no_longer_possible(s: str):
    if len(s) == 0:
        return '', None
    numberBuilder = ''
    if s[0] == '-':
        numberBuilder = '-'
        s = s[1:]
    while len(s) > 0 and s[0].isdigit():
        numberBuilder += s[0]
        s = s[1:]
    return s, int(numberBuilder)

def extract_first_number(s: str):
    s = helper_trunc_until_first_number(s)
    s, number = helper_extract_number_until_no_longer_possible(s)
    return s, number

#possible syntax:
    #Single Dice
        #General: D<n> -> Dice.withRange(n)
        #General: D[<m>..<n>] -> Dice.withMinMax(m, n)
        #General: D[<m>.<n>] -> Dice.withMinMax(m, n)
        #General: D[<m>-<n>] -> Dice.withMinMax(m, n)
        #General: D<m>..<n> -> Dice.withMinMax(m, n)
        #General: D<m>.<n> -> Dice.withMinMax(m, n)
        #General: D<m>-<n> -> Dice.withMinMax(m, n)
        #Examples:
            # D10 -> Dice.withRange(10)
    #Multiple Dice

def extract_single_dice(part: str):
    part, number1 = extract_first_number(part)
    if len(part) > 0 and (part[0] == '+' or part[0] == '*'):
        number2 = None
    else:
        part, number2 = extract_first_number(part)

    if number2 is None:  # SINGLE RANGE DICE
        return part, Dice.withRange(number1)
    else:  # SINGLE MIN MAX DICE
        return part, Dice.withMinMax(number1, number2)

def extract_single_config(part: str):
    if part[0].isdigit():
        part, num = extract_first_number(part)
        part, dice = extract_single_dice(part)
        dice_list = [dice for _ in range(num)]
        return part, DiceConfiguration.fromList(dice_list)
    else:
        part, dice = extract_single_dice(part)
        return part, DiceConfiguration.fromVariable(dice)

def parse_part(results: [str], original: str):
    part = original
    if part.startswith('+'):
        part, config = extract_single_config(part[1::])
        raw_res = config.generate_random_results()
        results.append('+' + str(config) + '=' + str(raw_res.sum()))
    elif part.startswith('*'):
        part, config = extract_single_config(part[1::])
        raw_res = config.generate_random_results()
        results.append('*' + str(config) + '=' + str(raw_res.prod()))
    else:
        part, config = extract_single_config(part)
        if len(part) > 0 and part[0] == '+':
            part, number = extract_first_number(part[1::])
            raw_res = config.generate_random_results()
            results.append(str(config) + '+' + str(number) + '=' + str(raw_res.add_each(number)))
        elif len(part) > 0 and part[0] == '*':
            part, number = extract_first_number(part[1::])
            raw_res = config.generate_random_results()
            results.append(str(config) + '*' + str(number) + '=' + str(raw_res.mul_each(number)))
        elif len(part) > 0 and part[0] == '-':
            part, number = extract_first_number(part[1::])
            raw_res = config.generate_random_results()
            results.append(str(config) + '-' + str(number) + '=' + str(raw_res.minus_each(number)))
        else:
            results.append(str(config.generate_random_results()))

    return len(config.dice)

def parse_to_result_str(arg_str: str):
    parts = arg_str.split(',')
    if len(parts) == 1:
        parts = arg_str.split(' ')
    dice_list = []
    for part in parts:
        parse_part(dice_list, part.strip())
    return ', '.join(dice_list)