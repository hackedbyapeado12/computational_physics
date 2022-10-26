import numpy as np
import matplotlib.pyplot as plt
import time
import streamlit as st
import pandas as pd
import re
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib import pyplot as plt
import numpy as np
import graphviz
import networkx as nx
import sys
sys.setrecursionlimit(15000)

st.set_page_config(page_title="Scientific Computing", 
    page_icon="🧊", 
	layout="wide", 
	initial_sidebar_state="collapsed", 
	menu_items=None)

# -----------
# random walk
def run_random_walk():
    st.markdown(r"""# RandomWalk""")
    def accumulate(x):
        X=np.zeros(len(x))
        X[0] = x[0]
        
        for i, _ in enumerate(x):
            #st.write(i)
            X[i] = X[i-1]+x[i]
        return X

    def randomWalk(nsteps, sigma2=1, seed=42, axisscale='linear'):
        (dx_f, dy_f) = (lambda theta, r=1: r*trig(theta) for trig in (np.cos, np.sin)) 
        dx_f = lambda theta, r = 1: r*np.cos(theta)
        dy_f = lambda theta, r = 1: r*np.sin(theta)

        np.random.seed(seed)
        thetas_uniform = np.random.uniform(0,2*np.pi,nsteps)
        thetas_randn = np.random.randn(nsteps)*sigma2
        thetas_bimodal = np.concatenate([ np.random.randn(nsteps//2) * sigma2-1, 
                                          np.random.randn(nsteps//2) * sigma2+1 ])

        thetas_uniform[0], thetas_randn[0], thetas_bimodal[0] = 0, 0, 0 

        rands = [thetas_uniform, thetas_randn, thetas_bimodal]
        rands_names = 'uniform, normal, bimodal'.split(', ')

        def plot2():
            colors = 'r g y'.split()
            fig = plt.figure(figsize=(12,6))
            
            gs = GridSpec(3, 3, figure=fig)
            ax1 = [fig.add_subplot(gs[i, 0]) for i in range(3)]
            ax2 = fig.add_subplot(gs[:, 1:])    
            
            lims = {'xl':0, 'xh':0, 'yl':0, 'yh':0}
            for i, (r, n) in enumerate(zip(rands, rands_names)):
                dx, dy = dx_f(r), dy_f(r)
                dx = np.vstack([np.zeros(len(dx)), dx]).T.flatten()
                dy = np.vstack([np.zeros(len(dy)), dy]).T.flatten()
                
                ax1[i].plot(dx,dy, lw=1, c=colors[i])
                ax1[i].set(ylim=(-1,1), xlim=(-1,1), 
                            xticks=[], yticks=[],facecolor = "black",)
                
                x = accumulate(dx)
                y = accumulate(dy)
                ax2.plot(x,y, lw=2, label=n,c=colors[i])

            ax2.set(facecolor = "black",# xticks=[], yticks=[],
                    xticklabels=[],
                    xscale=axisscale,
                    yscale=axisscale)
            ax2.legend(fontsize=20)
                
            ax2.set_xticks([])
            ax2.set_yticks([])
            ax1[0].set_title('Individual steps', fontsize=24)
            ax2.set_title('Cummulative path', fontsize=24)
            plt.tight_layout()
            fig.patch.set_facecolor('darkgrey')
            st.pyplot(fig)
        plot2()

    with st.sidebar:
        cols_sidebar = st.columns(2)
        nsteps = cols_sidebar[0].slider('nsteps',  4,   100, 14)
        seed   = cols_sidebar[1].slider('Seed',    0,   69 , 42)
        sigma2 = cols_sidebar[0].slider('Variance',0.2, 1. ,0.32)
        axisscale = cols_sidebar[1].radio('axis-scales', ['linear', 'symlog'])
        #yscale = cols_sidebar[1].radio('yscale', ['linear', 'symlog'])


    randomWalk(nsteps,sigma2, seed, axisscale)

    cols = st.columns(2)
    cols[0].markdown(r"""
    Continous steps in a random direction illustrates the
    differences between diff. distributions.

    Red steps are generated by sampling theta from a uniform distribution.
    This tends to keep us close to the origin.

    Normal and bi-modal distributions are different in that the
    similarity of step direction causes great displacement.

    """)

    cols[1].code(r"""
def randomWalk(nsteps):
    for i in range(nsteps):
        theta = random()
        dx = np.cos(theta) ; x += dx
        dy = np.sin(theta) ; y += dy 
    """)


# -----------
# percolation
def run_percolation():
    st.markdown(r"""# Percolation""")
    def makeGrid(size, seed=42): 
        np.random.seed(seed)
        grid = np.random.uniform(0,1,(size,size), )
        grid_with_border = np.ones((size+2,size+2))
        grid_with_border[1:-1, 1:-1] = grid
        return grid_with_border

    def checkNeighbours(pos, grid, domain, visited):
        (i,j) = pos
        neighbours = [(i-1,j), (i+1,j), (i,j-1), (i, j+1)]
        for n in neighbours:
            if (n[0]>=0) and (n[1]>=0) and (n[0]<len(grid)) and (n[1]<len(grid)):
                if grid[n] and (n not in visited):
                    domain.add(n)
                    visited.add(n)
                    domain_, visited_ = checkNeighbours(n, grid, domain, visited)
                    domain = domain.union(domain_)
                    visited = visited.union(visited_)
                else: visited.add(n)
        return domain, visited

    def getDomains(grid, p=.5):
        open_arr = grid < p
        domains = {} ; index = 0; visited = set()
        for i, _ in enumerate(open_arr):
            for j, val in enumerate(open_arr[i]):
                if val:
                    if (i,j) in visited:
                        domain, visited_ = checkNeighbours((i,j), open_arr, domain=set(), visited=visited)
                    else:
                        visited.add((i,j))
                        domain, visited_ = checkNeighbours((i,j), open_arr, domain=set([(i,j)]), visited=visited)
                    domains[index] = domain
                    visited = visited.union(visited_)
                    index+=1
                else:
                    visited.add((i,j))
        
        new_domains = {}
        index = 0
        for d in domains:
            if len(domains[d]) !=0:
                new_domains[index] = domains[d]
                index += 1
                
        return new_domains

    def percolation():
        grid = makeGrid(size,seed)
        domains = getDomains(grid, p)

        x = np.arange(size+2)
        X,Y = np.meshgrid(x,x)
        
        fig, ax = plt.subplots()
        # background
        ax.scatter(X,Y, c='black')

        # colors
        colors = sns.color_palette("hls", len(domains))
        np.random.shuffle(colors)
        colors = np.concatenate([[colors[i]]*len(domains[i]) for i in domains])

        # plot
        xx = np.concatenate([list(domains[i]) for i in domains])
        ax.scatter(xx[:,0], xx[:,1], c=colors, marker=marker)
        ax.set(xticks = [], yticks = [], facecolor='black')
        fig.patch.set_facecolor('darkgrey')
        st.pyplot(fig)
    
    with st.sidebar:
        cols_sidebar = st.columns(2)
        size = cols_sidebar[0].slider('size', 10  , 100, 50)
        p = cols_sidebar[1].slider('p',       0.01, 1. , .1)
        marker_dict = {
            'point': '.',
            'square': 's',
            'pixel': ',',
            'circle': 'o',
        }
        marker_key = st.select_slider('marker', marker_dict.keys())
        marker = marker_dict[marker_key]
        seed = st.slider('seed',10,100)

    percolation()
    cols = st.columns(2)
    cols[0].markdown(r"""
    A matrix containing values between zero and one, with
    the value determining openness as a function of $p$.

    After generating a grid and a value for p, we look for 
    connected domains. 
    """)

    cols[1].code(r"""
def getDomains(grid, p=.5):
    open_arr = grid < p
    domains = {} ; index = 0; visited = set()
    for i, _ in enumerate(open_arr):
        for j, val in enumerate(open_arr[i]):
            if val:
                if (i,j) in visited:
                    domain, visited_ = checkNeighbours((i,j), open_arr, domain=set(), visited=visited)
                else:
                    visited.add((i,j))
                    domain, visited_ = checkNeighbours((i,j), open_arr, domain=set([(i,j)]), visited=visited)
                domains[index] = domain
                visited = visited.union(visited_)
                index+=1
            else:
                visited.add((i,j))""")


# -----------
# mandel brot
def run_fractals():
    def stable(z):
        try:
            return False if abs(z) > 2 else True
        except OverflowError:
            return False
    stable = np.vectorize(stable)


    def mandelbrot(c, a, n=50):
        z = 0
        for i in range(n):
            z = z**a + c
        return z

    def makeGrid(resolution, lims=[-1.85, 1.25, -1.25, 1.45]):
        re = np.linspace(lims[0], lims[1], resolution)[::-1]
        im = np.linspace(lims[2], lims[3], resolution)
        re, im = np.meshgrid(re,im)
        return re+im*1j

    def plot_(res):
        fig = plt.figure(figsize=(12,6))
        plt.imshow(res.T, cmap='magma')
        plt.xticks([]); plt.yticks([])
        plt.xlabel('Im',rotation=0, loc='right', color='blue')
        plt.ylabel('Re',rotation=0, loc='top', color='blue')
        fig.patch.set_facecolor('black')
        st.pyplot(fig)

    with st.sidebar:
        cols_sidebar = st.columns(2)
        logsize = cols_sidebar[0].slider(r'Resolution (log)',1.5,4., 3.)
        size = int(10**logsize)
        cols_sidebar[1].latex(r'10^{}\approx {}'.format("{"+str(logsize)+"}", size))
        cols_sidebar = st.columns(2)
        n = cols_sidebar[0].slider('n',1,50,27)
        a = cols_sidebar[1].slider('a',0.01,13.,2.3)

    res = stable(mandelbrot(makeGrid(size,  lims=[-1.85, 1.25, -1.25, 1.45]), a=a, n=n))
    plot_(res)

    cols = st.columns(2)
    cols[0].markdown(r"""
    The Mandelbrot set contains complex numbers remaining stable through
    
    $$z_{i+1} = z^a + c$$
    
    after successive iterations. We let $z_0$ be 0.
    """)
    cols[1].code(r"""
def stable(z):
    try:
        return False if abs(z) > 2 else True
    except OverflowError:
        return False
stable = np.vectorize(stable)


def mandelbrot(c, a, n=50):
    z = 0
    for i in range(n):
        z = z**a + c
    return z

def makeGrid(resolution, lims=[-1.85, 1.25, -1.25, 1.45]):
    re = np.linspace(lims[0], lims[1], resolution)[::-1]
    im = np.linspace(lims[2], lims[3], resolution)
    re, im = np.meshgrid(re,im)
    return re+im*1j    """)


# -----------
# Bereaucrats
def bereaucrats():
    arr = np.zeros((3,4))
    N = len(arr.flatten())
    nsteps = 100

    _mean = []
    for step in range(nsteps):
        # bring in 1 task
        rand_index = np.random.randint(0,N)
        who = (rand_index//arr.shape[1], rand_index%arr.shape[1])
        arr[who] += 1


        # if someone has 4 tasks redistribute to neighbours
        for i, _ in enumerate(arr):
            for j, _ in enumerate(arr[i]):
                if arr[i,j] >= 4:
                    try: arr[i+1, j] +=1
                    except: pass
                    try: arr[i-1, j] +=1
                    except: pass
                    try: arr[i, j+1] +=1
                    except: pass
                    try: arr[i, j-1] +=1
                    except: pass
                    arr[i,j] -= 4
        _mean.append(np.mean(arr)) 
    _mean = np.array(_mean)

    fig = plt.figure()
    plt.plot(_mean)
    #lt.savefig('bureaucrats.png')
    #plt.close()
    st.pyplot(fig)
    
# -----------
# bakSneppen
def bakSneppen():

    def run(size, nsteps):
        chain = np.random.rand(size)

        X = np.empty((nsteps,size))
        L = np.empty(nsteps)
        for i in range(nsteps):
            lowest = np.argmin(chain)
            chain[(lowest-1+size)%size] = np.random.rand()
            chain[lowest] = np.random.rand()

            chain[(lowest+1)%size] = np.random.rand()
            X[i] = chain
            L[i] = lowest
        

        fig, ax = plt.subplots(2,1)
        ax[0].imshow(X.T, aspect  = nsteps/size*.5, vmin=0, vmax=1)
        ax[1].plot(L)
        st.pyplot(fig)

    with st.sidebar:
        nsteps = st.slider('nsteps',1,30)
        size = st.slider('size',10,31)
        st.write(size)
        run_ = st.radio('run', ['yes', 'no'])

    if run_=="yes":
        run(size, nsteps)

# -----------
# networkGenerator
def network():
    def make_network(n_persons = 5,alpha=.4):
        
        A = np.zeros((n_persons,n_persons))
        for i in range(n_persons):
            neighbours =  np.random.rand(n_persons)>alpha ; neighbours[i]=0
            if sum(neighbours) == 0: 
                a = np.random.randint(0,n_persons,4)
                a = a[a!=i][0]
                neighbours[a] =1
            A[i] += neighbours; A[:,i] = neighbours
        
        return A

    def draw_from_matrix(M, sick=[], pos=[]):
        sick = np.zeros(len(M)) if len(sick) == 0 else sick
        G = nx.Graph()
        for i, line in enumerate(M):
            G.add_node(i)

        for i, line in enumerate(M):
            for j, val in enumerate(line):
                if (i != j) and (val==1): 
                    G.add_edge(i, j)
        color_map = ['r' if s==1 else 'b' for s in sick]
        
        pos = nx.nx_agraph.graphviz_layout(G) if len(pos)==0 else pos
        
        nx.draw_networkx(G,pos, node_color=color_map)
        return pos


    with st.sidebar:
        N = st.slider('N',1,42,22)
        a = st.slider('alpha', 0.,1.,0.97)
    fig, ax = plt.subplots()

    net = make_network(N,a)
    draw_from_matrix(net)
    st.pyplot(fig)



func_dict = {
	'RandomWalk' : run_random_walk,
    'Percolation'   :run_percolation,
    'Fractals'    : run_fractals,
    'Bereaucrats'   : bereaucrats,
    'BakSneppen'    : bakSneppen,
    'Networks'       : network,
}

with st.sidebar:
	topic = st.selectbox("topic" , list(func_dict.keys()))

a = func_dict[topic] ; a()


#plt.style.available











