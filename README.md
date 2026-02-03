# CPSC-481---Final-project
CPSC 481 - Project Proposal
Project Title: 2x2x2 Rubik’s Cube Solver
Proposal Date: 1/6/2026

Introduction
Members:
Johnson Tran
Jasper Liong
Haley Patel
Daniel Chen
Howard Wu

Objective and Scope
The objective of this project is to create an agent that uses artificial intelligence algorithms to solve a 2x2x2 Rubik’s Cube. We will use the A*, IDS, and BFS algorithms to solve a given Rubik’s Cube. Each algorithm will output a set of moves in the order it was produced to show how it got to the solution. There will be a graphical user interface (GUI) that the user can navigate to visually see the differences between all three algorithms including a list of moves used to get to the solution and the computation time of each algorithm. We also plan to implement an animation that shows how to solve the cube given an algorithm’s output.

Roles and Responsibilities
- Jasper: Developer Implementation and Algorithm Implementation
- Johnson: Animator GUI implementation for Rubik’s Cube animation
- Daniel: Renderer GUI implementation for Rubik’s Cube representation
- Haley: User interface and Experience GUI UI/UX implementation
- Howard: Developer Algorithm Implementation for comparison

## Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/JohnsonT-cs/CPSC-481---Final-project.git
   cd CPSC-481---Final-project
   ```
2. **Install dependencies**
   On Linux/macOS:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
   On Windows:
   ```bash
   py -m pip install -r requirements.txt
   ```
3. **Run the Program**
   - Run gui_2x2.py to start program
