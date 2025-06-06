import os
import random
from PIL import Image
import copy
import cv2
import numpy

class Maze:
    emptyByte:bytes = 0b00000000
    usedByte:bytes = 0b00000010
    solByte:bytes = 0b00000001
    blockedByte:bytes = 0b01000000
    
    qImageFx:bytes = 0b00000001
    sImageFx:bytes = 0b00000010
    binFileFx:bytes = 0b00000100
    qFramesFx:bytes = 0b00001000
    sFramesFx:bytes = 0b00010000
    qVideoFx:bytes = 0b00100000
    sVideoFx:bytes = 0b01000000
    objFileFx:bytes = 0b10000000
    
    def __init__(self,size:tuple[int,int],seed:int,name:str,dirname:str,qImage:bool,sImage:bool,binFile:bool,qFrames:bool,sFrames:bool,qVideo:bool,sVideo:bool,objFile:bool,ppt:int,bw:int,border:list[int],bg:list[int],solBg:list[int],fps:int,codec:str,extension:str) -> None:
        self.size:tuple[int,int] = size
        self.seed:int = seed if seed else random.randint(1,1000000)
        random.seed(self.seed)
        self.name:str = name if name else f'maze{self.seed}'
        self.dirname:str = dirname if dirname else f'maze{self.seed}'
        
        self.functionalities:bytes = 0b00000000
        if qImage: self.functionalities|=self.qImageFx
        if sImage: self.functionalities|=self.sImageFx
        if binFile: self.functionalities|=self.binFileFx
        if qFrames: self.functionalities|=self.qFramesFx
        if sFrames: self.functionalities|=self.sFramesFx
        if qVideo: self.functionalities|=self.qVideoFx
        if sVideo: self.functionalities|=self.sVideoFx
        if objFile: self.functionalities|=self.objFileFx
        
        self.ppt:int = ppt
        self.bw:int = bw
        self.border:list[int] = border
        self.bg:list[int] = bg
        self.solbg:list[int] = solBg
        self.fps:int = fps
        self.codec:str = codec
        self.extension:str = extension
        
        self.array:bytearray = bytearray([self.emptyByte for _ in range(self.size[0]*self.size[1])])
        try:
            os.mkdir(self.dirname)
        except:
            None
        
        self.qFrames:list[list[list[list[int]]]] = self.generate()
        if self.functionalities&self.qFramesFx:
            os.mkdir(f'{self.dirname}/qFrames')
            for i in range(len(self.qFrames)):
                self.saveImage(f'{self.dirname}/qFrames',f'{self.name}qFrames{i}',self.qFrames[i])
        if self.functionalities&self.qImageFx:
            self.saveImage(f'{self.dirname}',f'{self.name}QImage',self.qFrames[-1] if self.functionalities&self.qFramesFx else self.mazeCurrentImage())
        
        self.solPath:list[int] = []
        self.sFrames:list[list[list[list[int]]]] = self.solve()
        if self.functionalities&self.sFramesFx:
            os.mkdir(f'{self.dirname}/sFrames')
            for i in range(len(self.sFrames)):
                self.saveImage(f'{self.dirname}/sFrames',f'{self.name}sFrames{i}',self.sFrames[i])
        if self.functionalities&self.sImageFx:
            self.saveImage(f'{self.dirname}',f'{self.name}SImage',self.sFrames[-1] if self.functionalities&self.sFramesFx else self.mazeCurrentImage())
            
        if self.functionalities&self.binFileFx:
            self.binarySave()

        if self.functionalities&self.qVideoFx:
            self.saveVideo(f'{self.dirname}',f'{self.name}qVideo',self.qFrames,self.fps)
        
        if self.functionalities&self.sVideoFx:
            self.saveVideo(f'{self.dirname}',f'{self.name}sVideo',self.sFrames,self.fps)
            
        if self.functionalities&self.objFileFx:
            self.saveObj(f'{self.dirname}',f'{self.name}object')
        return
    
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
    
    def imageForByte(self,byte:bytes,index:int = 0,solByteCheck:bool = False) -> list[list[list[int]]]:
        image:list[list[list[int]]] = [[self.bg for j in range(self.ppt)] for i in range(self.ppt)]
        pixelCenter:int = self.ppt//2
        if not byte & self.usedByte:
            return image
        for i in range(self.bw):
            image[i] = [self.border for j in range(self.ppt)]
            image[self.ppt-i-1] = [self.border for j in range(self.ppt)]
        for i in range(self.bw,self.ppt-self.bw):
            image[i] = [self.border for j in range(self.bw)]+[self.bg for j in range(self.bw,self.ppt-self.bw)]+[self.border for j in range(self.bw)]
        
        if byte & self.byteForDirection(0):
            for i in range(self.bw):
                image[i] = [self.border for j in range(self.bw)]+[self.bg for j in range(self.bw,self.ppt-self.bw)]+[self.border for j in range(self.bw)]
        if byte & self.byteForDirection(1):
            for i in range(self.bw,self.ppt-self.bw):
                for j in range(self.ppt-self.bw,self.ppt):
                    image[i][j] = self.bg
        if byte & self.byteForDirection(2):
            for i in range(self.bw):
                image[self.ppt-i-1] = [self.border for j in range(self.bw)]+[self.bg for j in range(self.bw,self.ppt-self.bw)]+[self.border for j in range(self.bw)]
        if byte & self.byteForDirection(3):
            for i in range(self.bw,self.ppt-self.bw):
                for j in range(self.bw):
                    image[i][j] = self.bg
                    
        if byte & self.solByte and solByteCheck:
            image[pixelCenter][pixelCenter] = self.solbg
            dirnByte:bytes = self.emptyByte
            
            adjacents:dict[int:int] = self.getDirectedAdjacents(index)
            for dirn in adjacents:
                if adjacents[dirn] in self.solPath and byte&self.byteForDirection(dirn):
                    dirnByte|=self.byteForDirection(dirn)
                    
            if index == 0:
                dirnByte|=self.byteForDirection(0)
            if index == len(self.array)-1:
                dirnByte|=self.byteForDirection(2)
            if dirnByte & self.byteForDirection(0):
                for X in range(pixelCenter):
                    image[X][pixelCenter] = self.solbg
            if dirnByte & self.byteForDirection(1):
                for Y in range(pixelCenter,self.ppt):
                    image[pixelCenter][Y] = self.solbg
            if dirnByte & self.byteForDirection(2):
                for X in range(pixelCenter,self.ppt):
                    image[X][pixelCenter] = self.solbg
            if dirnByte & self.byteForDirection(3):
                for Y in range(pixelCenter):
                    image[pixelCenter][Y] = self.solbg
        return image

    def generate(self) -> list[list[list[list[int]]]]:
        frames:list[list[list[list[int]]]] = [self.mazeCurrentImage()]
        count:int = 1
        currentPos:int = 0
        path:list[int] = []
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
            if self.functionalities&(self.qFramesFx|self.qVideoFx):
                prevImage:list[list[list[int]]] = copy.deepcopy(frames[-1])
                self.changePosImage(prevImage,[path[-1],currentPos])
                frames.append(prevImage)
        return frames
    
    def solve(self) -> list[list[list[list[int]]]]:
        currentPos:int = 0
        targetPos:int = self.size[0]*self.size[1]-1
        path:list[int] = []
        frames:list[list[list[list[int]]]] = [self.mazeCurrentImage(True)]
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
        self.solPath = path
        for index in path:
            self.array[index]|=self.solByte
            if self.functionalities&(self.sFramesFx|self.sVideoFx):
                prevImage:list[list[list[int]]] = copy.deepcopy(frames[-1])
                self.changePosImage(prevImage,self.solPath,True)
                frames.append(prevImage)
        return frames
    
    def mazeCurrentImage(self,solByteCheck:bool = False) -> list[list[list[int]]]:
        image:list[list[list[int]]] = [[self.bg for j in range(self.size[1]*self.ppt)] for i in range(self.size[0]*self.ppt)]
        self.array[0]|=self.byteForDirection(0)
        self.array[-1]|=self.byteForDirection(2)
        self.changePosImage(image,range(len(self.array)),solByteCheck)
        return image
    
    def changePosImage(self,image:list[list[list[int]]],indices:list[int],solByteCheck:bool = False) -> None:
        for index in indices:
            byte:bytes = self.array[index]
            byteImage:list[list[list[int]]] = self.imageForByte(byte,index,solByteCheck)
            i,j = self.getCoord(index)
            for p in range(self.ppt):
                for q in range(self.ppt):
                    image[i*self.ppt+p][j*self.ppt+q] = byteImage[p][q]
        return
    
    def saveImage(self,path:str,name:str,image:list[list[list[int]]]) -> None:
        flat:list[tuple] = []
        for x in range(len(image)):
            for y in range(len(image[0])):
                flat.append(tuple(image[x][y]))
        imageObject = Image.new("RGB",(len(image[0]),len(image)))
        imageObject.putdata(flat)
        imageObject.save(f'{path}/{name}.png')
        return
    
    def binarySave(self) -> None:
        fname:str = f'{self.dirname}/{self.name}binFile.bin'
        file = open(fname,"wb")
        file.write(self.array)
        file.close()
        return


    def saveVideo(self,path:str,name:str,images:list[list[list[list[int]]]],fps:int) -> None:
        videoWriter = cv2.VideoWriter(f'{path}/{name}.{self.extension}',cv2.VideoWriter_fourcc(*f'{self.codec}'),fps,(self.size[1]*self.ppt,self.size[0]*self.ppt))
        for image in images:
            videoWriter.write(cv2.cvtColor(numpy.array(image,dtype=numpy.uint8),cv2.COLOR_RGB2BGR))
        videoWriter.release()
        return
        
    def saveObj(self,path:str,name:str) -> None:
        vertices:list[list[float]] = []
        faces:list[list[int]] = []
        offset:int = 0
        vText:str = ""
        fText:str = ""
        currentImage:list[list[list[int]]] = self.mazeCurrentImage()
        for i in range(self.size[0]*self.ppt):
            for j in range(self.size[1]*self.ppt):
                for k in range(self.ppt):
                    if currentImage[i][j] == self.border or k<self.bw:
                        vText+=f'v {i} {j} {k}\nv {i+1} {j} {k}\nv {i+1} {j+1} {k}\nv {i} {j+1} {k}\nv {i} {j} {k+1}\nv {i+1} {j} {k+1}\nv {i+1} {j+1} {k+1}\nv {i} {j+1} {k+1}\n'
                        fText+=f'f {1+offset} {2+offset} {4+offset}\nf {2+offset} {3+offset} {4+offset}\nf {1+offset} {4+offset} {8+offset}\nf {1+offset} {5+offset} {8+offset}\nf {1+offset} {2+offset} {6+offset}\nf {1+offset} {5+offset} {6+offset}\nf {7+offset} {8+offset} {4+offset}\nf {7+offset} {3+offset} {4+offset}\nf {7+offset} {3+offset} {2+offset}\nf {7+offset} {6+offset} {2+offset}\nf {7+offset} {8+offset} {5+offset}\nf {7+offset} {6+offset} {5+offset}\n'
                        offset+=8
        objFile = open(f'{path}/{name}.obj','x')
        objFile.write(vText+fText)
        objFile.close()
        return
        
    def __call__(self) -> None:
        print(f'Maze:\n Seed: {self.seed}\n Height: {self.size[0]}, Width: {self.size[1]}\n Name: {self.name}\n Directory name: {self.dirname}\n Functionalities:\n  Question image: {bool(self.functionalities&self.qImageFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}QImage.png") if self.functionalities&self.qImageFx else 0} bytes\n  Solution image: {bool(self.functionalities&self.sImageFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}SImage.png") if self.functionalities&self.sImageFx else 0} bytes\n  Binary file save: {bool(self.functionalities&self.binFileFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}binFile.bin") if self.functionalities&self.binFileFx else 0} bytes\n  Question frames: {bool(self.functionalities&self.qFramesFx)} --- Size: {os.path.getsize(f"{self.dirname}/qFrames") if self.functionalities&self.qFramesFx else 0} bytes\n  Solution frames: {bool(self.functionalities&self.sFramesFx)} --- Size: {os.path.getsize(f"{self.dirname}/sFrames") if self.functionalities&self.sFramesFx else 0} bytes\n  Question video: {bool(self.functionalities&self.qVideoFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}qVideo.{self.extension}") if self.functionalities&self.qVideoFx else 0} bytes\n  Solution video: {bool(self.functionalities&self.sVideoFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}sVideo.{self.extension}") if self.functionalities&self.sVideoFx else 0} bytes\n  3D Model: {bool(self.functionalities&self.objFileFx)} --- Size: {os.path.getsize(f"{self.dirname}/{self.name}object.obj") if self.functionalities&self.objFileFx else 0} bytes')

height:int = int(input("Height: "))
width:int = int(input("Width: "))
seed:int = int(input("Seed (0 for random): "))
print("For below questions, leave empty for default values")
mazeName:str = input("Maze name: ")
dirName:str = input("Directory name: ")
print("For below questions, press enter key for NO, and type anything and enter for YES")
qImage:bool = bool(input("Question image save: "))
sImage:bool = bool(input("Solution image save: "))
bFile:bool = bool(input("Binary file save: "))
qFrames:bool = bool(input("Question frames save: "))
sFrames:bool = bool(input("Solution frames save: "))
qVideo:bool = bool(input("Question video save: "))
sVideo:bool = bool(input("Solution video save: "))
objFile:bool = bool(input("3D model: "))
ppt:int = 0
bw:int = 0
fps:int = 0
codec:str = ""
extension:str = ""
if qImage or sImage or qFrames or sFrames or qVideo or sVideo or objFile:
    print("For below question, enter an integer")
    ppt = int(input("Pixels per tile: "))
    bw = int(input("Border width: "))
if qVideo or sVideo:
    print("For below question, enter an integer or float")
    fps = float(input("Frames per second: "))
    print("NOTE: Codec, extension and its compatibility with the codec is not checked by the program, do your research on your own. Video made using cv2 module")
    codec = input("Codec: ")
    extension = input("Extension: ")
print("Generating your maze...")
myMaze:Maze = Maze((height,width),seed,mazeName,dirName,qImage,sImage,bFile,qFrames,sFrames,qVideo,sVideo,objFile,ppt,bw,[48,210,197],[0,0,0],[255,255,255],fps,codec,extension)
print("Maze generated")
myMaze()
