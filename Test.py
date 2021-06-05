from collections import defaultdict
import random
import Maze
import Agent
import matplotlib.pyplot as plt
import matplotlib.patches as patches

cc=plt.cm.get_cmap("tab20").colors
diff=[(-1,0),(0,1),(1,0),(0,-1)]
Agent_num=1
Steps=50 #大きくするときはsave_mazeをしないこと！
maze=Maze.Maze(31,31,0.4)
maze.make_maze_arranged()
agents=[Agent.Agent(loc,maze,"b") for loc in random.sample(maze.route,Agent_num)]

for idx,agent in enumerate(agents): agent.cc=cc[idx]
agent_array=[[[] for i in range(maze.width)] for j in range(maze.height)]

def update_agentarray():
    for i in range(maze.height):
        for j in range(maze.width): agent_array[i][j]=[]
    for agent in agents:
        agent_array[agent.loc[0]][agent.loc[1]].append(agent)
        agent.decide=False

def dist(start):
    dic={}
    visited=set()
    queue=[(start,0)]
    while queue:
        tmp=queue.pop(0)
        visited.add(tmp[0])
        x,y=tmp[0]
        dic[tmp[0]]=tmp[1]
        for d in diff:
            tx,ty=x+d[0],y+d[1]
            if maze.maze[tx][ty] and ((tx,ty) not in visited): queue.append(((tx,ty),tmp[1]+1))
    return dic

def save_maze(directory,step):
    fig=plt.figure(figsize=(7,7))
    ax=plt.axes()
    for i in range(maze.height):
        for j in range(maze.width):
            if maze.maze[i][j]==0: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#000000"))
            elif maze.maze[i][j]==2: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#ffc0cb"))
    for agent in agents:
        d_x=agent.admin[1].loc[0]-agent.admin[0].loc[0]
        d_y=agent.admin[1].loc[1]-agent.admin[0].loc[1]
        ax.add_patch(patches.Rectangle(xy=(agent.admin[1].loc[0]-0.5,agent.admin[1].loc[1]-0.5),width=1,height=1,fc="#FFFFFF",ec=agent.cc))
        ax.add_patch(patches.Rectangle(xy=(agent.admin[0].loc[0]-0.5,agent.admin[0].loc[1]-0.5),width=1,height=1,fc=agent.cc))
        ax.add_patch(patches.Arrow(x=agent.admin[0].loc[0],y=agent.admin[0].loc[1],dx=d_x,dy=d_y,color=agent.cc))
        ax.add_patch(patches.Circle(xy=(agent.loc[0],agent.loc[1]),radius=0.5,fc=agent.cc))
    plt.axis("scaled")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig("./"+directory+"/step"+str(step)+".png")
    plt.close()

MHD=lambda x,y: abs(x[0]-y[0])+abs(x[1]-y[1])

class Cross_Agent:
    def __init__(self,loc):
        self.loc=loc
        self.adjacent=[0 for _ in range(4)] #隣にいる交差点エージェント
        self.ad_route=[0 for _ in range(4)] #管理する道(4つ)
        self.routes=set()
        self.routing_table=dict() #どこに行くエージェントをどの道に送ってやるかのテーブル
        self.agent_admin=[] #管理すべきエージェント

    def set_adjacent_route(self): #半島の場合はどうするか
        for idx,d in enumerate(diff):
            x,y=self.loc[0]+d[0],self.loc[1]+d[1]
            if maze.maze[x][y]:
                self.ad_route[idx]=[] #道がある方向
                visited={self.loc}
                while True:
                    visited.add((x,y))
                    if (x,y) in maze.crosses:
                        self.adjacent[idx]=cross_agents_dict[(x,y)]
                        break
                    else:
                        self.ad_route[idx].append((x,y))
                        flag=0
                        for c in diff:
                            tx,ty=(x+c[0],y+c[1])
                            if maze.maze[tx][ty] and ((tx,ty) not in visited): 
                                x,y=tx,ty
                                flag=1
                                break
                        if not flag: break #行き止まりがある時
        for route in self.ad_route:
            if not route: continue
            for r in route: self.routes.add(r)
    
    def set_routing_table(self):
        for goal in maze.generate:
            self.routing_table[goal]=None
            m=100000
            if goal in self.routes:
                for idx,route in enumerate(self.ad_route):
                    flag=0
                    if not route: continue
                    for r in route:
                        if r==goal:
                            flag=1
                            self.routing_table[goal]=self.adjacent[idx]
                            break
                    if flag: break
                continue
            for ca in self.adjacent:
                if not ca: continue
                if dist_table[goal][ca.loc]<m:
                    m=dist_table[goal][ca.loc]
                    self.routing_table[goal]=ca

    def set_admin_dict(self,admindict):
        for r in self.routes: admindict[r].append(self)

    def check(self):
        self.agent_admin=[]

    def plan(self): #各道の一方通行の方向を設定 -> 交差点上にいるエージェントの処理が最も重要？それぞれのエージェントが行く方向を決定(routing)->行先のエージェントと交渉したり、自身で経路探索や学習をするべき
        for agent in self.agent_admin:
            if agent.decide or self==agent.admin[0]: continue
            if agent.loc==self.loc: #目的交差点に到着した時
                agent.admin=(self,agent.nex_cross)
                if agent.task in self.routes: agent.nex_cross=None
                else: agent.nex_cross=agent.admin[1].routing_table[agent.task]
                for idx,ca in enumerate(self.adjacent):
                    if not ca: continue
                    if ca==agent.admin[1]: agent.nex=self.ad_route[idx][0]
            else:
                for adj in adjacent[agent.loc]:
                    if MHD(agent.admin[1].loc,adj)==MHD(agent.admin[1].loc,agent.loc)-1: agent.nex=adj
            agent.decide=True
            
cross_agents_dict={loc:Cross_Agent(loc) for loc in maze.crosses}
cross_agents=cross_agents_dict.values()

dist_table={goal:{} for goal in maze.generate}
for goal in maze.generate:
    tmp=dist(goal)
    dist_table[goal]=tmp

adjacent={locate:[(locate[0]+d[0],locate[1]+d[1]) for d in diff if maze.maze[locate[0]+d[0]][locate[1]+d[1]]] for locate in maze.route}

admin_dict=defaultdict(list)

for ca in cross_agents: ca.set_adjacent_route()
for ca in cross_agents:
    ca.set_routing_table()
    ca.set_admin_dict(admin_dict)
for key,val in admin_dict.items(): admin_dict[key]=tuple(val)

for step in range(Steps):
    if step%10==0: print(step)
    update_agentarray()
    for agent in agents: agent.update_next(adjacent,dist_table,cross_agents_dict,admin_dict)
    save_maze("pics",step)
    for ca in cross_agents: ca.check() #管理する道の状態を監視する
    for agent in agents: agent.check(cross_agents_dict) #管理される交差点エージェントを確認する
    for ca in cross_agents: ca.plan()
    for agent in agents: agent.move()