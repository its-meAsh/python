import random
import matplotlib.pyplot
from PIL import Image

class Maze:
    def __init__(self,size:tuple[int,int]) -> None:
        self.size:tuple[int,int] = size
        self.array:bytearray = [0b00000000 for _ in range(size[0]*size[1])]
        self.cache:dict[bytes:list[list[list[int]]]] = {}
        self.cache2:dict[bytes:list[list[list[int]]]] = {}
    
    def generate(self,seed:int = None) -> int:
        self.array[0] = 0b00000110
        self.array[-1] = 0b00010000
        count:int = 1
        currentPos:int = 0
        path:list[int] = []
        self.seed:int = random.randint(1,1000000) if seed == None else seed
        random.seed(self.seed)
        while count < self.size[0]*self.size[1]:
            adjacents:dict[int:int] = self.getDirectedAdjacents(currentPos)
            availableDirections:list[int] = []
            for dirn in adjacents:
                if not self.array[adjacents[dirn]] & 0b00000010:
                    availableDirections.append(dirn)
            if len(availableDirections) == 0:
                currentPos = path.pop()
                continue
            path.append(currentPos)
            nextDirn:int = random.choice(availableDirections)
            nextPos:int = adjacents[nextDirn]
            self.array[currentPos]=self.array[currentPos]|0b00000010|self.byteForDirection(nextDirn)
            self.array[nextPos]=self.array[nextPos]|0b00000010|self.byteForDirection((nextDirn-2)%4)
            currentPos = nextPos
            count+=1
        return self.seed
        
    def getCoord(self,index:int) -> tuple[int,int]:
        return (index//self.size[1],index%self.size[1])
        
    def getIndex(self,coord:tuple[int,int]) -> int:
        return self.size[1]*coord[0]+coord[1]
    
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
        
    def byteForDirection(self,dirn:int) -> bytes:
        if dirn == 0:
            return 0b00000100
        if dirn == 1:
            return 0b00001000
        if dirn == 2:
            return 0b00010000
        if dirn == 3:
            return 0b00100000
            
    def imageForByte(self,byte:bytes,pixel:int,bw:int,bg:list[int],border:list[int]) -> list[list[list[int]]]:
        if byte in self.cache:
            return self.cache[byte]
        image:list[list[list[int]]] = [[bg for j in range(pixel)] for i in range(pixel)]
        for i in range(bw):
            image[i] = [border for j in range(pixel)]
            image[pixel-i-1] = [border for j in range(pixel)]
        for i in range(bw,pixel-bw):
            image[i] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        
        if byte & 0b00000100:
            for i in range(bw):
                image[i] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        if byte & 0b00001000:
            for i in range(bw,pixel-bw):
                for j in range(pixel-bw,pixel):
                    image[i][j] = bg
        if byte & 0b00010000:
            for i in range(bw):
                image[pixel-i-1] = [border for j in range(bw)]+[bg for j in range(bw,pixel-bw)]+[border for j in range(bw)]
        if byte & 0b00100000:
            for i in range(bw,pixel-bw):
                for j in range(bw):
                    image[i][j] = bg
        self.cache[byte] = image
        return image

    def image(self,pixel:int,bw:int,bg:list[int],border:list[int]) -> None:
        image:list[list[list[int]]] = [[bg for j in range(self.size[1]*pixel)] for j in range(self.size[0]*pixel)]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                byte:bytes = self.array[self.getIndex((i,j))]
                byteImage:list[list[list[int]]] = self.imageForByte(byte,pixel,bw,bg,border)
                for p in range(pixel):
                    for q in range(pixel):
                        image[i*pixel+p][j*pixel+q] = byteImage[p][q]

        flat:list[tuple] = []
        for x in range(self.size[0]*pixel):
            for y in range(self.size[1]*pixel):
                flat.append(tuple(image[x][y]))
        imageObject = Image.new("RGB",(self.size[1]*pixel,self.size[0]*pixel))
        imageObject.putdata(flat)
        imageObject.save(f'maze{self.seed}.png')
        return f'maze{self.seed}.png'

    def solve(self) -> list[int]:
        currentPos:int = 0
        targetPos:int = self.size[0]*self.size[1]-1
        path:list[int] = []
        self.array[0] = self.array[0] ^ 0b00000100
        while currentPos != targetPos:
            adjacents:dict[int:int] = self.getDirectedAdjacents(currentPos)
            gatesAvailable:bytes = 0b00000000
            for dirn in adjacents:
                if self.byteForDirection(dirn) & self.array[currentPos]:
                    if not self.array[adjacents[dirn]] & 0b01000000:
                        gatesAvailable = gatesAvailable | self.byteForDirection(dirn)
            if not gatesAvailable:
                self.array[currentPos] = self.array[currentPos]|0b01000000
                currentPos = path.pop()
                continue
            self.array[currentPos] = self.array[currentPos]|0b01000000
            path.append(currentPos)
            nextDirn:int = 0
            if gatesAvailable & 0b00000100:
                nextDirn = 0
            elif gatesAvailable & 0b00001000:
                nextDirn = 1
            elif gatesAvailable & 0b00010000:
                nextDirn = 2
            elif gatesAvailable & 0b00100000:
                nextDirn = 3
            currentPos = adjacents[nextDirn]
        path.append(self.size[0]*self.size[1]-1)
        self.array[0] = self.array[0]|0b00000100
        for index in path:
            self.array[index] = self.array[index]|0b00000001
        return path

    
    def solutionImage(self,pixel:int,bw:int,bg:list[int],solBg:list[int],border:list[int]) -> str:
        pixelCenter:int = pixel//2
        image:list[list[list[int]]] = [[bg for j in range(self.size[1]*pixel)] for j in range(self.size[0]*pixel)]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                byte:bytes = self.array[self.getIndex((i,j))]
                byteImage:list[list[list[int]]] = self.imageForByte(byte,pixel,bw,bg,border)
                if byte & 0b00000001:
                    byteImage[pixelCenter][pixelCenter] = solBg
                    dirnByte:bytes = 0b00000000
                    adjacents:dict[int:int] = self.getDirectedAdjacents(self.getIndex((i,j)))
                    for dirn in adjacents:
                        if self.array[adjacents[dirn]]& 0b00000001 and byte & self.byteForDirection(dirn):
                            dirnByte = dirnByte|self.byteForDirection(dirn)
                    if (i,j) == (0,0):
                        dirnByte|=self.byteForDirection(0)
                    if (i,j) == (self.size[0]-1,self.size[1]-1):
                        dirnByte|=self.byteForDirection(2)
                    if dirnByte in self.cache2:
                        byteImage = self.cache2[dirnByte]
                    else:
                        if dirnByte & 0b00000100:
                            for X in range(pixelCenter):
                                byteImage[X][pixelCenter] = solBg
                        if dirnByte & 0b00001000:
                            for Y in range(pixelCenter,pixel):
                                byteImage[pixelCenter][Y] = solBg
                        if dirnByte & 0b00010000:
                            for X in range(pixelCenter,pixel):
                                byteImage[X][pixelCenter] = solBg
                        if dirnByte & 0b00100000:
                            for Y in range(pixelCenter):
                                byteImage[pixelCenter][Y] = solBg
                        self.cache2[dirnByte] = byteImage
                for p in range(pixel):
                    for q in range(pixel):
                        image[i*pixel+p][j*pixel+q] = byteImage[p][q]

        flat:list[tuple] = []
        for x in range(self.size[0]*pixel):
            for y in range(self.size[1]*pixel):
                flat.append(tuple(image[x][y]))
        imageObject = Image.new("RGB",(self.size[1]*pixel,self.size[0]*pixel))
        imageObject.putdata(flat)
        imageObject.save(f'mazeSol{self.seed}.png')
        return f'mazeSol{self.seed}.png'

myMaze:Maze = Maze((int(input("Height: ")),int(input("Width: "))))
print("Creating maze...")
seed:int = myMaze.generate()
print(f"Maze generated with seed: {seed}")
print("Creating image...")
fname:str = myMaze.image(11,1,[0,0,0],[48,210,197])
print(f"Image saved with name {fname} in the current directory")
print("Finding solution path...")
myMaze.solve()
print("Creating solution image...")
solfname:str = myMaze.solutionImage(11,1,[0,0,0],[255,255,255],[48,210,197])
print(f"Solution image saved with name {solfname} in the current directory")
