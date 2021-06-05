from collections import defaultdict
import random
import Maze
import Agent
import matplotlib.pyplot as plt
import matplotlib.patches as patches

cc=plt.cm.get_cmap("tab20").colors
diff=[(-1,0),(0,1),(1,0),(0,-1)]
Agent_num=3
Steps=30
maze=Maze.Maze(31,31,0.4)
maze.make_maze_arranged()
agents=[Agent.Agent(loc,maze,color) for color,loc in zip(cc,random.sample(maze.route,Agent_num))]
dist_table={goal:{} for goal in maze.generate}

def dist():
    for goal in maze.generate:
        dic={}
        visited=set()
        queue=[(goal,0)]
        while queue:
            tmp=queue.pop(0)
            visited.add(tmp[0])
            x,y=tmp[0]
            dic[tmp[0]]=tmp[1]
            for d in diff:
                tx,ty=x+d[0],y+d[1]
                if maze.maze[tx][ty] and ((tx,ty) not in visited): queue.append(((tx,ty),tmp[1]+1))
        dist_table[goal]=dic

def save_maze(directory,step):
    fig=plt.figure(figsize=(7,7))
    ax=plt.axes()
    for i in range(maze.height):
        for j in range(maze.width):
            if maze.maze[i][j]==0: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#000000"))
            elif maze.maze[i][j]==2: ax.add_patch(patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc="#ffc0cb"))
    for agent in agents:
        d_x,d_y=agent.admin.loc[0]-agent.loc[0],agent.admin.loc[1]-agent.loc[1]
        ax.add_patch(patches.Rectangle(xy=(agent.admin.loc[0]-0.5,agent.admin.loc[1]-0.5),width=1,height=1,ec=agent.cc,fc="#FFFFFF"))
        ax.add_patch(patches.Arrow(x=agent.loc[0],y=agent.loc[1],dx=d_x,dy=d_y,color=agent.cc))
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
        self.ad_route=[] #管理する道(4つ)
        self.adjacent=[] #隣にいる交差点エージェント
        self.routing_table=dict() #どこに行くエージェントをどの道に送ってやるかのテーブル
        self.agent_admin=[] #管理すべきエージェント

    def initiate(self):
        #隣接エージェントと道を設定する
        for d in diff:
            x,y=self.loc[0]+d[0],self.loc[1]+d[1]
            if maze.maze[x][y]: #障害物の無い方向なら
                self.ad_route.append([])
                visited={self.loc}
                while True:
                    visited.add((x,y))
                    if (x,y) in maze.crosses:
                        self.adjacent.append(cross_agents_dict[(x,y)])
                        break
                    else:
                        self.ad_route[-1].append((x,y))
                        flag=0
                        for c in diff:
                            tx,ty=(x+c[0],y+c[1])
                            if maze.maze[tx][ty] and ((tx,ty) not in visited):
                                x,y,flag=tx,ty,1
                                break
                        if not flag: break #行き止まりがある時->袋小路
    
        #ルーティングテーブルの設定
        for goal in maze.generate:
            m=100000
            for ca,route in zip(self.adjacent,self.ad_route):
                if goal in route:
                    self.routing_table[goal]=ca
                    break
                elif dist_table[goal][ca.loc]<m:
                    m=dist_table[goal][ca.loc]
                    self.routing_table[goal]=ca

        #マス毎に担当する交差点エージェントを管理する辞書に自分自身を設定
        for route in self.ad_route:
            for r in route: admin_dict[r].append(self)

    def plan(self): #次に行きたい交差点を決める＋次ステップで行くマスを決めるとこ
        for agent in self.agent_admin[::-1]:
            if agent.decide: continue
            if agent.loc==self.loc: #目的交差点に到着した時
                self.agent_admin.remove(agent)
                agent.nex_cross.agent_admin.append(agent)
                agent.admin=agent.nex_cross
                if set(admin_dict[agent.task])=={self,agent.nex_cross}: agent.nex_cross=None #行こうとしている道にもうタスクがある
                else: agent.nex_cross=agent.admin.routing_table[agent.task]
                for idx,ca in enumerate(self.adjacent):
                    if ca==agent.admin: agent.nex=self.ad_route[idx][0]
            else:
                for adj in adjacent[agent.loc]:
                    if MHD(agent.admin.loc,adj)==MHD(agent.admin.loc,agent.loc)-1: agent.nex=adj #一時的目的地に最も近いマスへ行く
            agent.decide=True


cross_agents_dict={loc:Cross_Agent(loc) for loc in maze.crosses}
cross_agents=cross_agents_dict.values()
adjacent={locate:[(locate[0]+d[0],locate[1]+d[1]) for d in diff if maze.maze[locate[0]+d[0]][locate[1]+d[1]]] for locate in maze.route}
admin_dict=defaultdict(list)
dist()
for ca in cross_agents: ca.initiate()

for step in range(Steps):
    if step%10==0: print(step)
    for agent in agents: agent.update_next(adjacent,dist_table,cross_agents_dict,admin_dict)
    for ca in cross_agents: ca.plan()
    for agent in agents: agent.move()
    #save_maze("pics",step)