import csv
import copy
import math
import numpy as np
from pandas import *
import random as rd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time


def svd(a):#Calculates svd decomposition
    # positive number representable in the computer.
    eps = 1.e-15  # assumes double precision
    tol = 1.e-64/eps
    assert 1.0+eps > 1.0 # if this fails, make eps bigger
    assert tol > 0.0     # if this fails, make tol bigger
    itmax = 50
    u = copy.deepcopy(a)
    m = len(a)
    n = len(a[0])
    #if __debug__: print 'a is ',m,' by ',n
    if m < n:
        if __debug__: print 'Error: m is less than n'
        raise ValueError,'SVD Error: m is less than n.'
    e = [0.0]*n  # allocate arrays
    q = [0.0]*n
    v = []
    for k in range(n): v.append([0.0]*n)
 
    # Householder's reduction to bidiagonal form

    g = 0.0
    x = 0.0

    for i in range(n):
        e[i] = g
        s = 0.0
        l = i+1
        for j in range(i,m): s += (u[j][i]*u[j][i])
        if s <= tol:
            g = 0.0
        else:
            f = u[i][i]
            if f < 0.0:
                g = math.sqrt(s)
            else:
                g = -math.sqrt(s)
            h = f*g-s
            u[i][i] = f-g
            for j in range(l,n):
                s = 0.0
                for k in range(i,m): s += u[k][i]*u[k][j]
                f = s/h
                for k in range(i,m): u[k][j] = u[k][j] + f*u[k][i]
        q[i] = g
        s = 0.0
        for j in range(l,n): s = s + u[i][j]*u[i][j]
        if s <= tol:
            g = 0.0
        else:
            f = u[i][i+1]
            if f < 0.0:
                g = math.sqrt(s)
            else:
                g = -math.sqrt(s)
            h = f*g - s
            u[i][i+1] = f-g
            for j in range(l,n): e[j] = u[i][j]/h
            for j in range(l,m):
                s=0.0
                for k in range(l,n): s = s+(u[j][k]*u[i][k])
                for k in range(l,n): u[j][k] = u[j][k]+(s*e[k])
        y = abs(q[i])+abs(e[i])
        if y>x: x=y
    # accumulation of right hand gtransformations
    for i in range(n-1,-1,-1):
        if g != 0.0:
            h = g*u[i][i+1]
            for j in range(l,n): v[j][i] = u[i][j]/h
            for j in range(l,n):
                s=0.0
                for k in range(l,n): s += (u[i][k]*v[k][j])
                for k in range(l,n): v[k][j] += (s*v[k][i])
        for j in range(l,n):
            v[i][j] = 0.0
            v[j][i] = 0.0
        v[i][i] = 1.0
        g = e[i]
        l = i
    #accumulation of left hand transformations
    for i in range(n-1,-1,-1):
        l = i+1
        g = q[i]
        for j in range(l,n): u[i][j] = 0.0
        if g != 0.0:
            h = u[i][i]*g
            for j in range(l,n):
                s=0.0
                for k in range(l,m): s += (u[k][i]*u[k][j])
                f = s/h
                for k in range(i,m): u[k][j] += (f*u[k][i])
            for j in range(i,m): u[j][i] = u[j][i]/g
        else:
            for j in range(i,m): u[j][i] = 0.0
        u[i][i] += 1.0
    #diagonalization of the bidiagonal form
    eps = eps*x
    for k in range(n-1,-1,-1):
        for iteration in range(itmax):
            # test f splitting
            for l in range(k,-1,-1):
                goto_test_f_convergence = False
                if abs(e[l]) <= eps:
                    # goto test f convergence
                    goto_test_f_convergence = True
                    break  # break out of l loop
                if abs(q[l-1]) <= eps:
                    # goto cancellation
                    break  # break out of l loop
            if not goto_test_f_convergence:
                #cancellation of e[l] if l>0
                c = 0.0
                s = 1.0
                l1 = l-1
                for i in range(l,k+1):
                    f = s*e[i]
                    e[i] = c*e[i]
                    if abs(f) <= eps:
                        #goto test f convergence
                        break
                    g = q[i]
                    h = pythag(f,g)
                    q[i] = h
                    c = g/h
                    s = -f/h
                    for j in range(m):
                        y = u[j][l1]
                        z = u[j][i]
                        u[j][l1] = y*c+z*s
                        u[j][i] = -y*s+z*c
            # test f convergence
            z = q[k]
            if l == k:
                # convergence
                if z<0.0:
                    #q[k] is made non-negative
                    q[k] = -z
                    for j in range(n):
                        v[j][k] = -v[j][k]
                break  # break out of iteration loop and move on to next k value
            if iteration >= itmax-1:
                if __debug__: print 'Error: no convergence.'
                # should this move on the the next k or exit with error??
                #raise ValueError,'SVD Error: No convergence.'  # exit the program with error
                break  # break out of iteration loop and move on to next k
            # shift from bottom 2x2 minor
            x = q[l]
            y = q[k-1]
            g = e[k-1]
            h = e[k]
            f = ((y-z)*(y+z)+(g-h)*(g+h))/(2.0*h*y)
            g = pythag(f,1.0)
            if f < 0:
                f = ((x-z)*(x+z)+h*(y/(f-g)-h))/x
            else:
                f = ((x-z)*(x+z)+h*(y/(f+g)-h))/x
            # next QR transformation
            c = 1.0
            s = 1.0
            for i in range(l+1,k+1):
                g = e[i]
                y = q[i]
                h = s*g
                g = c*g
                z = pythag(f,h)
                e[i-1] = z
                c = f/z
                s = h/z
                f = x*c+g*s
                g = -x*s+g*c
                h = y*s
                y = y*c
                for j in range(n):
                    x = v[j][i-1]
                    z = v[j][i]
                    v[j][i-1] = x*c+z*s
                    v[j][i] = -x*s+z*c
                z = pythag(f,h)
                q[i-1] = z
                c = f/z
                s = h/z
                f = c*g+s*y
                x = -s*g+c*y
                for j in range(m):
                    y = u[j][i-1]
                    z = u[j][i]
                    u[j][i-1] = y*c+z*s
                    u[j][i] = -y*s+z*c
            e[l] = 0.0
            e[k] = f
            q[k] = x
            # goto test f splitting
    return np.matmul(u,np.matmul(np.diag(q),np.transpose(v)))

def pythag(a,b):#Function to avoid overflow or underflow in qr Decomposition
    absa = abs(a)
    absb = abs(b)
    if absa > absb: return absa*math.sqrt(1.0+(absb/absa)**2)
    else:
        if absb == 0.0: return 0.0
        else: return absb*math.sqrt(1.0+(absa/absb)**2)


def frob(arr,k):#Calculate frobenius error
    m,n = arr.shape
    err=0.0
    for i in range(m):
        for j in range(n):
           err+=((arr[i][j]-k[i][j])**2)
    return math.sqrt(err)


def cur(p):#Calculates CUR decomposition
    m,n = p.shape
    row = [0.0 for i in range(m)]
    col = [0.0 for i in range(n)]
    tot=0;
    for i in range(m):
        for j in range(n):
                row[i]+=(p[i][j]*p[i][j])
                tot+=(p[i][j]*p[i][j])
    for i in range(n):
        for j in range(m):
            col[i]+=(p[j][i]*p[j][i])
    for i in range(m):
        row[i]/=tot
    for i in range(n):
        col[i]/=tot
    rowa = np.asarray(row)
    idx_r = rowa.argsort()[::-1]
    row_mat = p[idx_r] 
    cola = np.asarray(col)
    tran = np.transpose(p)
    idx_c = cola.argsort()[::-1]
    col_mat = tran[idx_c]
    col_mat = np.transpose(col_mat)
    num_c = rd.randrange(1,n+1)
    num_r = rd.randrange(num_c,m+1)
    row_mat = row_mat[:num_r,:]
    col_mat = col_mat[:,:num_c]
    row_mat = row_mat.astype(float)
    col_mat = col_mat.astype(float)
    x,y = row_mat.shape
    for i in range(x):
        for j in range(y):
            row_mat[i][j] = row_mat[i][j]/(math.sqrt(num_r * row[idx_r[i]]))
    x,y = col_mat.shape
    for i in range(x):
        for j in range(y):
            col_mat[i][j] = col_mat[i][j]/(math.sqrt(num_c * col[idx_c[j]]))
    i=0
    j=0
    lis=[]
    for i in range(num_r):
        for j in range(num_c):
            lis.append([idx_r[i],idx_c[j]])
    arr_u = [[] for i in range(num_r)]
    k=0
    for i in range(num_r):
        for j in range(num_c):
            arr_u[i].append(p[lis[k][0]][lis[k][1]])
            k+=1
    arr_u = np.asarray(arr_u)
    final_u = np.linalg.pinv(arr_u)
    return np.matmul(col_mat,np.matmul(final_u,row_mat))

def randrange(n, vmin, vmax):
    return (vmax - vmin)*np.random.rand(n) + vmin


def dataToMatrix(examp):#Converts the user-item data from the file into a matrix
    d = {}
    li=[]
    for li in examp:
        d[li[0]]={}
    for li in examp:
        d[li[0]][li[1]] = int(li[2])
    df = DataFrame.from_dict(d,orient='index').fillna(0)
    arr = df.as_matrix()
    return arr    


csvfile = open('C:\Users\Nishanth\Desktop\data.csv')
reader = csv.reader(csvfile)
examp = list(reader)
x=[]
y=[]
zc=[]
zs=[]
tc=[]
ts=[]
for i in range(1000,49,-25):
    arr1 = dataToMatrix(examp[:i])
    arr2 = arr1
    arr3 = arr1
    m,n = arr1.shape
    x.append(m)
    y.append(n)
    p = time.time()
    k = cur(arr2)
    tc.append(time.time()-p)
    error = 0.0
    error = frob(arr1,k)
    zc.append(error)
    p = time.time()
    k = svd(arr3.tolist())
    ts.append(time.time()-p)
    error = 0.0
    error = frob(arr1,k)
    zs.append(error)
fig = plt.figure()
fig1 = plt.figure()
ax = fig.add_subplot(111, projection='3d')
bx = fig1.add_subplot(111, projection='3d')
c, m = ('r', 'o')
ax.scatter(x, y, zs, c=c, marker=m)
c, m = ('b', '^')
ax.scatter(x, y, zc, c=c, marker=m)
ax.set_xlabel('Rows')
ax.set_ylabel('Columns')
ax.set_zlabel('Error')
c, m = ('r', 'o')
bx.scatter(x, y, ts, c=c, marker=m)
c, m = ('b', '^')
bx.scatter(x, y, tc, c=c, marker=m)
bx.set_xlabel('Rows')
bx.set_ylabel('Columns')
bx.set_zlabel('Time')
plt.show()
print "Done..!"
csvfile.close()