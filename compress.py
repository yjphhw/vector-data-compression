#--coding--:utf-8 
import numpy as np
import time
def makeline(x,y,PN=100):
    #pl=[QgsGeometry.fromPointXY(QgsPointXY(x[i],y[i])) for i in range(PN)]
    pl=QgsGeometry.fromPolyline([(QgsPoint(x[i],y[i])) for i in range(PN)])
    #pl=QgsLineString([(QgsPoint(x[i],y[i])) for i in range(PN)])
    #pl.nCoordinates() # number of vertex
    print('orgin length is',pl.length()) #calclength
    #pl.deleteVertex(0) # delete a vertex at pos 0
    return pl
def showline(line,name='line'):
    feat=QgsFeature()
    feat.setGeometry(line)
    vl = QgsVectorLayer("LineString?crs=epsg:4326", name, "memory")
    dp=vl.dataProvider()
    dp.addFeatures([feat])
    if vl.isValid():
        vl.updateExtents()
        QgsProject.instance().addMapLayer(vl)
def test(PN=50,dagelas_thresh=1):
    samelines=easyline(linenum=5,PN=PN)
    
    #show orgin line
    showline(samelines[0],'orgin')
    
    #daogelas method
    dt=time.time()
    daogelas_line,leftpoints=daogelas_method(samelines[2],dagelas_thresh)
    print('daogelas time is ',time.time()-dt)
    showline(daogelas_line,'daogelas_method')
    
    deletenum=PN-leftpoints
    
    
    
    #show interval delete
    interval=max(2,int(PN/deletenum)) if deletenum else 2
    dt=time.time()
    modpline=modp_method(samelines[1],interval)
    print('mdpmethod time is',time.time()-dt)
    showline(modpline,'modp_method')
    
    
    dt=time.time()
    lengthmin_line=lengthmin2_method(samelines[3],deletenum)
    print('lengthmin time is ',time.time()-dt)
    showline(lengthmin_line,'lengthmin_method')
def easyline(linenum=5,PN=10):
    y=np.random.random(PN)*9-5
    x=np.array(range(PN))+np.random.random(PN)
    res=[]
    for i in range(linenum):
        res.append(makeline(x,y,PN))
    return res
def modp_method(line,p=2):
    '''
    from p=0 to PN ,interval p vertex,delete one vertex  
    '''
    cl=line.constGet()
    length=line.length()
    num=cl.numPoints()
    #print(type(line),num)
    if num<=p: 
        print('p is bigger than number of points in line')
        return line
    for k in range(num-p,0,-p):
        line.deleteVertex(k)
    #print('after modp p=',p,'line length is,',line.length(),'has points:',line.constGet().numPoints())
    print('{} points left after daogelas method, length/orginlength:{}'.format(cl.numPoints(),line.length()/length) )
    return line
def daogelas_method(line,threshold=2):
    length=line.length()
    cl=line.constGet()
    pnum=cl.numPoints()
    idx=[0]*pnum
    idx[0]=1
    idx[-1]=1
    st=0
    ed=pnum-1
    def r(idx,cl,st,ed,threshold=2):
        '''
            idx is the map, at position p is 1 indiacate point should preserve
            cl is line string object
            st is startpoint index to search
            ed is endpoint index to search
        '''
        if 1==ed-st: return 0
        stp=cl.pointN(st)
        edp=cl.pointN(ed)
        vy=stp.x()-edp.x()   #calc the perpendicular vector of sttoed 
        vx=edp.y()-stp.y()
        l=(vx**2+vy**2)**0.5
        vy/=l
        vx/=l
        cur=st+1
        maxd=0
        maxp=0
        while cur<ed:
            curp=cl.pointN(cur)
            d=abs((curp.x()-stp.x())*vx+(curp.y()-stp.y())*vy) #calc the projection on perpendicular 
            #print(st,ed,cur,d)
            if d>maxd:
                maxd=d
                maxp=cur
            cur+=1
        if maxd>threshold:
            idx[maxp]=1
            #print('maxd is',maxd,' maxpid is',maxp)
            r(idx,cl,st,maxp,threshold)
            r(idx,cl,maxp,ed,threshold)
        return 0
    #print(idx,cl,st,ed,threshold)
    r(idx,cl,st,ed,threshold)
    #print(idx)
    for i in range(pnum-1,0,-1):
        if 0==idx[i]:
            line.deleteVertex(i)
    print('{} points left after daogelas method, length/orginlength:{}'.format(cl.numPoints(),line.length()/length) )
    
    return line,cl.numPoints()

def lengthmin_method(line,percent=0.1):
    cl=line.constGet()
    pnum=cl.numPoints()
    length=0
    pdist=[]
    p1dist=[]
    i=0
    while i<pnum-1 :  #clac distancs between 
        stp=cl.pointN(i)
        edp=cl.pointN(i+1)
        d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
        pdist.append(d**0.5)
        length+=d**0.5
        if i+2<pnum:
            edp=cl.pointN(i+2)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            p1dist.append(d**0.5)
        i+=1
    #print(pdist)
    #print(p1dist)
    ddl=[]
    for i,d in enumerate(p1dist):
        dd=pdist[i]+pdist[i+1]-d
        ddl.append(dd)
    while line.length()/length>1-percent:
        
        idx=np.argmin(ddl)+1
        line.deleteVertex(idx)
        #print(line.length()/length)
        cl=line.constGet()
        pnum=cl.numPoints()
        pdist=[]
        p1dist=[]
        i=0
        while i<pnum-1 :  #clac distancs between 
            stp=cl.pointN(i)
            edp=cl.pointN(i+1)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            pdist.append(d**0.5)
            if i+2<pnum:
                edp=cl.pointN(i+2)
                d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
                p1dist.append(d**0.5)
            i+=1
        #print(pdist)
        #print(p1dist)
        ddl=[]
        for i,d in enumerate(p1dist):
            dd=pdist[i]+pdist[i+1]-d
            ddl.append(dd)
    print('{} left after lengthmin method, length/orginlength={}'.format(pnum,line.length()/length))
    return line
    
def lengthmin2_method(line,deletenum=1):
    ''' jiasu mingtian '''
    cl=line.constGet()
    pnum=cl.numPoints()
    length=0
    pdist=[]
    p1dist=[]
    i=0
    while i<pnum-1 :  #clac distancs between 
        stp=cl.pointN(i)
        edp=cl.pointN(i+1)
        d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
        pdist.append(d**0.5)
        length+=d**0.5
        if i+2<pnum:
            edp=cl.pointN(i+2)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            p1dist.append(d**0.5)
        i+=1
    #print(pdist)
    #print(p1dist)
    ddl=[]
    for i,d in enumerate(p1dist):
        dd=pdist[i]+pdist[i+1]-d
        ddl.append(dd)
    while deletenum>0:
        
        idx=np.argmin(ddl)+1
        line.deleteVertex(idx)
        deletenum-=1
        #print(line.length()/length)
        cl=line.constGet()
        pnum=cl.numPoints()
        
        pdist.pop(idx)
        pdist[idx-1]=p1dist[idx-1]
        
        #print(p1dist,idx)
        p1dist.pop(idx-1)
        ddl.pop(idx-1)
        if idx>=2:
            stp=cl.pointN(idx-2)
            edp=cl.pointN(idx)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            p1dist[idx-2]=d**0.5
            ddl[idx-2]=pdist[idx-2]+pdist[idx-1]-p1dist[idx-2]
        if idx<pnum-1:
            stp=cl.pointN(idx-1)
            edp=cl.pointN(idx+1)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            p1dist[idx-1]=d**0.5
            ddl[idx-1]=pdist[idx-1]+pdist[idx]-p1dist[idx-1]
        #print(idx,pdist,p1dist,pnum)
        '''pdist=[]
        p1dist=[]
        i=0
        while i<pnum-1 :  #clac distancs between 
            stp=cl.pointN(i)
            edp=cl.pointN(i+1)
            d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
            pdist.append(d**0.5)
            if i+2<pnum:
                edp=cl.pointN(i+2)
                d=(stp.x()-edp.x())**2+(stp.y()-edp.y())**2
                p1dist.append(d**0.5)
            i+=1
        #print(pdist)
        #print(p1dist)
        ddl=[]
        for i,d in enumerate(p1dist):
            dd=pdist[i]+pdist[i+1]-d
            ddl.append(dd)'''
    print('{} left after lengthmin method, length/orginlength={}'.format(pnum,line.length()/length))
    return line



        
def clear():
    qins=QgsProject.instance()
    layers=qins.mapLayers()
    qins.removeMapLayers(layers)
    
#some illustrion on thesis
def fig13():
    clear()
    x=[0,1,2,3,4,5,6,7,8]
    y=[0,0,0.3,0,0,1,0,0,0]
    line=makeline(x,y,len(x))
    y=[0]*9
    line2=makeline(x,y,len(x))
    showline(line)
    showline(line2)

def experimenttable1(PN=50,threshold=1):
    clear()
    test(PN,threshold)