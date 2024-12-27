#pylint:disable=E1136
#pylint:disable=E0213
import typing
import time

DELAY:int = 0.05

class Gates:
    def OR(array:list[int]) -> int:
        return int(sum(array) > 0)
    
    def AND(array:list[int]) -> int:
        return int(sum(array) == len(array) and array[0] == 1)
    
    def NOT(array:list[int]) -> int:
        return int(not array[0])
        
    def BUFFER(array:list[int]) -> int:
        return array[0]
        
    def NAND(array:list[int]) -> int:
        return Gates.NOT(Gates.AND(array))
     
    def NOR(array:list[int]) -> int:
        return Gates.NOT(Gates.OR(array))
        
    def XOR(array:list[int]) -> int:
        return int(not sum(array)%2)
        
    def XNOR(array:list[int]) -> int:
        return Gates.NOT(Gates.XOR(array))

fxToName:dict = {
"AND":Gates.AND,
"OR":Gates.OR,
"NOT":Gates.NOT,
"BUFFER":Gates.BUFFER,
"XOR":Gates.XOR,
"NOR":Gates.NOR,
"NAND":Gates.NAND,
"XNOR":Gates.XNOR
}
#user:str = input("Enter: ")
user = "AND((1),(1),OR((0),(1)))"
def divide(string:str) -> list:
    witnessed:int = 0
    parts:str = []
    start:int = 0
    for i in range(len(string)):
        if string[i] == "(":
            witnessed+=1
        if string[i] == ")":
            witnessed-=1
            if witnessed==0:
                parts.append((start,i))
                start = i+2
    return [parts,[string[i[0]:i[1]+1] for i in parts]]

def divideInput(string:str) -> list:
    pairs:list = []
    previous:list = []
    for i in range(len(string)):
        if string[i] == "(":
            previous.append(i)
        if string[i] == ")":
            pairs.append((previous.pop(),i))
    return [string[pairs[-1][0]+1:pairs[-1][1]],pairs]
    
def solve(string: str) -> int:
    pairs:list = divideInput(string)
    fx:typing.Callable = fxToName[string[:pairs[1][-1][0]]]
    inputs:list = divide(pairs[0])
    realInputs:list = []
    for i in inputs[1]:
        if i == "(0)" or i == "(1)":
            realInputs.append(int(i[1]))
        else:
            realInputs.append(solve(i))
    return fx(realInputs)
    
print(solve(user))