###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 02/25/2021
# Modified By: Jordan Williams
###

from tkinter.constants import SUNKEN
from log_handler import logging as log
from simulation import Simulation
import datetime
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
        time_steps = [0]
        for i in range(self.params['time_horizon']):
            time_steps.append(i + 1)
            sim.run_step()
        self.plot_data(sim.data, time_steps, sim.all_states)
        self.export_data_to_file(sim)
        log.info("R_0: %.2f" % (sim.calculate_r_0()))

    def generate_sim(self):
        sim = Simulation(self.load_graph())
        log.info(self.params)
        sim.update_parameters(self.params)    
        sim.pre_step() # Initializes simulation
        return sim
        
    def load_graph(self):
        if int(self.frame.getvar('graph_mode')) == 1:
            return graph_handler.import_graph(path = self.graph_manager.graph_file_name)
        else:
            params = self.graph_manager.frm_graph_gen.get_params()
            if self.graph_manager.frm_graph_gen.graph_type == 0:
                # Complete
                return graph_handler.import_graph(graph_type = 'complete',
                            graph_args = [params['population_size']]
                            )
            elif self.graph_manager.frm_graph_gen.graph_type == 1:
                # Ring
                return graph_handler.import_graph(graph_type = 'ring',
                            graph_args = [params['population_size'], params['node_degree']]
                            )
            elif self.graph_manager.frm_graph_gen.graph_type == 2:
                # Watts-Strogatz
                return graph_handler.import_graph(graph_type = 'wattsstrogatz',
                            graph_args = [params['population_size'], params['node_degree'], params['diameter_goal'], params['rng']]
                            )

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

    def plot_data(self, data, time_steps, states):
        fig, ax = plt.subplots(1, figsize=(8, 6))
        ax.set_prop_cycle(color = ['green', 'orange', 'red', 'purple', 'blue', 'brown'])
        for state in states:
            ax.plot(time_steps, data[state], label = state)
        ax.legend()
        plt.show()

    def export_data_to_file(self, simulation):
        '''https://stackoverflow.com/a/19476284
        '''
        # TODO(jordan): Change this to when the simulation started instead of when we're saving
        time = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        default_extension = '.csv'
        f = tkfd.asksaveasfile(mode = 'w',
                defaultextension = default_extension,
                filetypes = [('CSV', '*.csv')],
                initialdir = config.settings['output']['data']['directory'],
                initialfile = 'simulation_%s_%s' % (time, simulation.graph.name + default_extension),
                title = 'Save simulation data')
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        f.write(simulation.export_data())
        f.close()

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
        self.graph_file_name = tkfd.askopenfilename(initialdir = config.settings['graph']['directory'])

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
        self.add_param(self.frame, 'population_size', 'Population', default=5000)
        self.graph_type = 0
        lbox_graph_gen_type = tk.Listbox(self.frame, height=3, name='lbox_graph_gen_type')
        lbox_graph_gen_type.insert(1, 'Complete')
        lbox_graph_gen_type.insert(2, 'Ring')
        lbox_graph_gen_type.insert(3, 'Watts-Strogatz')
        lbox_graph_gen_type.bind('<<ListboxSelect>>', self.lbox_graph_gen_type_cb)
        lbox_graph_gen_type.pack()

    def gen_frm_graph_gen_ring(self):
        frm_graph_gen_ring = tk.Frame(self.frame)
        self.add_param(frm_graph_gen_ring, 'node_degree', 'Neighbors Per Node', default=3)
        return frm_graph_gen_ring

    def gen_frm_graph_gen_ws(self):
        frm_graph_gen_ws = tk.Frame(self.frame)
        self.add_param(frm_graph_gen_ws, 'node_degree', 'Neighbors Per Node', default=3)
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