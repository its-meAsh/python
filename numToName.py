basics: dict[int,str] = {
0:"Zero",
1:"One",
2:"Two",
3:"Three",
4:"Four",
5:"Five",
6:"Six",
7:"Seven",
8:"Eight",
9:"Nine",
10:"Ten",
11:"Eleven",
12:"Twelve",
13:"Thirteen",
14:"Fourteen",
15:"Fifteen",
16:"Sixteen",
17:"Seventeen",
18:"Eighteen",
19:"Nineteen",
20:"Twenty",
30:"Thirty",
40:"Fourty",
50:"Fifty",
60:"Sixty",
70:"Seventy",
80:"Eighty",
90:"Ninety"
}

powers: dict[int,str] = {
    2: "Hundred",
    3: "Thousand",
    6: "Million",
    9: "Billion",
    12: "Trillion",
    15: "Quadrillion",
    18: "Quintillion",
    21: "Sextillion",
    24: "Septillion",
    27: "Octillion",
    30: "Nonillion",
    33: "Decillion",
    36: "Undecillion",
    39: "Duodecillion",
    42: "Tredecillion",
    45: "Quattuordecillion",
    48: "Quindecillion",
    51: "Sexdecillion",
    54: "Septendecillion",
    57: "Octodecillion",
    60: "Novemdecillion",
    63: "Vigintillion"
}

powersList:list[int] = list(powers.keys())
powersList.reverse()
def join(array:list)->str:
    text = []
    for i in array:
        if isinstance(i,list):
            text+=join(i)
        else:
            text+=[i]
    return text

def convert(num:int)->str:
    if num in list(basics.keys()):
        return [basics[num]]
    elif 0<=num<100:
        text = []
        text.append(convert((num//10)*10))
        if num%10!=0:
            text.append(convert(num%10))
        return text
    text = []
    for power in powersList:
        if num//10**power != 0:
            text+=[convert(num//10**power),powers[power]]
            num = num%(10**power)
            if (power == 2 and num!=0):
                text+=convert(num)
    return join(text)
            
conv: list[str] = convert(161645788116733852821916737385588291643735655581916735659591613438558194676)
text: str = ""
for i in conv:
    text+=i+" "
print(text)