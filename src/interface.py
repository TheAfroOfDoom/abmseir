###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 03/04/2021
# Modified By: Jordan Williams
###

from log_handler import logging as log
from simulation import Simulation
import datetime
import graph_handler
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import tkinter.filedialog as tkfd
import config

class UIController(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.interface = Interface(self)

class UIModule(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.params = {}

    def add_param(self, name, text, default=None):
        # Declares a new param to be added to the interface
        var = tk.IntVar(self, value=default, name=name)
        entry = tk.Entry(self, bd=5, textvariable=var)
        entry.pack(side='left')
        label = tk.Label(self, text=text)
        label.pack(side='left')
        self.params[name] = default

    def get_params(self):
        for param in self.params:
            self.params[param] = int(self.getvar(param))
        return self.params

class Interface(UIModule):
    def __init__(self, root):
        UIModule.__init__(self, root)
        self.graph_manager = GraphManager(self)
        self.output_panel = OutputPanel(self)
        self.menu = self.gen_menu()
        root.config(menu=self.menu)
        '''
        Currently implemented params:
        time_horizon
        initial_infected_count
        exogenous_rate
        '''

    def simulate(self):
        sim = self.generate_sim()
        sim.run()
        self.output_panel.plot_data(sim.data, sim.data['day'], sim.all_states)
        self.export_data_to_file(sim)
        log.info("R0: %.2f" % (sim.calculate_r0()))

    def generate_sim(self):
        sim = Simulation(self.load_graph())
        log.info(self.params)
        sim.set_parameters(self.get_params())
        return sim
        
    def load_graph(self):
        if int(self.getvar('graph_mode')) == 1:
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
        menu = tk.Menu(self)
        menu_file = tk.Menu(menu, tearoff=0)
        #menu_file.add_command(label="New")
        #menu_file.add_command(label="Open")
        #menu_file.add_command(label="Save")
        #menu_file.add_command(label="Save as...")
        #menu_file.add_command(label="Close")
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=menu_file)
        return menu
    
    def btn_sim_cb(self):
        self.simulate()

    def create_window(self):
        self.add_param('time_horizon', 'Days', default=100)
        self.add_param('initial_infected_count', 'Initial Infection Count', default=10)
        self.add_param('exogenous_rate', 'Weekly Exogenous Infections', default=10)
        btn_sim = tk.Button(self, text='Simulate', command=self.btn_sim_cb)
        btn_sim.pack(side=tk.BOTTOM)
        self.graph_manager.pack()
        #self.output_panel.pack(side=tk.RIGHT)
        self.pack()
        self.mainloop()

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

class OutputPanel(UIModule):
    def __init__(self, root):
        UIModule.__init__(self,root)
        self.create_graph_panel()

    def create_graph_panel(self):
        f = Figure(figsize=(5,5), dpi=100)
        self.output_graph = f.add_subplot(111)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True)
        self.output_graph.set_prop_cycle(color = ['green', 'orange', 'red', 'purple', 'blue', 'brown'])

    def plot_data(self, data, time_steps, states):
        for state in states:
            self.output_graph.plot(time_steps, data[state], label = state)
        self.output_graph.legend()

class GraphManager(UIModule):
    def __init__(self, root):
        UIModule.__init__(self, root)
        self.graph_file_name = None
        self.frm_graph_load = self.gen_frm_graph_load()
        self.frm_graph_gen = GraphGenerator(self)
        self.graph_mode = tk.IntVar(root, value=1, name='graph_mode')
        frm_graph_mode = tk.Frame(root)
        rbtn_graph_load = tk.Radiobutton(frm_graph_mode, text='Load Graph', command=self.rbtn_graph_load_cb, variable=self.graph_mode, value=1)
        rbtn_graph_gen = tk.Radiobutton(frm_graph_mode, text='Generate Graph', command=self.rbtn_graph_gen_cb, variable=self.graph_mode, value=2)
        rbtn_graph_load.pack(side='left')
        rbtn_graph_gen.pack(side='right')
        frm_graph_mode.pack(side='bottom')
        self.frm_graph_load.pack(side='bottom')
        self.frm_graph_gen.pack(side='top')

    def gen_frm_graph_load(self):
        frm_graph_load = tk.Frame(self)
        btn_graph_select = tk.Button(frm_graph_load, text='Select Graph', command=self.btn_graph_select_cb)
        btn_graph_select.pack(side='left')
        return frm_graph_load

    def btn_graph_select_cb(self):
        self.graph_file_name = tkfd.askopenfilename(initialdir = config.settings['graph']['directory'])

    def rbtn_graph_load_cb(self):
        self.frm_graph_gen.pack_forget()
        self.frm_graph_load.pack(side='bottom')

    def rbtn_graph_gen_cb(self):
        self.frm_graph_load.pack_forget()
        self.frm_graph_gen.pack(side='bottom')

class GraphGenerator(UIModule):
    def __init__(self, root):
        UIModule.__init__(self, root)
        self.frm_graph_gen_ring = self.gen_frm_graph_gen_ring()
        self.frm_graph_gen_ws = self.gen_frm_graph_gen_ws()
        self.graph_type = 0
        lbox_graph_gen_type = tk.Listbox(self, height=3, name='lbox_graph_gen_type')
        lbox_graph_gen_type.insert(1, 'Complete')
        lbox_graph_gen_type.insert(2, 'Ring')
        lbox_graph_gen_type.insert(3, 'Watts-Strogatz')
        lbox_graph_gen_type.bind('<<ListboxSelect>>', self.lbox_graph_gen_type_cb)
        lbox_graph_gen_type.pack()

    def gen_frm_graph_gen_ring(self):
        frm_graph_gen_ring = tk.Frame(self)
        self.add_param('node_degree', 'Neighbors Per Node', default=3)
        return frm_graph_gen_ring

    def gen_frm_graph_gen_ws(self):
        frm_graph_gen_ws = tk.Frame(self)
        self.add_param('node_degree', 'Neighbors Per Node', default=3)
        self.add_param('diameter_goal', 'Diameter Goal', default=42)
        self.add_param('rng', 'Generation Seed', default=0)
        self.add_param('population_size', 'Population', default=5000)
        return frm_graph_gen_ws

    def lbox_graph_gen_type_cb(self, event):
        type = self.children['lbox_graph_gen_type'].curselection()[0]
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
    controller = UIController()
    controller.interface.create_window()