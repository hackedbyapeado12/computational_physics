import numpy as np
import matplotlib.pyplot as plt
import time
import streamlit as st
import numpy as np
import pandas as pd
from complex_utils import *
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib as mpl
import seaborn as sns
try: import graphviz # having trouble with this when hosted
except: pass
try: import networkx as nx  # networkx too :(
except: pass
import time
import sys

sys.setrecursionlimit(150000)

st.set_page_config(page_title="Scientific Computing", 
    page_icon="🧊", 
	layout="wide", 
	initial_sidebar_state="collapsed", 
	menu_items=None)

# setting matplotlib style:

mpl.rcParams['patch.facecolor'] = (0.04, 0.065, 0.03)
mpl.rcParams['axes.facecolor'] = (0.04, 0.065, 0.03)
mpl.rcParams['figure.facecolor'] = (0.04, 0.065, 0.03)
mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['ytick.color'] = 'white'
mpl.rcParams['figure.autolayout'] = True  # 'tight_layout'
# mpl.rcParams['axes.grid'] = True  # should we?

textfile_path = 'assets/complex/text/'

def homeComplex():
    text = getText_prep(filename = textfile_path+'home.md')
    st.title('Complex Physics')
    st.markdown(text['# Complex Physics'])

def statisticalMechanics():
    
    # Sidebar
    with st.sidebar:
        size = st.slider('size',3,100,10)
        beta = st.slider('beta',0.01,5.,1.)
        nsteps = st.slider('nsteps',3,10000,100)
        nsnapshots = 8
    
    # Detailed Description
    ## some of these should perhaps be partially unpacked
    st.markdown(r"""# Statistical Mechanics""")
    text_dict = getText_prep(filename = textfile_path+'statisticalMechanics.md', 
                                split_level = 2)
    
    with st.expander("Microcanonical Ensemble", expanded=False):
        text_dict["Microcanonical Ensemble"]

    with st.expander("Ising Model ", expanded=False):
        text_dict["Ising Model "]
    
    with st.expander("Metropolis algorithm", expanded=False):
        text_dict["Metropolis algorithm"]
        cols = st.columns(2)
        cols[0].markdown(r"""
            As I mentioned earlier, first step of Metropolis algorithm is 
            trying random state transition.
            In second step of the algorithm, first caliculate energy difference.
            If energy difference is negative, accept the trial transition.
            If energy difference is positive, accept with weight 
            $\exp \left[-\beta \Delta E_{ij} \right]$. 
            """)
        
        cols[1].pyplot(metropolisVisualization(beta))

    with st.expander("Mean Field Solution to Ising Model", expanded=False):
        text_dict["Mean Field Solution to Ising Model"]
    
    # Simulation
    results, data = ising(size, nsteps, beta, nsnapshots)
     
    st.markdown(r"""
        ### Ising 2d Simulation  
        Snapshots of the output of a simulation of the 2d Ising modelusing the metropolis algorithm.
        """)
    st.pyplot(plotSnapshots(results, nsnapshots))

    st.markdown(r"""If we track paramters through time,
        we may be able to spot a phase transition (they're a rare breed).
        On the right are plots of the energy and magnetization over time. Below
        is susceptibility as obtained the variance of the magnetization, 
        $\chi = \left< \left< M\right> - M\right>$ (:shrug)""")
    st.pyplot(plotEnergy_magnetization(results))
    st.pyplot(plotSusceptibility(data))
    
def phaseTransitions_CriticalPhenomena():
    text_dict = getText_prep(filename = textfile_path+'phaseTransitions.md', split_level = 2)
    
    st.title('Phase Transitions and Critical Phenomena')

    key = 'Mean Field Solution to Ising Model'
    with st.expander(key, expanded=False):
        st.markdown(text_dict[key])
    
    key = '1D Ising model and transfer matrix method'
    with st.expander(key, expanded=False):
        st.markdown(text_dict[key])
      
    with st.sidebar:
        size = st.slider('size',3,100,30)
        beta = st.slider('beta',0.01,5.,1.5)
        nsteps = st.slider('nsteps',3,10000,100)
    
    
    fig, _ = ising_1d(size, beta, nsteps)
    st.pyplot(fig)

def percolation_and_fractals():
    # Side bar
    with st.sidebar:
        st.markdown('## Paramteres') 
        with st.expander('square grid percolation'):

            cols_sidebar = st.columns(2)
            size = cols_sidebar[0].slider('size', 4  , 64, 24)
            n_ps = cols_sidebar[1].slider('Num ps = ', 5,20,5)
            marker_dict = {'point': '.','pixel': ',',}
            marker = marker_dict[cols_sidebar[0].radio('marker', marker_dict.keys())]
            seed = cols_sidebar[1].slider('seed',10,100)

        with st.expander('Mandelbrot'):
            cols_sidebar = st.columns(2)
            logsize = cols_sidebar[0].slider(r'Resolution (log)',1.5,4., 2.)
            size_fractal = int(10**logsize)
            cols_sidebar[1].latex(r'10^{}\approx {}'.format("{"+str(logsize)+"}", size_fractal))
            cols_sidebar = st.columns(2)
            n = cols_sidebar[0].slider('n',1,50,27)
            a = cols_sidebar[1].slider('a',0.01,13.,2.3)


    # Render
    st.markdown(r"""# Percolation and Fractals""")
    
    st.markdown(r"""## Percolation""")
    cols = st.columns(2)
    cols[0].markdown(r"""
    Percolation theory considers the behavior of a network. An appropriate case to start with is a 2D lattice with nearest neigbour connections. Let the nodes (intersections) require activation energy $p$ to be *open*. Neighboring open sites connect to form domains.

    On the right, is a randomly generated grid. Vary $p$ to alter openness and affect the number of domains, $N(p)$.
    """)
    
    p_percolation = cols[0].slider("""p =""",       0.01, 1. , .1)
    fig_percolation, domains = percolation(size, seed, p_percolation,marker, devmod=False)
    #domains
    cols[1].pyplot(fig_percolation)
    cols[0].latex(r"""N({}) = {}""".format(p_percolation, len(domains)))
    
    fig = percolation_many_ps(n_ps, size, seed)
    cols[1].pyplot(fig)


    st.markdown(r"""By visualizing $N(p_c)$, we find that this lattice structure undergoes a phase transition at $p_c=\frac{1}{2}$
    """)
        
    # Bethe lattice
    st.markdown(r"""
    ## Bethe Lattice""")
    cols = st.columns(2)
    cols[0].markdown(r"""
    Bethe lattice (also called a regular tree)  is an infinite connected 
    cycle-free graph where all vertices have the same number of neighbors.  
    
    
    We may perform percolation on this lattice. To do this, we fill the adjencancy matrix, not with boolean value, but instead with random samples drawn from a uniform distribution.
    """)
    degree = cols[1].slider("""degree""",       2, 5 , 3)
    cols[1].pyplot(betheLattice(0, size={2:5,3:10,4:17,5:26}[degree], degree=degree))

    #st.graphviz_chart(betheLattice_old())
    size_beth = 40
    #cols=st.columns(2)
    p_beth = cols[0].slider("""p = """,       0.01, 1. , .33)
    
    st.pyplot( betheLattice(p_beth, size=size_beth, degree=degree))
    
    st.markdown(r'''Again we may take a look at the number of domains as a function of $p$.''')

    
    Ns = betheLattice(size=32, get_many=True, 
                    ps=np.linspace(.1,.9,7), degree=degree)
        
    fig, ax = plt.subplots(figsize=(7,3))
    ax.plot(Ns.keys(),Ns.values() , c='white')
    ax.set_xlabel(r'$p$', color='white')
    ax.set_ylabel(r'Number of domains, $N$ ', color='white')
    st.pyplot(fig)

    st.markdown(r"""We may find the critical point for different degree, $z$, bethe lattices.
    $$
        p_c = \frac{1}{z-1}
    $$
    """)

    st.markdown(r"""## Mandelbrot""")
    st.markdown(r"""
    The Mandelbrot set contains complex numbers remaining stable through the mandelbrot function after successive iterations. Note; we let $z_0$ be 0. The two main essential pieces of code are displayed below the plot.
    """)
    st.pyplot(run_fractals(size_fractal, a, n))
    st.markdown(r"""
    To optimize run-time, we have used that the output is symmetric across the real axis. We only calculate one side, i.e., 
    $$
        \text{stable} \left(\text{mandelbrot}(a+ib)\right)
        =
        \text{stable} \left(\text{mandelbrot}(a-ib)\right)
    $$
    """)
    
    cols = st.columns(2)
    cols[0].code(r"""
def stable(z):
    try:
        return False if abs(z) > 2 else True
    except OverflowError:
        return False
stable = np.vectorize(stable)""")
    
    cols[1].code(r"""
def mandelbrot(c, a=2, n=50):
    z = 0
    for i in range(n):
        z = z**a + c
    return z
""")
    st.markdown(r"""
    ## Fractal Dimension
    After we get the formulae for this, we could look at the fractal dimension of the mandelbrot set at different zoom-levels.
    """)

def selfOrganizedCriticality():
        # Sidebar
    with st.sidebar:
        cols_sidebar = st.columns(2)
        nsteps = cols_sidebar[0].slider('nsteps',  4,   100, 14)
        seed   = cols_sidebar[1].slider('Seed',    0,   69 , 42)
        sigma2 = cols_sidebar[0].slider('Variance',0.2, 1. ,0.32)
        step_size = cols_sidebar[0].slider('Stepsize = random^x, x=', 0.,3.,0.)
        axisscale = cols_sidebar[1].radio('axis-scales', ['linear', 'symlog'])
        #yscale = cols_sidebar[1].radio('yscale', ['linear', 'symlog'])
    
    st.markdown(r"""
    # Self organized criticality (SOC)
    Self-organized criticality, is a property of a dynamic system which have a critical point as an attractor. In this type of model, we may set initial values rather arbitrarily, as the system itself will evolve to the critical state. At the criticality, the model displays spatial or temporal scale-invariance.

    ## Bak-Sneppen
    """)
    # Main fig
    cols = st.columns(2)
    nsteps = cols[0].slider('nsteps',1,30000,5000)
    size = cols[1].slider('size',10,1000,300)
    bakSneppen_fig, L = bakSneppen(size, nsteps)
    st.pyplot(bakSneppen_fig)

    # fill
    cols = st.columns(2)
    cols[0].markdown(r"""
    The Bak-Sneppen method starts with a random vector. At each
    timestep the smallest element and its two neighbors, are each 
    replaced with new random numbers.

    The figure on the right depicts the mean magnitude of elements in
    the vector.
    """)
    fig_baksneppen_fill = bakSneppen_plot_fill(L)
    cols[1].pyplot(fig_baksneppen_fill)

    st.markdown(r"""
    To build further on this, we should identify power laws along each dimension.""")

    st.markdown(r"""
    ## Critical branching
    Critical branching is ...
    
    We may observe critial branching, by visualizing the first return of a random walk.

    In 1 dimension, we either take a step right or a step left at each iteration. It should be very likely that we return to the origin, however some *walks* may take us on a long trip.
    """)
    run_firstReturn1D = st.button('run: First return of 1d randomwalk')
    if run_firstReturn1D: firstReturn1D()

    st.markdown(r"""
    In 2 dimensions, we generate a random angle and take a step in that direction.
    """)
    st.code(r"""
    def randomWalk(nsteps):
        for i in range(nsteps):
            theta = random()
            dx = np.cos(theta) ; x += dx
            dy = np.sin(theta) ; y += dy 
        """)
    st.markdown(r"""
    When looking for first return in 2d with floating point angles, we must consider a region around origo to be *home*. I implement this by looking when the agent enters the unit circle after having been a distance greater than $\frac{3}{2}$ from the origin.
    """)
    run_firstReturn2D = st.button('run: First return of 2d randomwalk')
    if run_firstReturn2D: firstReturn2D()
    
    
    st.markdown(r"""
    Notice, it becomes increasingly unlikely to make a swift return as we add dimensions to our random walk model.""")

    st.markdown(r"""## Sandpile Model (bereaucrats)""")

    

    st.markdown(r"""
    The problem with beraucrats, is that they dont finish tasks. When a task 
    lands on the desk of one, the set a side to start a pile. When that pile contains 
    4 tasks, its time to distribute them amongst the nieghbors. If a
    beraucrat neighbours an edge, they may dispose of the task headed in that direction. 
    """)

    cols = st.columns(3)
    run_bereaucrats = cols[0].button('run: bereaucrat model')
    size_bereaucrats = cols[1].slider('size_bereaucrats', 10,100,30)
    nsteps_bereaucrats = cols[2].slider('nsteps_bereaucrats', 10,20000,3000)
    
    if run_bereaucrats: bereaucrats(nsteps_bereaucrats, size_bereaucrats)

    st.markdown(r"""
    After a while, the model reaches steady state. Analyzing the distribution of avalanche sizes in steady state, reveals the ...
    """)
    st.image('assets/complex/images/sandpile_2d_aval_dist.png')
    
    st.markdown('## Evolution Model')

def newNetwork():
    def makeBetheLattice(n_nodes = 10):
        M = np.zeros((n_nodes,n_nodes))

        idx = 1
        for i, _ in enumerate(M):
            if i ==0: n =3
            else: n =2
            M[i, idx:idx+n] = 1
            idx+=n

        return M+M.T

    import seaborn as sns

    def checkOpenNeighbours(open_neighbours,visited, domain, open_arr):
        
        for j in open_neighbours:
            if j not in visited:
                domain.append(j)
                visited.add(j)
                open_neighbours = np.argwhere(M[j] * open_arr).flatten()
                open_neighbours = open_neighbours[open_neighbours!=j]
                visited_, domain_ = checkOpenNeighbours(open_neighbours,visited, domain,open_arr)
                visited = visited.union(visited_)
                domain += domain
        return visited, domain
        
    def getDomains(M, p=0.3):
        
        open_arr = p>np.random.rand(len(M))
        visited = set()
        domains = []
        for i in range(len(M)):

            if i not in visited:
                if open_arr[i]:
                    domain = []
                    visited.add(i)
                    domain.append(i)

                    open_neighbours = np.argwhere(M[i] * open_arr).flatten()
                    open_neighbours = open_neighbours[open_neighbours!=i]
                    if len(open_neighbours)>0:
                        visited_, domain_ = checkOpenNeighbours(open_neighbours,visited, domain,open_arr)
                        visited = visited.union(visited_)
                        domain += domain
                    domains.append(set(domain))

        return domains
                    
                


    def draw_from_matrix(M, domains) :
        
        inDomain = {}
        for idx, d in enumerate(domains):
            for i in d:
                inDomain[i] = idx
        inDomain   
        
        
        G = nx.Graph()
        for i, line in enumerate(M):
            G.add_node(i)

        for i, line in enumerate(M):
            for j, val in enumerate(line):
                if (i != j) and (val==1): 
                    G.add_edge(i, j)
        palette = sns.color_palette('hls', len(domains))
        color_map = ['darkgrey' if i not in inDomain.keys() else palette[inDomain[i]] for i in range(len(M))]

        nx.draw_networkx(G, node_color=color_map, pos=nx.kamada_kawai_layout(G))
        
        
    import networkx as nx
    import numpy as np
    M = makeBetheLattice(34)
    domains = getDomains(M,0.6)
    open_arr = draw_from_matrix(M,domains)

def network():

    def makeBetheLattice(n_nodes = 10):
        M = np.zeros((n_nodes,n_nodes))

        idx = 1
        for i, _ in enumerate(M):
            if i ==0: n =3
            else: n =2
            M[i, idx:idx+n] = 1
            idx+=n

        return M+M.T

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
        color_map = ['r' if s==1 else 'white' for s in sick]
        
        pos = nx.nx_agraph.graphviz_layout(G) if len(pos)==0 else pos
        
        nx.draw_networkx(G,pos, node_color=color_map, edge_color='white')
        return pos


    with st.sidebar:
        network_type = st.selectbox('networt_type',['bethe', 'random'])
        N = st.slider('N',1,42,22)
        if network_type == 'random':
            a = st.slider('alpha', 0.,1.,0.97)
        
    fig, ax = plt.subplots()
    net = make_network(N,a) if network_type == 'random' else makeBetheLattice(N)
    draw_from_matrix(net)
    st.pyplot(fig)

def agent_event_models():
    st.markdown(r"""
    # Agent/event based models
    """)

def run_betHedging():

    st.markdown('# Bet-Hedghing')
    with st.sidebar:
        cols_sidebar = st.columns(2)
        nsteps = cols_sidebar[0].slider('nsteps',1,3000,500)
        starting_capital = cols_sidebar[1].slider('starting capital',1,1000,10)
        prob_loss = cols_sidebar[0].slider('loss probability', 0.,1.,.5) 
        invest_per_round = cols_sidebar[1].slider('invest per round', 0.,1.,.5) 

    capital = [starting_capital]
    for i in range(nsteps):
        if np.random.uniform()>prob_loss:
            capital.append(capital[i]*(1+invest_per_round))
        else:
            capital.append(capital[i]*(1-invest_per_round))

    fig, ax = plt.subplots()
    plt.plot(capital, c='purple')
    plt.xlabel('timestep', color='white')
    fig.patch.set_facecolor((.04,.065,.03))
    ax.set(yscale='log')
    plt.ylabel('capital', color='white')
    st.pyplot(fig)


func_dict = {
    'Contents' : homeComplex,
    'Statistical Mechanics' : statisticalMechanics,
    'Phase transitions & Critical phenomena' : phaseTransitions_CriticalPhenomena,
    'Percolation and Fractals'   : percolation_and_fractals,
	'Self-organized Criticality'    : selfOrganizedCriticality,
    'Networks'      : network,
    'Agent/event based models' : agent_event_models,
    'Econophysics'  : run_betHedging,
}
    

with st.sidebar:
	topic = st.selectbox("topic" , list(func_dict.keys()))

run_topic = func_dict[topic] ; run_topic()


#plt.style.available
