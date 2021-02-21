###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 02/19/2021
# Modified By: Aidan Tokarski
###

from typing_extensions import IntVar
from simulation import Simulation
import graph_handler
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.filedialog as tkfd
import config

class Interface:
    def __init__(self):
        self.window = tk.Tk()
        self.params = {}
        self.graph_generated = None
        self.frm_graph = tk.Frame(self.window)
        self.frm_graph_load = self.gen_frm_graph_load()
        self.frm_graph_gen = self.gen_frm_graph_gen()
        '''
        Currently implemented params:
        time_horizon
        initial_infected_count
        exogenous_rate
        '''

    def simulate(self):
        sim = self.generate_sim()
        time_steps = []
        for i in range(self.params['time_horizon']):
            time_steps.append(i)
            sim.run_step()
        self.plot_data(sim.data, time_steps)

    def generate_sim(self):
        sim = Simulation(self.load_graph())
        for param in self.params:
            self.params[param] = int(self.window.getvar(param))
            if param == 'initial_infected_count':
                sim.initial_infected_count = self.params[param]
            elif param == 'exgogenous_rate':
                sim.exogenous_rate = self.params[param]
        return sim
        
    def load_graph(self):
        if int(self.window.getvar('graph_mode')) == 1:
            return graph_handler.import_graph(path=self.graph_file_name)
        else:
            return graph_handler.complete_graph([int(self.frm_graph_gen.getvar('pop_size'))])

    def add_param(self, root_frame, name, text, default=None):
        # Declares a new param to be added to the interface
        var = tk.IntVar(root_frame, value=default, name=name)
        frame = tk.Frame(root_frame)
        entry = tk.Entry(frame, bd=5, textvariable=var)
        entry.pack(side=tk.RIGHT)
        label = tk.Label(frame, text=text)
        label.pack(side=tk.LEFT)
        frame.pack(anchor=tk.N)
        self.params[name] = default

    def gen_frm_graph_load(self):
        frm_graph_load = tk.Frame(self.window)
        btn_graph_select = tk.Button(frm_graph_load, text='Select Graph', command=self.btn_graph_select_cb)
        btn_graph_select.pack(side=tk.LEFT)
        return frm_graph_load

    def gen_frm_graph_gen(self):
        frm_graph_gen = tk.Frame(self.window)
        self.add_param(frm_graph_gen, 'pop_size', 'Node Count', default=500)
        return frm_graph_gen
    
    def btn_sim_cb(self):
        self.simulate()

    def btn_graph_select_cb(self):
        self.graph_file_name = tkfd.askopenfilename(initialdir='./' + config.settings['graph']['directory'])

    def rbtn_graph_load_cb(self):
        self.frm_graph_gen.pack_forget()
        self.frm_graph_load.pack(side=tk.BOTTOM)

    def rbtn_graph_gen_cb(self):
        self.frm_graph_load.pack_forget()
        self.frm_graph_gen.pack(side=tk.BOTTOM)

    def create_window(self):
        win = self.window
        self.add_param(win, 'time_horizon', 'Days', default=100)
        self.add_param(win, 'initial_infected_count', 'Initial Infection Count', default=10)
        self.add_param(win, 'exogenous_rate', 'Weekly Exogenous Infections', default=10)
        btn_sim = tk.Button(win, text='Simulate', command=self.btn_sim_cb)
        btn_sim.pack(side=tk.BOTTOM)
        graph_mode = tk.IntVar(win, value=1, name='graph_mode')
        frm_graph_mode = tk.Frame(win)
        rbtn_graph_load = tk.Radiobutton(frm_graph_mode, text='Load Graph', command=self.rbtn_graph_load_cb, variable=graph_mode, value=1)
        rbtn_graph_gen = tk.Radiobutton(frm_graph_mode, text='Generate Graph', command=self.rbtn_graph_gen_cb, variable=graph_mode, value=2)
        rbtn_graph_load.pack(side=tk.LEFT)
        rbtn_graph_gen.pack(side=tk.RIGHT)
        frm_graph_mode.pack(side=tk.BOTTOM)
        self.frm_graph_load.pack(side=tk.BOTTOM)
        win.mainloop()

    def plot_data(self, data, time_steps):
        fig, ax = plt.subplots(1, figsize=(8, 6))
        ax.plot(time_steps, data['susceptible'], color='green', label='sus')
        ax.plot(time_steps, data['exposed'], color='orange', label='exp')
        ax.plot(time_steps, data['infected asymptomatic'], color='red', label='asymp')
        ax.plot(time_steps, data['infected symptomatic'], color='purple', label='symp')
        ax.plot(time_steps, data['recovered'], color='blue', label='rec')
        ax.plot(time_steps, data['dead'], color='brown', label='dead')
        plt.show()


if __name__ == '__main__':
    interface = Interface()
    interface.create_window()