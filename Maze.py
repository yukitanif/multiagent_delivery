import random
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches

diff=[(-1,0),(0,1),(1,0),(0,-1)]
delta=[(0,0),(0,1),(1,0),(1,1)]
MHD=lambda a,b: abs(a[0]-b[0])+abs(a[1]-b[1])

def check_cross(x,y,maze):
    cnt=0
    for d in diff: cnt+=bool(maze[x+d[0]][y+d[1]])
    return cnt

class Maze:
    def __init__(self,height,width,rate):
        self.height=height
        self.width=width
        self.route_length=height*width*rate
        self.maze=[[0 for i in range(width)] for j in range(height)]
        self.route=[] #通れるマス
        self.generate=[] #タスク生成マス
        self.crosses=set() #交差点マス

    def make_maze_arranged(self): #道路作成
        for i in range(1,self.height-1,4):
            for j in range(1,self.width-1): self.maze[i][j],self.maze[j][i]=1,1
        for i in range(1,self.height-1): self.maze[i][self.width-2]=1
        for i in range(1,self.width-1): self.maze[self.height-2][i]=1

        for i in range(1,self.height-1):
            for j in range(1,self.width-1):
                if self.maze[i][j]: self.route.append((i,j))
                if check_cross(i,j,self.maze)>=3: self.crosses.add((i,j))
        
        self.task_generate()
    
    def make_maze_random(self): #迷路作成
        x,y=self.height//2,self.width//2
        rand=[0,1,2,3]
        while len(self.route)<self.route_length:
            random.shuffle(rand)
            flag=0
            for d in rand:
                tx,ty=x+diff[d][0],y+diff[d][1]
                if 0<tx<self.height-1 and 0<ty<self.width-1 and self.maze[tx][ty]==0 and self.hantei(tx,ty):
                    x,y,flag=tx,ty,1
                    break
            if flag==0: x,y=random.choice(self.route)
            else:
                if self.maze[x][y]==0: self.route.append((x,y))
                self.maze[x][y]=1

        #交差点登録
        for i in range(self.height):
            for j in range(self.width):
                if self.maze[i][j]:
                    if check_cross(i,j,self.maze)>=3: self.crosses.add((i,j))
        
        self.task_generate()
    
    def task_generate(self): #タスク生成場所をランダムに決定
        tmp_route=copy.deepcopy(self.route)
        while tmp_route:
            tmp=random.choice(tmp_route)
            self.generate.append(tmp)
            self.maze[tmp[0]][tmp[1]]=2
            delete=[]
            for idx,r in enumerate(tmp_route):
                if MHD(r,tmp)<8: delete.append(idx)
            for i in delete[::-1]: del tmp_route[i]

    def hantei(self,tx,ty):
        for d in delta:
            sx,sy=tx-1+d[0],ty-1+d[1]
            tmp=0
            for c in delta: tmp+=self.maze[sx+c[0]][sy+c[1]]
            if tmp==3: return False
        return True

    def print_map(self):
        fig=plt.figure()
        ax=plt.axes()
        for i in range(self.height):
            for j in range(self.width):
                if self.maze[i][j]==0: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#000000"))
                elif self.maze[i][j]==2: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#ffc0cb"))
                else: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#FFFFFF"))
        plt.axis("scaled")
        ax.set_aspect("equal")
        ax.axis("off")
        plt.show()

    def print_map_adjacent(self):
        fig=plt.figure()
        ax=plt.axes()
        for i in range(self.height):
            for j in range(self.width):
                if self.maze[i][j]==0: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#000000"))
                else:
                    cnt=0
                    for d in diff: cnt+=bool(self.maze[i+d[0]][j+d[1]])
                    if cnt<=2: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#94c09e"))
                    else: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#ffd56a"))
        plt.axis("scaled")
        ax.set_aspect("equal")
        ax.axis("off")
        plt.show()

#maze=Maze(31,31,0.4)
#maze.make_maze_arranged()
#maze.task_generate()
#maze.print_map()