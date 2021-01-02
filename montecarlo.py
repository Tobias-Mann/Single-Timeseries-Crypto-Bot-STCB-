import multiprocessing as mp
import pandas as pd 
import numpy as np
import simulator
import smartstrategies
import qlearning as ql
from tqdm import tqdm



def perform_mc_simulation(env, data, repetitions = 100, output="./Data/lastmontecarlosimulation.csv"):
    # the q_table is asigned with the random starting values when the agent is initialized,
    # thus the same ql.environment can be reused in the simulation but the agent needs to be initialized each time
    performance_aggregator = pd.DataFrame(index=data.index, columns=range(repetitions))
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    inputs = []
    print(f"Starting Monte Carlo Simulation with {repetitions} repetitions, this will take a long time:\n")
    # define function for one simulation
    def simple_simulation(i, env, data, return_dict):
            # each simulation enforces the process to use a different seed, otherwise the random numbers in use will be the same for each simulation
            np.random.seed(i)
            agent = ql.agent(env)
            sim = simulator.simulator_environment()
            sim.initialize_decisionmaker(smartstrategies.smartbalancer)
            sim.decisionmaker.agent = agent
            sim.simulate_on_aggregate_data(data, verbose=False)
            return_dict[i] = sim.env.portfolio.portfolio_repricing(data)["cumreturn"].values
    
    for i in range(repetitions):
        p = mp.Process(target=simple_simulation, args=(i, env, data, return_dict))
        jobs.append(p)
        p.start()
    
    for proc in jobs:
        proc.join()
    
    print(f"\nDone with Generating Paths!\nAppending...\n")
    for i, cumreturn in return_dict.items():
        performance_aggregator[i] = cumreturn
    data = data.set_index("time")
    performance_aggregator.index = data.index
    if output is not None:
        performance_aggregator.to_csv(output)
        print(f"Saved the Paths in: {output}")
    return performance_aggregator