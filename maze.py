import random
from PIL import Image
import os

class Maze:
    emptyByte:bytes = 0b00000000
    usedByte:bytes = 0b00000010
    solByte:bytes = 0b00000001
    blockedByte:bytes = 0b01000000

    def __init__(self,size:tuple[int,int],seed:int = None) -> None:
        self.size:tuple[int,int] = size
        self.seed:int = random.randint(1,10000000) if seed == None else seed
        self.array:bytearray = bytearray([self.emptyByte for _ in range(self.size[0]*self.size[1])])
        self.dirname:str = f'maze{self.seed}'
        self.qImage:list[list[list[int]]] = []
        self.sImage:list[list[list[int]]] = []
        try:
            os.mkdir(self.dirname)
        except:
            None
    
    def getCoord(self,index:int) -> tuple[int,int]:
        return (index//self.size[1],index%self.size[1])
        
    def getIndex(self,coord:tuple[int,int]) -> int:
        return self.size[1]*coord[0]+coord[1]

    def byteForDirection(self,dirn:int) -> bytes:
        if dirn == 0:
            return 0b00000100
        if dirn == 1:
            return 0b00001000
        if dirn == 2:
            return 0b00010000
        if dirn == 3:
            return 0b00100000
        
    def getDirectedAdjacents(self,index:int) -> dict[int:int]:
        adjacents:dict[int:int] = {}
        x,y = self.getCoord(index)
        X,Y = self.size
        if x-1>=0:
            adjacents[0] = self.getIndex((x-1,y))
        if y+1<Y:
            adjacents[1] = self.getIndex((x,y+1))
        if x+1<X:
            adjacents[2] = self.getIndex((x+1,y))
        if y-1>=0:
            adjacents[3] = self.getIndex((x,y-1))
        return adjacents

    def generate(self) -> int:
        count:int = 1
        currentPos:int = 0
        path:list[int] = []
        random.seed(self.seed)
        while count < self.size[0]*self.size[1]:
            adjacents:dict[int:int] = self.getDirectedAdjacents(currentPos)
            availableDirections:list[int] = []
            for dirn in adjacents:
                if not self.array[adjacents[dirn]] & self.usedByte:
                    availableDirections.append(dirn)
            if len(availableDirections) == 0:
                currentPos = path.pop()
                continue
            path.append(currentPos)
            nextDirn:int = random.choice(availableDirections)
            nextPos:int = adjacents[nextDirn]
            self.array[currentPos]|=(self.usedByte|self.byteForDirection(nextDirn))
            self.array[nextPos]|=(self.usedByte|self.byteForDirection((nextDirn-2)%4))
            currentPos = nextPos
            count+=1
        return self.seed

    def imageForByte(self,byte:bytes,pixel:int,bw:int,bg:list[int],border:list[int]) -> list[list[list[int]]]:
        image:list[list[list[int]]] = [[bg for j in range(pixel)] for i in range(pixel)]
        for i in range(bw):
            image[i] = [border for j in range(pixel)]
            image[pixel-i-1] = [border for j in range(pixel)]
        for i in range(bw,pixel-bw):
            image[i] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        
        if byte & self.byteForDirection(0):
            for i in range(bw):
                image[i] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        if byte & self.byteForDirection(1):
            for i in range(bw,pixel-bw):
                for j in range(pixel-bw,pixel):
                    image[i][j] = bg
        if byte & self.byteForDirection(2):
            for i in range(bw):
                image[pixel-i-1] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        if byte & self.byteForDirection(3):
            for i in range(bw,pixel-bw):
                for j in range(bw):
                    image[i][j] = bg
        return image

    def image(self,pixel:int,bw:int,bg:list[int],border:list[int]) -> tuple[str,int]:
        self.array[0]|=self.byteForDirection(0)
        self.array[-1]|=self.byteForDirection(2)
        image:list[list[list[int]]] = [[bg for j in range(self.size[1]*pixel)] for j in range(self.size[0]*pixel)]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                byte:bytes = self.array[self.getIndex((i,j))]
                byteImage:list[list[list[int]]] = self.imageForByte(byte,pixel,bw,bg,border)
                for p in range(pixel):
                    for q in range(pixel):
                        image[i*pixel+p][j*pixel+q] = byteImage[p][q]
        self.qImage = image
        flat:list[tuple] = []
        for x in range(self.size[0]*pixel):
            for y in range(self.size[1]*pixel):
                flat.append(tuple(image[x][y]))
        imageObject = Image.new("RGB",(self.size[1]*pixel,self.size[0]*pixel))
        imageObject.putdata(flat)
        imageObject.save(f'{self.dirname}/maze{self.seed}.png')
        self.array[0]^=self.byteForDirection(0)
        self.array[-1]^=self.byteForDirection(2)
        return (f'maze{self.seed}.png',os.path.getsize(f'{self.dirname}/maze{self.seed}.png'))
    
    def solve(self) -> list[int]:
        currentPos:int = 0
        targetPos:int = self.size[0]*self.size[1]-1
        path:list[int] = []
        while currentPos != targetPos:
            adjacents:dict[int:int] = self.getDirectedAdjacents(currentPos)
            gatesAvailable:bytes = self.emptyByte
            for dirn in adjacents:
                if self.byteForDirection(dirn) & self.array[currentPos]:
                    if not self.array[adjacents[dirn]] & self.blockedByte:
                        gatesAvailable = gatesAvailable | self.byteForDirection(dirn)
            if not gatesAvailable:
                self.array[currentPos]|=self.blockedByte
                currentPos = path.pop()
                continue
            self.array[currentPos]|=self.blockedByte
            path.append(currentPos)
            nextDirn:int = 0
            for i in range(4):
                if gatesAvailable & self.byteForDirection(i):
                    nextDirn = i
                    break
            currentPos = adjacents[nextDirn]
        path.append(self.size[0]*self.size[1]-1)
        for index in path:
            self.array[index]|=self.solByte
        return path
    
    def solImage(self,pixel:int,bw:int,bg:list[int],solBg:list[int],border:list[int]) -> tuple[str,int]:
        self.array[0]|=self.byteForDirection(0)
        self.array[-1]|=self.byteForDirection(2)
        pixelCenter:int = pixel//2
        if len(self.qImage) != 0:
            image:list[list[list[int]]] = self.qImage
        else:
            image:list[list[list[int]]] =  [[bg for j in range(self.size[1])] for i in range(self.size[0])]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                byte:bytes = self.array[self.getIndex((i,j))]
                byteImage:list[list[list[int]]] = self.imageForByte(byte,pixel,bw,bg,border)
                if byte&self.solByte:
                    byteImage[pixelCenter][pixelCenter] = solBg
                    dirnByte:bytes = self.emptyByte
                    if self.getIndex((i,j)) == 0:
                        dirnByte|=self.byteForDirection(0)
                    if self.getIndex((i,j)) == len(self.array)-1:
                        dirnByte|=self.byteForDirection(2)
                    adjacents:dict[int,int] = self.getDirectedAdjacents(self.getIndex((i,j)))
                    for dirn in adjacents:
                        if byte&self.byteForDirection(dirn) and self.array[adjacents[dirn]]&self.solByte:
                            dirnByte|=self.byteForDirection(dirn)
                    if dirnByte & self.byteForDirection(0):
                        for X in range(pixelCenter):
                            byteImage[X][pixelCenter] = solBg
                    if dirnByte & self.byteForDirection(1):
                        for Y in range(pixelCenter,pixel):
                            byteImage[pixelCenter][Y] = solBg
                    if dirnByte & self.byteForDirection(2):
                        for X in range(pixelCenter,pixel):
                            byteImage[X][pixelCenter] = solBg
                    if dirnByte & self.byteForDirection(3):
                        for Y in range(pixelCenter):
                            byteImage[pixelCenter][Y] = solBg
                for p in range(pixel):
                    for q in range(pixel):
                        image[i*pixel+p][j*pixel+q] = byteImage[p][q]
        self.array[0]^=self.byteForDirection(0)
        self.array[-1]^=self.byteForDirection(2)
        flat:list[tuple] = []
        for x in range(self.size[0]*pixel):
            for y in range(self.size[1]*pixel):
                flat.append(tuple(image[x][y]))
        imageObject = Image.new("RGB",(self.size[1]*pixel,self.size[0]*pixel))
        imageObject.putdata(flat)
        imageObject.save(f'{self.dirname}/mazeSol{self.seed}.png')
        return (f'mazeSol{self.seed}.png',os.path.getsize(f'{self.dirname}/mazeSol{self.seed}.png'))
    
    def binarySave(self) -> tuple[str,str,int]:
        fname:str = f'{self.dirname}/mazeBin{self.seed}.bin'
        file = open(fname,"wb")
        file.write(self.array)
        file.close()
        return [f'mazeBin{self.seed}.png',os.path.getsize(fname)]
    
myMaze:Maze = Maze((int(input("Height: ")),int(input("Width: "))),7811956)
print("Creating maze...")
seed:int = myMaze.generate()
print(f"Maze generated with seed: {seed}")
[binfname,binSize] = myMaze.binarySave()
print(f"Binary file saved with name {binfname} in {myMaze.dirname} directory of size {binSize} bytes")
print("Creating image...")
imgName,imgSize = myMaze.image(11,1,[0,0,0],[48,210,197])
print(f"Image saved with name {imgName} in {myMaze.dirname} directory of size {imgSize} bytes")
print("Finding solution path...")
myMaze.solve()
print("Creating solution image...")
solfname,solSize = myMaze.solImage(11,1,[0,0,0],[255,255,255],[48,210,197])
print(f"Solution image saved with name {solfname} in the {myMaze.dirname} directory of size {solSize} bytes")