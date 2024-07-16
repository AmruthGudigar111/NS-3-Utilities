import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import sys

# Function to parse NS-3 config file
def parse_ns3_config(file_path):
    nodes = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        node_id = 1
        for line in lines:
            match = re.search(r'positionAlloc->Add\(Vector\((\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*)\)\);', line)
            if match:
                x, y, z = match.groups()
                node_name = f'N{node_id}'
                nodes[node_name] = (float(x), float(y))
                node_id += 1

    return nodes

# Function to draw network topology
def draw_topology(nodes):
    fig, ax = plt.subplots()
    for node, pos in nodes.items():
        ax.plot(pos[0], pos[1], 'o', markersize=10)  # Adjust markersize as needed
        ax.text(pos[0], pos[1], f'{node}\n({pos[0]}, {pos[1]})', verticalalignment='bottom', horizontalalignment='left', fontweight='bold')

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    #ax.grid(True)

    # Set Arial as the default font
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = '10'

    # Invert the axes
    #ax.invert_xaxis()
    ax.invert_yaxis()

    # Removing top and right borders of the plot grid
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Adjusting grid lines
    plt.grid(True, linestyle='--', color='lightgrey')

    # Moving ticks inside the plot
    plt.tick_params(axis='x', which='both', direction='in')
    plt.tick_params(axis='y', which='both', direction='in')

    return fig

# Function to open file dialog and load NS-3 config file
def load_config():
    file_path = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch", title="Select NS-3 Config File", filetypes=[("Config Files", "*.cc")])
    if file_path:
        nodes = parse_ns3_config(file_path)
        fig = draw_topology(nodes)
        global canvas
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Function to save the plot as an image
def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        fig = canvas.figure
        fig.savefig(file_path)

# Function to handle window close event
def on_closing():
    window.destroy()
    sys.exit()

# Create main window
window = tk.Tk()
window.title("NS-3 Network Topology Viewer")
window.geometry("800x600")

# Bind the close event to the on_closing function
window.protocol("WM_DELETE_WINDOW", on_closing)

# Create load button
load_button = tk.Button(window, text="Load NS-3 Config File", command=load_config)
load_button.pack()

# Create save button
save_button = tk.Button(window, text="Save Image", command=save_image)
save_button.pack()

# Start the Tkinter main loop
window.mainloop()