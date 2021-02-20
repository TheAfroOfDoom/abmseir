###
# File: interface.py
# Created: 02/19/2021
# Author: Aidan Tokarski (astoka21@colby.edu)
# -----
# Last Modified: 02/19/2021
# Modified By: Aidan Tokarski
###

import simulation as sim
import graph_handler
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.messagebox as tkmb

class Interface:
    def __init__(self):
        self.pop_size = 500
        self.g = None

    def simulate(self):
        if self.g is None:
            self.loadGraph(self.pop_size)
        simulation = sim.Simulation(self.g)
        time_steps = []
        for i in range(100):
            time_steps.append(i)
            simulation.run_step()
        time_steps.append(time_steps[-1] + 1)
        data = simulation.data
        fig, ax = plt.subplots(1, figsize=(8, 6))
        ax.plot(time_steps, data['susceptible'], color='green', label='sus')
        ax.plot(time_steps, data['exposed'], color='orange', label='exp')
        ax.plot(time_steps, data['infected asymptomatic'], color='red', label='asymp')
        ax.plot(time_steps, data['infected symptomatic'], color='purple', label='symp')
        ax.plot(time_steps, data['recovered'], color='blue', label='rec')
        ax.plot(time_steps, data['dead'], color='brown', label='dsc')
        plt.show()
        
    def loadGraph(self, size):
        self.g = graph_handler.complete_graph([size])

    def create_window(self):
        window = tk.Tk()
        self.window = window

        pop_size = tk.IntVar(window, value=500, name='pop_size')
        frm_ps = tk.Frame(window)
        ent_pop_size = tk.Entry(frm_ps, bd=5, textvariable=pop_size)
        ent_pop_size.pack(side=tk.RIGHT)
        lbl_pop_size = tk.Label(frm_ps, text='Pop Size')
        lbl_pop_size.pack(side=tk.LEFT)
        frm_ps.pack(anchor=tk.N)
        btn_sim = tk.Button(window, text='Simulate', command=self.btn_sim_cb)
        btn_sim.pack(side=tk.BOTTOM)
        window.mainloop()
    
    def btn_sim_cb(self):
        self.pop_size = int(self.window.getvar('pop_size'))
        self.simulate()

if __name__ == '__main__':
    interface = Interface()
    interface.create_window()