import random

diff=[(-1,0),(0,1),(1,0),(0,-1)]

class Agent:
    def __init__(self,loc,maze,cc):
        self.loc=loc
        self.task=loc
        self.maze=maze
        self.admin=None #from,to
        self.nex=None
        self.nex_cross=None #次に担当する交差点エージェント
        self.decide=False
        self.cc=cc

    def select_task(self):
        prior_task=self.task
        while self.task==prior_task: self.task=random.choice(self.maze.generate)

    def update_next(self,adjacent,dist_table,ca_dict,admin_dic):
        self.decide=False
        if self.loc==self.task:
            if self.admin: self.admin.agent_admin.remove(self)
            self.select_task()
            self.set_admin(dist_table,ca_dict,admin_dic)

    def set_admin(self,dist_table,ca_dict,admin_dic):
        if self.loc in self.maze.crosses:
            m=10000
            for ca in ca_dict[self.loc].adjacent:
                if dist_table[self.task][ca.loc]<m:
                    m=dist_table[self.task][ca.loc]
                    self.admin=ca
        else: #同一道路上のタスクを選択してしまった時はまた別で考える必要がある。
            tmp=admin_dic[self.loc]
            if len(tmp)!=2: print("aaaaaaaaaaa") #袋小路や半島がある時に発生
            if dist_table[self.task][tmp[0].loc]<dist_table[self.task][tmp[1].loc]: self.admin=tmp[0]
            else: self.admin=tmp[1]
        self.admin.agent_admin.append(self)
        self.nex_cross=self.admin.routing_table[self.task]

    def move(self):
        self.loc=self.nex
