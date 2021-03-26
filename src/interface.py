###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 03/25/2021
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
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfd
import config
import re

class UIController(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title('SN-COV Beta v1.0.2')
        self.protocol("WM_DELETE_WINDOW", self.quit)
        #self.resizable(False, False)

        self.interface = self.create_interface()
        self.config(menu=self.gen_menu())
        self.frames = self.load_frames()
        self.show_frame(ParameterPanel, tk.NW)
        self.show_frame(GraphManager, tk.NW)
        self.show_frame(GraphLoader, tk.NW)
        self.show_frame(OutputPanel, tk.NE)
        btn_sim = tk.Button(self, text='Simulate', command=self.btn_sim_cb)
        btn_sim.pack(side=tk.BOTTOM)

    def create_interface(self):
        interface = tk.Frame(self)
        interface.pack(side="top", fill="both", expand=True)
        return interface

    def load_frames(self):
        frames = {}

        for F in (ParameterPanel, GraphManager, GraphLoader, GraphGenerator, OutputPanel):
            frame = F(self.interface, self)
            frames[F] = frame

        return frames

    def show_frame(self, wrapper, sticky=None):
        frame = self.frames[wrapper]
        frame.grid(row=frame.row, column=frame.col, sticky=sticky)

    def hide_frame(self, wrapper):
        frame = self.frames[wrapper]
        frame.grid_forget()
    
    def raise_frame(self, wrapper):
        frame = self.frames[wrapper]
        frame.tkraise()

    def gen_menu(self):
        menu = tk.Menu(self)
        menu_file = tk.Menu(menu, tearoff=0)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=menu_file)
        return menu

    def simulate(self):
        sim = self.generate_sim()
        sim.run()
        self.frames[OutputPanel].plot_data(sim.data, sim.data['day'], sim.all_states)
        self.export_data_to_file(sim)

        gens = sim.calculate_r0()
        gen1 = gens.get('1') or 0
        gen2 = gens.get('2') or 0
        r0 = gen2 / gen1

        log.info("R0: %.2f" % (r0))

    def generate_sim(self):
        sim = Simulation(self.load_graph())
        sim.set_parameters(self.frames[ParameterPanel].get_params())
        return sim

    def btn_sim_cb(self):
        self.simulate()

    def load_graph(self):
        if int(self.getvar('graph_mode')) == 1:
            return graph_handler.import_graph(path = self.frames[GraphLoader].graph_file_name)
        else:
            params = self.frames[GraphGenerator].get_params()
            if self.frames[GraphGenerator].graph_type == 'complete':
                # Complete
                return graph_handler.import_graph(graph_type = 'complete',
                            graph_args = [params['population_size']]
                            )
            elif self.frames[GraphGenerator].graph_type == 'ring':
                # Ring
                return graph_handler.import_graph(graph_type = 'ring',
                            graph_args = [params['population_size'], params['node_degree']]
                            )
            elif self.frames[GraphGenerator].graph_type == 'wattsstrogatz':
                # Watts-Strogatz
                return graph_handler.import_graph(graph_type = 'wattsstrogatz',
                            graph_args = [params['population_size'], params['node_degree'], params['diameter_goal'], params['rng']]
                            )

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

class UIModule(tk.Frame):
    def __init__(self, root, controller, row=0, col=0):
        tk.Frame.__init__(self, root, relief=tk.RAISED, borderwidth=1)
        self.params = {}
        self.controller = controller
        self.row = row
        self.col = col

    def add_param(self, name, text, default=None, root=None, entry_side = 'top', label_side='top'):
        # Declares a new param to be added to the interface
        var = tk.IntVar(self, value=default, name=name)
        label = tk.Label(root if (root != None) else self, text=text)
        label.pack(side=label_side)
        entry = tk.Entry(root if (root != None) else self, bd=5, textvariable=var)
        entry.pack(side=entry_side)

    def get_params(self):
        for param in self.params:
            self.params[param] = int(self.getvar(param))
        return self.params

class ParameterPanel(UIModule):
    def __init__(self, root, controller):
        UIModule.__init__(self, root, controller, row=0, col=0)
        
        self.add_param('initial_infected_count', 'Initial infection count', default=10)

        self.add_param('cycles_per_day', 'Cycles per day', default=3)
        self.add_param('time_horizon', 'Days', default=100)

        self.add_param('exogenous_amount', 'Exogenous amount', default=5)
        self.add_param('exogenous_frequency', 'Exogenous frequency', default=7)
        
        self.add_param('r0', 'Basic reproduction number (R0)', default=1.5)
        
        self.add_param('time_to_infection_mean', 'Mean time to infection (incubation)', default=3)
        self.add_param('time_to_infection_min', 'Min time to infection', default=0)

        self.add_param('time_to_recovery_mean', 'Mean time to recovery', default=14)
        self.add_param('time_to_recovery_min', 'Min time to recovery', default=0)
        
        self.add_param('symptoms_probability', 'Probability of symptoms', default=0.30)
        self.add_param('death_probability', 'Probability of death given symptoms', default=0.0005)
        
        self.add_param('specificity', 'Test specificity', default=0.997)
        self.add_param('sensitivity', 'Test sensitivity', default=0.9)
        self.add_param('cost', 'Test cost', default=25)
        self.add_param('results_delay', 'Delay until test results', default=1)
        self.add_param('rate', 'Rate of testing', default=0)

class OutputPanel(UIModule):
    def __init__(self, root, controller):
        UIModule.__init__(self, root, controller, row=0, col=1)
        self.create_graph_panel()

    def create_graph_panel(self):
        f = plt.figure(figsize=(5,5), dpi=100)
        self.output_graph = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True)
        self.output_graph.set_prop_cycle(color = ['green', 'orange', 'red', 'purple', 'blue', 'brown'])

    def plot_data(self, data, time_steps, states):
        for state in states:
            self.output_graph.plot(time_steps, data[state], label = state)
        self.output_graph.legend()
        self.canvas.draw()

class GraphManager(UIModule):
    def __init__(self, root, controller):
        UIModule.__init__(self, root, controller, row=1, col=0)
        self.graph_file_name = None
        self.graph_mode = tk.IntVar(root, value=1, name='graph_mode')
        rbtn_graph_load = tk.Radiobutton(self, text='Load Graph', command=self.rbtn_graph_load_cb, variable=self.graph_mode, value=1)
        rbtn_graph_gen = tk.Radiobutton(self, text='Generate Graph', command=self.rbtn_graph_gen_cb, variable=self.graph_mode, value=2)
        rbtn_graph_load.pack(side='left')
        rbtn_graph_gen.pack(side='right')

    def rbtn_graph_load_cb(self):
        self.controller.hide_frame(GraphGenerator)
        self.controller.show_frame(GraphLoader, tk.NW)

    def rbtn_graph_gen_cb(self):
        self.controller.hide_frame(GraphLoader)
        self.controller.show_frame(GraphGenerator, tk.NW)

class GraphLoader(UIModule):
    def __init__(self, root, controller):
        UIModule.__init__(self, root, controller, row=0, col=2)
        btn_graph_select = tk.Button(self, text='Select Graph', command=self.btn_graph_select_cb)
        btn_graph_select.pack(side='left')

    def btn_graph_select_cb(self):
        self.graph_file_name = tkfd.askopenfilename(initialdir = config.settings['graph']['directory'])

class GraphGenerator(UIModule):
    def __init__(self, root, controller):
        UIModule.__init__(self, root, controller, row=0, col=2)
        graph_definitions = config.settings['graph']['definitions'].items()
        self.frms_graph_gen = {}

        self.graph_type = tk.StringVar()
        self.rbtns = {}
        for graph_type, definition in graph_definitions:
            # Capitalize (CamelCase) graph type
            graph_title = definition.get('title') or graph_type.title().replace('_', ' ')

            # Make graph type's frame
            self.frms_graph_gen[graph_type] = eval('self.gen_frm_graph_gen_%s()' % (graph_type))

            # Make radio button
            self.rbtns[graph_type] = tk.Radiobutton(
                            self,
                            text=graph_title,
                            variable=self.graph_type,
                            value=graph_type,
                            command=self.lbox_graph_gen_type_cb
                        )
            rbtn_graph = self.rbtns[graph_type]
            rbtn_graph.pack(anchor=tk.W, side='top')

        # By default, select 'complete' radio button
        self.rbtns['complete'].invoke()

    def gen_frm_graph_gen_complete(self):
        frm_graph_gen_complete = tk.Frame(self)
        self.add_param('population_size', 'Population', default=5000, root=frm_graph_gen_complete)
        return frm_graph_gen_complete

    def gen_frm_graph_gen_ring(self):
        frm_graph_gen_ring = tk.Frame(self)
        self.add_param('population_size', 'Population', default=5000, root=frm_graph_gen_ring)
        self.add_param('node_degree', 'Neighbors per node', default=42, root=frm_graph_gen_ring)
        return frm_graph_gen_ring

    def gen_frm_graph_gen_wattsstrogatz(self):
        frm_graph_gen_wattsstrogatz = tk.Frame(self)
        self.add_param('population_size', 'Population', default=5000, root=frm_graph_gen_wattsstrogatz)
        self.add_param('node_degree', 'Neighbors per node', default=42, root=frm_graph_gen_wattsstrogatz)
        self.add_param('diameter_goal', 'Diameter goal', default=3, root=frm_graph_gen_wattsstrogatz)
        self.add_param('rng', 'Random seed', default=0, root=frm_graph_gen_wattsstrogatz)
        return frm_graph_gen_wattsstrogatz

    def lbox_graph_gen_type_cb(self):
        # Unpack all graph gen frames
        for graph_type, frm_graph_gen in self.frms_graph_gen.items():
            frm_graph_gen.pack_forget()

        graph_type = self.graph_type.get()        
        # Repack the one we want
        self.frms_graph_gen[graph_type].pack()

if __name__ == '__main__':
    controller = UIController()
    controller.mainloop()