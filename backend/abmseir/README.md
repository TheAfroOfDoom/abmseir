# **Modelling the Spread of SARS-CoV-2 using Small World Networks**
Simulating the spread of COVID-19 on the UMassD campus using a Strogatz-Watts network to determine social connections.

---
## Prerequisites

* [Python 3.9](https://www.python.org/downloads/)

  * Check version with `py --version`

* [Git](https://git-scm.com/)

  * Check version with `git --version`

* Some LaTeX processor to generate the report

  * I use [TeXworks](http://www.tug.org/texworks/)

---
## Installation

1. **Clone git repository**

In the command prompt or terminal, move the folder that you would like to keep the local repository. Once there type in the console:
```
git clone https://github.com/TheAfroOfDoom/SWN-COVID-Model.git
```  

This will create a local repository identical to this GitHub repository.

2. **Install dependencies**

In the command prompt or terminal, in the root of the local repository, type the following:
```
pip install -r requirements.txt
```  

---
## Run
To run the simulation and get graph outputs, use `main.py`:  
```
py src/main.py
```  

To get statistics and a preview of a graph file, modify and run `graphStats.py`:  
```
py graphStats.py
```  

## pretty
![Strogatz-Watts Graph](report/figures/ws/graph.png)
Strogatz-Watts Graph with 1500 nodes, mean node degree 43, and diameter 3.

---
## Contributors
* Jordan Williams ([@TheAfroOfDoom](https://github.com/theafroofdoom))
* Alana McGraw
* Aidan Tokarski ([@aidant19](https://github.com/aidant19))