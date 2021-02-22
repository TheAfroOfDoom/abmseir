###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 02/21/2021
# Modified By: Jordan Williams
###

from log_handler import logging as log
from simulation import Simulation
import graph_handler
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.filedialog as tkfd
import config

class UIModule:
    def __init__(self, root):
        self.params = {}
        self.root = root
        if(root is not None):
            self.frame = tk.Frame(root)
        else:
            self.frame = tk.Tk()

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

    def pack_forget(self):
        self.frame.pack_forget()

    def pack(self, **args):
        self.frame.pack(args)

    def get_params(self):
        for param in self.params:
            self.params[param] = int(self.frame.getvar(param))
        return self.params

class Interface(UIModule):
    def __init__(self):
        UIModule.__init__(self, root=None)
        self.graph_manager = GraphManager(self.frame)
        self.menu = self.gen_menu()
        self.frame.config(menu=self.menu)
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
        log.info(self.params)
        sim.update_parameters(self.params)
        return sim
        
    def load_graph(self):
        if int(self.frame.getvar('graph_mode')) == 1:
            return graph_handler.import_graph(path=self.graph_manager.graph_file_name)
        else:
            params = self.graph_manager.frm_graph_gen.get_params()
            if self.graph_manager.frm_graph_gen.graph_type == 0:
                # Complete
                return graph_handler.complete_graph([params['population_size']])
            elif self.graph_manager.frm_graph_gen.graph_type == 1:
                # Ring
                return graph_handler.ring_graph([params['population_size'], params['vertex_degree']])
            elif self.graph_manager.frm_graph_gen.graph_type == 2:
                # Watts-Strogatz
                return graph_handler.wattsstrogatz_graph([params['population_size'], params['vertex_degree'], params['diameter_goal'], params['rng']])
            

    def gen_menu(self):
        menu = tk.Menu(self.frame)
        menu_file = tk.Menu(menu, tearoff=0)
        #menu_file.add_command(label="New")
        #menu_file.add_command(label="Open")
        #menu_file.add_command(label="Save")
        #menu_file.add_command(label="Save as...")
        #menu_file.add_command(label="Close")
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.frame.quit)
        menu.add_cascade(label="File", menu=menu_file)
        return menu
    
    def btn_sim_cb(self):
        self.simulate()

    def create_window(self):
        self.add_param(self.frame, 'time_horizon', 'Days', default=100)
        self.add_param(self.frame, 'initial_infected_count', 'Initial Infection Count', default=10)
        self.add_param(self.frame, 'exogenous_rate', 'Weekly Exogenous Infections', default=10)
        btn_sim = tk.Button(self.frame, text='Simulate', command=self.btn_sim_cb)
        btn_sim.pack(side=tk.BOTTOM)
        self.graph_manager.pack()
        self.frame.mainloop()

    def plot_data(self, data, time_steps):
        fig, ax = plt.subplots(1, figsize=(8, 6))
        ax.plot(time_steps, data['susceptible'], color='green', label='sus')
        ax.plot(time_steps, data['exposed'], color='orange', label='exp')
        ax.plot(time_steps, data['infected asymptomatic'], color='red', label='asymp')
        ax.plot(time_steps, data['infected symptomatic'], color='purple', label='symp')
        ax.plot(time_steps, data['recovered'], color='blue', label='rec')
        ax.plot(time_steps, data['dead'], color='brown', label='dead')
        plt.show()

class GraphManager(UIModule):
    def __init__(self, root):
        UIModule.__init__(self, root)
        self.graph_file_name = None
        self.frm_graph_load = self.gen_frm_graph_load()
        self.frm_graph_gen = GraphGenerator(self.frame)
        self.graph_mode = tk.IntVar(root, value=1, name='graph_mode')
        frm_graph_mode = tk.Frame(root)
        rbtn_graph_load = tk.Radiobutton(frm_graph_mode, text='Load Graph', command=self.rbtn_graph_load_cb, variable=self.graph_mode, value=1)
        rbtn_graph_gen = tk.Radiobutton(frm_graph_mode, text='Generate Graph', command=self.rbtn_graph_gen_cb, variable=self.graph_mode, value=2)
        rbtn_graph_load.pack(side=tk.LEFT)
        rbtn_graph_gen.pack(side=tk.RIGHT)
        frm_graph_mode.pack(side=tk.BOTTOM)
        self.frm_graph_load.pack(side=tk.BOTTOM)

    def gen_frm_graph_load(self):
        frm_graph_load = tk.Frame(self.root)
        btn_graph_select = tk.Button(frm_graph_load, text='Select Graph', command=self.btn_graph_select_cb)
        btn_graph_select.pack(side=tk.LEFT)
        return frm_graph_load

    def btn_graph_select_cb(self):
        self.graph_file_name = tkfd.askopenfilename(initialdir='./' + config.settings['graph']['directory'])

    def rbtn_graph_load_cb(self):
        self.frm_graph_gen.pack_forget()
        self.frm_graph_load.pack(side=tk.BOTTOM)

    def rbtn_graph_gen_cb(self):
        self.frm_graph_load.pack_forget()
        self.frm_graph_gen.pack(side=tk.BOTTOM)

class GraphGenerator(UIModule):
    def __init__(self, root):
        UIModule.__init__(self, root)
        self.frm_graph_gen_ring = self.gen_frm_graph_gen_ring()
        self.frm_graph_gen_ws = self.gen_frm_graph_gen_ws()
        self.add_param(self.frame, 'population_size', 'Population', default=500)
        self.graph_type = 0
        lbox_graph_gen_type = tk.Listbox(self.frame, height=3, name='lbox_graph_gen_type')
        lbox_graph_gen_type.insert(1, 'Complete')
        lbox_graph_gen_type.insert(2, 'Ring')
        lbox_graph_gen_type.insert(3, 'Watts-Strogatz')
        lbox_graph_gen_type.bind('<<ListboxSelect>>', self.lbox_graph_gen_type_cb)
        lbox_graph_gen_type.pack()

    def gen_frm_graph_gen_ring(self):
        frm_graph_gen_ring = tk.Frame(self.frame)
        self.add_param(frm_graph_gen_ring, 'vertex_degree', 'Neighbors Per Node', default=3)
        return frm_graph_gen_ring

    def gen_frm_graph_gen_ws(self):
        frm_graph_gen_ws = tk.Frame(self.frame)
        self.add_param(frm_graph_gen_ws, 'vertex_degree', 'Neighbors Per Node', default=3)
        self.add_param(frm_graph_gen_ws, 'diameter_goal', 'Diameter Goal', default=42)
        self.add_param(frm_graph_gen_ws, 'rng', 'Generation Seed', default=0)
        return frm_graph_gen_ws

    def lbox_graph_gen_type_cb(self, event):
        type = self.frame.children['lbox_graph_gen_type'].curselection()[0]
        self.graph_type = type
        if(type == 0):
            # Complete
            self.frm_graph_gen_ring.pack_forget()
            self.frm_graph_gen_ws.pack_forget()
        elif(type == 1):
            # Ring
            self.frm_graph_gen_ws.pack_forget()
            self.frm_graph_gen_ring.pack()
        elif(type == 2):
            # Watts-Strogatz
            self.frm_graph_gen_ring.pack_forget()
            self.frm_graph_gen_ws.pack()

if __name__ == '__main__':
    interface = Interface()
    interface.create_window()