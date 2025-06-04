from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='Final Simulation Frame Workflow (Correct Reverse Handling and Layout)')

# Define nodes
dot.node('P', 'Reset to Initial Position\nBegin Reverse Stepping', shape='box')  # <-- moved up
dot.node('A', 'Start:\nLoad Initial Position')
dot.node('B', 'Check if Initial Mechanism\nConfiguration is Feasible', shape='diamond')
dot.node('C', 'Search for Closest Feasible\nInitial Position', shape='box')
dot.node('D', 'Set Initial Dependent Variable Guess', shape='parallelogram')
dot.node('F', 'Store Frame Data', shape='parallelogram')
dot.node('G', 'Update Inputs\n(Position, Velocity, Variable Guess Update)', shape='box')
dot.node('I', 'Compute Frame Image', shape='box')
dot.node('J', 'Is New Frame Feasible?', shape='diamond')
dot.node('H', 'Reverse Stepping?', shape='diamond')
dot.node('Q', 'Merge Forward and Reverse Frames', shape='box')
dot.node('R', 'Check Simulation Time\nTermination Criteria', shape='diamond')
dot.node('T', 'Simulation Complete')

# Define edges
dot.edge('A', 'B')
dot.edge('B', 'D', label='Feasible')
dot.edge('B', 'C', label='Not Feasible')
dot.edge('C', 'D')
dot.edge('D', 'F')

dot.edge('J', 'H', label='Reverse Stepping Check')
dot.edge('H', 'Q', label='Yes')
dot.edge('Q', 'T', label='Simulation Complete')

# Forward pass
dot.edge('H', 'P', label='No')  # <-- direct to reset immediately
dot.edge('P', 'F')
dot.edge('F', 'G')
dot.edge('G', 'R')
dot.edge('R', 'I', label='Total Runtime Not Reached')
dot.edge('R', 'T', label='Total Runtime Reached')
dot.edge('I', 'J')
dot.edge('J', 'F', label='Feasible')

# If becomes not feasible


# Render the graph
dot.render('simulation_frame_workflow_corrected', format='png', view=True)

# Display the graph object
print(dot.source)

