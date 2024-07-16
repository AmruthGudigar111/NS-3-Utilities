import tkinter as tk
from tkinter import ttk, filedialog
from collections import defaultdict

# Function to load and parse the log file
def load_file(filename, progress_var):
    progress_var.set(0)  # Reset progress bar
    with open(filename, 'r') as file:
        lines = file.readlines()

    progress_var.set(100)  # Update progress bar to indicate completion
    return lines

# Function to extract the details from the log data
def extract_details(lines):
    details = []
    current_time = ""
    current_flow = {}
    end_to_end_throughput = ""

    for line in lines:
        line = line.strip()
        if line.startswith("Time:"):
            if current_flow:
                if end_to_end_throughput:
                    current_flow["End-to-End Throughput"] = end_to_end_throughput
                details.append(current_flow)
            current_time = line.split(":")[1].strip()
            current_flow = {"Time": current_time}
        elif line.startswith("FlowID:"):
            if "FlowID" in current_flow:
                if end_to_end_throughput:
                    current_flow["End-to-End Throughput"] = end_to_end_throughput
                details.append(current_flow)
            parts = line.split()
            flow_id = parts[1]
            protocol_info = " ".join(parts[2:])
            protocol, src_dest = protocol_info.split(" ", 1)
            src, dest = src_dest.split(" --> ")
            current_flow = {
                "Time": current_time,
                "FlowID": flow_id,
                "Protocol": protocol,
                "Source IP/Src Port": src,
                "Destination IP/Dst Port": dest
            }
        elif line.startswith("Tx Bytes:"):
            current_flow["Tx Bytes"] = line.split(":")[1].strip()
        elif line.startswith("Rx Bytes:"):
            current_flow["Rx Bytes"] = line.split(":")[1].strip()
        elif line.startswith("Tx Packets:"):
            current_flow["Tx Packets"] = line.split(":")[1].strip()
        elif line.startswith("Rx Packets:"):
            current_flow["Rx Packets"] = line.split(":")[1].strip()
        elif line.startswith("Lost Packets:"):
            current_flow["Lost Packets"] = line.split(":")[1].strip()
        elif line.startswith("Pkt Lost Ratio:"):
            current_flow["Pkt Lost Ratio"] = line.split(":")[1].strip()
        elif line.startswith("Mean{Delay}:"):
            current_flow["Mean{Delay}"] = line.split(":")[1].strip()
        elif line.startswith("Mean{Jitter}:"):
            current_flow["Mean{Jitter}"] = line.split(":")[1].strip()
        elif line.startswith("Throughput:"):
            current_flow["Throughput"] = line.split(":")[1].strip()
        elif line.startswith("End-to-End Throughput:"):
            end_to_end_throughput = line.split(":")[1].strip()
            current_flow["End-to-End Throughput"] = end_to_end_throughput

    if current_flow:
        if end_to_end_throughput:
            current_flow["End-to-End Throughput"] = end_to_end_throughput
        details.append(current_flow)

    return details

# Function to handle file selection
def browse_file():
    filename = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filename:
        progress_var.set(0)  # Reset progress bar
        lines = load_file(filename, progress_var)
        display_details(lines)

# Function to display details in table format
def display_details(lines):
    global details
    details = extract_details(lines)

    # Clear existing table
    for row in details_tree.get_children():
        details_tree.delete(row)

    # Insert new data into table
    for detail in details:
        values = {}
        for col in columns:
            values[col] = detail.get(col, "N/A")
        details_tree.insert("", tk.END, values=list(values.values()))

    # Create filter options after loading details
    create_filters()

# Function to create filter menus for each column
def create_filters():
    global filter_menus
    global columns

    # Remove existing filters
    for widget in filter_frame.winfo_children():
        widget.destroy()

    # Create filter menus dynamically based on column headers
    for col_index, col in enumerate(columns):
        values = set()
        for detail in details:
            values.add(detail.get(col, "N/A"))

        # Create label for the filter
        filter_label = ttk.Label(filter_frame, text=col, style='Arial.TLabel')
        filter_label.grid(row=0, column=col_index, padx=5, pady=5)

        # Create combobox for the filter
        filter_menus[col] = ttk.Combobox(filter_frame, values=['All'] + list(values), width=11)  # Adjust width as needed
        filter_menus[col].bind("<<ComboboxSelected>>", apply_filters)
        filter_menus[col].current(0)  # Set default to 'All'
        filter_menus[col].grid(row=1, column=col_index, padx=5, pady=5)

# Function to apply filters based on selected values
def apply_filters(event=None):
    filters = {}
    for col, combobox in filter_menus.items():
        value = combobox.get()
        if value and value != 'All':
            filters[col] = value

    # Clear existing table
    for row in details_tree.get_children():
        details_tree.delete(row)

    # Filter and display data
    for detail in details:
        include = True
        for col, value in filters.items():
            if detail.get(col, "N/A") != value:
                include = False
                break
        if include:
            values = [detail.get(col, "N/A") for col in columns]
            details_tree.insert("", tk.END, values=values)

# GUI setup
root = tk.Tk()
root.title("Flow Monitor txt Analyzer by Amruth")

# Set Arial font with font size 10 for all widgets
style = ttk.Style()
style.configure('Arial.TButton', font=('Arial', 10))
style.configure('Arial.TLabel', font=('Arial', 10))
style.configure('Arial.TEntry', font=('Arial', 10))
style.configure('Arial.Treeview', font=('Arial', 10))

# Progress bar to indicate file reading progress
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, mode="determinate", variable=progress_var)
progress_bar.pack(fill="x", padx=10, pady=10)

# Label to browse for log file
browse_label = ttk.Label(root, text="Browse the Instantaneous_Flow_Log.txt file:", style='Arial.TLabel')
browse_label.pack(pady=5)

# Browse button to select log file
browse_button = ttk.Button(root, text="Browse", command=browse_file, style='Arial.TButton')
browse_button.pack(pady=5)

# Frame to contain filter options
filter_frame = ttk.Frame(root)
filter_frame.pack(padx=10, pady=10, fill="x")

# Frame to contain the Treeview and Scrollbars
frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Define the columns for the Treeview
columns = ("Time", "FlowID", "Protocol", "Source IP/Src Port", "Destination IP/Dst Port",
           "Tx Bytes", "Rx Bytes", "Tx Packets", "Rx Packets", "Lost Packets",
           "Pkt Lost Ratio", "Mean{Delay}", "Mean{Jitter}", "Throughput", "End-to-End Throughput")

# Treeview (table) to display details
details_tree = ttk.Treeview(frame, columns=columns, show="headings", style='Arial.Treeview')

# Configure column headings
for col in columns:
    details_tree.heading(col, text=col, command=lambda c=col: sort_treeview(details_tree, c, False))
    details_tree.column(col, anchor="center")

# Vertical Scrollbar
vsb = ttk.Scrollbar(frame, orient="vertical", command=details_tree.yview)
details_tree.configure(yscrollcommand=vsb.set)
vsb.pack(side='right', fill='y')

# Horizontal Scrollbar
hsb = ttk.Scrollbar(frame, orient="horizontal", command=details_tree.xview)
details_tree.configure(xscrollcommand=hsb.set)
hsb.pack(side='bottom', fill='x')

# Pack the Treeview widget
details_tree.pack(fill="both", expand=True)

# Dictionary to hold filter comboboxes
filter_menus = {}

root.mainloop()
