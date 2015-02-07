import VP_tree

class KNN:
    def __init__(self,dist,mapper,weight,k):
        #the list of all instances.
        self.L=[]
        #the list of instances not in the vp-tree.
        self.l=[]
        #the vp-tree.
        self.vpt=None
        self.d=dist
        self.k=k
        #The "kernel" takes an instance and a distance.
        self.mapper=mapper
        self.weight=weight

    def fit(self,x,y):
        if len(self.l)>3000:
            self.l.append((x,y))
            self.L.extend(self.l)
            self.vpt=VP_tree.VP_tree(self.L,lambda x1,x2:self.d(x1[0],x2[0]))
            self.l=[]
        else:
            self.l.append((x,y))

    def predict(self,x):
        kn=self.knearest(x)
        #simple averaging.
        return sum([self.weight(e[1])*self.mapper(e[0][1]) for e in kn if not e==(1,float("Inf"))])/max(sum([self.weight(e[0][1]) for e in kn if not e==(1,float("Inf"))]),1)

    def knearest(self,x):
        """Returns a list of format [((x,y),distance),..] of size k"""
        the_nearest=[]
        if not self.vpt==None:
            the_nearest.extend(self.find_knearest_in_vptree(x))
        if not self.l==[]:
            the_nearest.extend(self.find_knearest_in_buffer(x))
        return sorted(the_nearest,key=lambda e:e[1])[:self.k-1]

    def find_knearest_in_vptree(self,x):
        """Returns a list of format [((x,y),distance),..] of size k"""
        knvp=[]
        i=0
        for item in self.vpt.find([x,1]):
            if i<self.k:
                knvp.append(item)
            else:
                break
            i+=1
        return knvp

    def find_knearest_in_buffer(self,x):
        """Returns a list of format [((x,y),distance),..] of size k"""
        ds=[]
        maxdist=float("Inf")
        for i in range(0,len(self.l)):
            current_dist=self.d(self.l[i][0],x)
            if maxdist>=current_dist:
                maxdist=current_dist
                ds.append((self.l[i],current_dist))
                ds.sort(key=lambda e:e[1])
                ds.pop()
        return ds
        #ds=[(1,float("Inf"))]*self.k
        #for i in range(0,len(self.l)):
            #current_dist=self.dist(self.l[i][0],x)
            #if max([j[1] for j in ds])>=current_dist:
                #ds_index_biggest=max(range(len(ds)), key=lambda x:ds[x][1])
                #ds[ds_index_biggest]=(self.l[i],current_dist)
        #return ds
