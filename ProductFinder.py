import json
import sys
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from collections import defaultdict

class ProductFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Chain Finder")
        self.root.geometry("800x600")
        
        # Predefined base products with ALL option
        self.base_products = [
            "ALL",
            "ogkush",
            "sourdiesel",
            "greencrack",
            "granddaddypurple",
            "meth",
            "cocaine"
        ]
        
        # Ingredient costs dictionary
        self.ingredient_costs = {
            "cuke": 2,
            "banana": 2,
            "paracetamol": 3,
            "donut": 3,
            "viagra": 4,
            "mouthwash": 4,
            "flumedicine": 5,
            "gasoline": 5,
            "energydrink": 6,
            "motoroil": 6,
            "megabean": 7,
            "chili": 7,
            "battery": 8,
            "iodine": 8,
            "addy": 9,
            "horsesemen": 9
        }
        
        # Style configuration
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#333")
        style.configure("TLabel", padding=6, font=('Helvetica', 10))
        style.configure("TEntry", padding=6)
        
        # Variables
        self.json_file_path = StringVar()
        self.base_product = StringVar(value=self.base_products[0])
        self.sort_method = StringVar(value="Default")
        self.mix_recipes = None
        self.product_prices = {}
        self.product_properties = {}
        self.current_chains = []
        self.current_bubble = None
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        # File selection frame
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        # Recipe file selection
        recipe_frame = ttk.Frame(file_frame)
        recipe_frame.grid(row=0, column=0, sticky=(W, E), pady=2)
        
        self.file_label = ttk.Label(recipe_frame, text="No recipe file selected", wraplength=300)
        self.file_label.grid(row=0, column=0, sticky=W)
        ttk.Button(recipe_frame, text="Select Recipe File", 
                  command=self.select_file).grid(row=0, column=1, padx=5)
        
        # Properties toggle and directory selection
        prop_frame = ttk.Frame(main_frame)
        prop_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        # Properties toggle button
        self.properties_enabled = BooleanVar(value=True)
        self.toggle_button = ttk.Checkbutton(prop_frame, 
                                           text="Enable Properties", 
                                           variable=self.properties_enabled)
        self.toggle_button.grid(row=0, column=0, padx=5)
        
        # Properties directory selection
        self.prop_dir_label = ttk.Label(prop_frame, text="No properties directory selected", 
                                      wraplength=300)
        self.prop_dir_label.grid(row=0, column=1, sticky=W)
        ttk.Button(prop_frame, text="Select Properties Directory", 
                  command=self.select_properties_dir).grid(row=0, column=2, padx=5)
        
        # Product input and controls
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        ttk.Label(input_frame, text="Select base product:").grid(row=0, column=0, sticky=W)
        
        # Product dropdown
        product_dropdown = ttk.Combobox(input_frame, 
                                      textvariable=self.base_product,
                                      values=self.base_products,
                                      state="readonly",
                                      width=20)
        product_dropdown.grid(row=0, column=1, sticky=(W, E), padx=5)
        
        ttk.Button(input_frame, text="Find Chains", command=self.find_chains).grid(row=0, column=2, padx=5)
        
        # Sorting options
        sort_frame = ttk.Frame(main_frame)
        sort_frame.grid(row=3, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        ttk.Label(sort_frame, text="Sort by:").grid(row=0, column=0, sticky=W)
        sort_options = ttk.Combobox(sort_frame, 
                                  textvariable=self.sort_method, 
                                  values=["Default", "Shortest First", "Longest First", 
                                         "Price (Low to High)", "Price (High to Low)",
                                         "Cost (Low to High)", "Cost (High to Low)"],
                                  state="readonly",
                                  width=15)
        sort_options.grid(row=0, column=1, sticky=W, padx=5)
        sort_options.bind('<<ComboboxSelected>>', self.resort_chains)
        
        # Export/Import buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=4, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        ttk.Button(export_frame, text="Export Results", 
                  command=self.export_results).grid(row=0, column=0, padx=5)
        ttk.Button(export_frame, text="Import Results", 
                  command=self.import_results).grid(row=0, column=1, padx=5)
        
        # Results area
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=5, column=0, columnspan=2, sticky=(N, W, E, S), pady=5)
        
        # Create text widget and scrollbar
        self.result_text = Text(result_frame, wrap=WORD, width=80, height=20, 
                              font=('Courier', 11),
                              cursor="hand2")
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure text tags for colored operators and prices
        self.result_text.tag_configure("plus", foreground="green")
        self.result_text.tag_configure("equals", foreground="red")
        self.result_text.tag_configure("price", foreground="green")
        self.result_text.tag_configure("cost", foreground="red")
        self.result_text.tag_configure("highlight", background="lightblue")
        self.result_text.tag_configure("clickable", underline=True)
        
        # Bind click event for highlighting
        self.result_text.bind("<Button-1>", self.highlight_line)
        
        # Grid text widget and scrollbar
        self.result_text.grid(row=0, column=0, sticky=(N, W, E, S))
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # Try to load default properties directory without showing error
        try:
            if os.path.exists("CreatedProducts"):
                self.load_properties("CreatedProducts")
                self.prop_dir_label.config(text="Using: CreatedProducts")
        except:
            pass

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.json_file_path.set(file_path)
            self.file_label.config(text=f"Selected: {file_path}")
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    self.mix_recipes = data.get("MixRecipes", [])
                    prices_list = data.get("ProductPrices", [])
                    self.product_prices = {item["String"]: item["Int"] for item in prices_list}
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
                self.mix_recipes = None
                self.product_prices = {}

    def select_properties_dir(self):
        """Handle properties directory selection"""
        dir_path = filedialog.askdirectory(title="Select Properties Directory")
        if dir_path:
            self.prop_dir_label.config(text=f"Selected: {dir_path}")
            self.load_properties(dir_path)

    def load_properties(self, directory):
        """Load properties from all JSON files in the directory"""
        self.product_properties = {}
        
        try:
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(directory, filename)
                    try:
                        with open(filepath, 'r') as file:
                            data = json.load(file)
                            product_name = os.path.splitext(filename)[0]
                            if "Properties" in data:
                                self.product_properties[product_name] = data["Properties"]
                    except:
                        continue  # Skip files that can't be loaded
        except Exception as e:
            # Only show error if user explicitly selected the directory
            if directory != "CreatedProducts":
                messagebox.showerror("Error", f"Error loading properties: {str(e)}")

    def create_bubble(self, product, x, y):
        """Create a bubble-style popup for properties with close button"""
        # Only create bubble if properties are enabled and we have properties to show
        if not self.properties_enabled.get() or not self.product_properties or product not in self.product_properties:
            return
            
        # Destroy existing bubble if it exists
        if self.current_bubble:
            self.current_bubble.destroy()
            
        # Create new bubble
        bubble = Toplevel(self.root)
        bubble.overrideredirect(True)  # Remove window decorations
        
        # Create main frame with border and background
        frame = Frame(bubble, bg='lightyellow', bd=1, relief='solid')
        frame.pack(fill=BOTH, expand=True)
        
        # Create header frame for title and close button
        header_frame = Frame(frame, bg='lightyellow')
        header_frame.pack(fill=X, padx=5, pady=(5,0))
        
        # Title
        title = Label(header_frame, text=f"Properties: {product}", 
                     bg='lightyellow', font=('Courier', 11, 'bold'))
        title.pack(side=LEFT, padx=(5,0))
        
        # Close button
        close_button = Label(header_frame, text="×", bg='lightyellow',
                           font=('Arial', 12, 'bold'), cursor='hand2')
        close_button.pack(side=RIGHT, padx=(5,0))
        close_button.bind('<Button-1>', lambda e: bubble.destroy())
        
        # Change color on hover
        def on_enter(e):
            close_button['fg'] = 'red'
        def on_leave(e):
            close_button['fg'] = 'black'
            
        close_button.bind('<Enter>', on_enter)
        close_button.bind('<Leave>', on_leave)
        
        # Add properties with bullet points
        if product in self.product_properties:
            properties = self.product_properties[product]
            
            # Properties container
            prop_frame = Frame(frame, bg='lightyellow')
            prop_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
            
            # Properties
            for prop in properties:
                prop_label = Label(prop_frame, text=f"• {prop}", 
                                 bg='lightyellow', font=('Courier', 11))
                prop_label.pack(anchor='w')
            
            # Position the bubble near the cursor but not under it
            bubble.update_idletasks()
            bubble_width = bubble.winfo_width()
            bubble_height = bubble.winfo_height()
            
            # Adjust position to keep bubble on screen
            screen_width = bubble.winfo_screenwidth()
            screen_height = bubble.winfo_screenheight()
            
            # Calculate position
            bubble_x = min(x + 10, screen_width - bubble_width)
            bubble_y = min(y + 10, screen_height - bubble_height)
            
            bubble.geometry(f"+{bubble_x}+{bubble_y}")
            
            # Store reference to current bubble
            self.current_bubble = bubble

    def highlight_line(self, event):
        # Remove previous highlight
        self.result_text.tag_remove("highlight", "1.0", END)
        
        # Get clicked line
        index = self.result_text.index(f"@{event.x},{event.y}")
        line_start = self.result_text.index(f"{index} linestart")
        line_end = self.result_text.index(f"{index} lineend")
        
        # Add highlight to clicked line
        self.result_text.tag_add("highlight", line_start, line_end)
        
        # Get the clicked line's text and extract the output product
        line = self.result_text.get(line_start, line_end)
        if "=" in line:
            output_product = line.split(" = ")[1].split(" ----")[0].strip()
            # Get mouse position for bubble placement
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            self.create_bubble(output_product, x, y)

    def get_chain_price(self, chain):
        """Get the price for a chain's output product"""
        if "=" not in chain:
            return 0
        output_product = chain.split(" = ")[1].strip()
        return self.product_prices.get(output_product, 0)

    def get_chain_cost(self, chain):
        """Calculate the total cost of ingredients in a chain"""
        if "+" not in chain:
            return 0
            
        parts = chain.split(" = ")[0].split(" + ")[1:]  # Skip the first part (base product)
        total_cost = sum(self.ingredient_costs.get(ingredient.strip(), 0) for ingredient in parts)
        return total_cost

    def sort_chains(self, chains):
        sort_method = self.sort_method.get()
        
        # Don't sort empty strings (used as separators in ALL view)
        chains_to_sort = [chain for chain in chains if chain]
        
        if sort_method == "Default":
            return chains
            
        if sort_method in ["Price (Low to High)", "Price (High to Low)"]:
            chain_tuples = [(self.get_chain_price(chain), chain) for chain in chains_to_sort]
            reverse = (sort_method == "Price (High to Low)")
            chain_tuples.sort(key=lambda x: (x[0], x[1]), reverse=reverse)
        elif sort_method in ["Cost (Low to High)", "Cost (High to Low)"]:
            chain_tuples = [(self.get_chain_cost(chain), chain) for chain in chains_to_sort]
            reverse = (sort_method == "Cost (High to Low)")
            chain_tuples.sort(key=lambda x: (x[0], x[1]), reverse=reverse)
        else:
            chain_tuples = [(len(chain.split("+")), chain) for chain in chains_to_sort]
            if sort_method == "Longest First":
                chain_tuples.sort(key=lambda x: (-x[0], x[1]))
            else:  # "Shortest First"
                chain_tuples.sort(key=lambda x: (x[0], x[1]))
            
        return [chain[1] for chain in chain_tuples]

    def resort_chains(self, event=None):
        if self.current_chains:
            sorted_chains = self.sort_chains(self.current_chains)
            self.display_chains(sorted_chains)

    def export_results(self):
        """Export current results to a text file"""
        if not self.current_chains:
            messagebox.showwarning("Warning", "No results to export!")
            return
            
        try:
            # Get file name for saving
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Results"
            )
            
            if not file_path:  # If user cancels
                return
                
            with open(file_path, 'w', encoding='utf-8') as file:
                # Write header
                if self.base_product.get() == "ALL":
                    file.write("Chains for all products:\n\n")
                else:
                    file.write(f"Chains starting from {self.base_product.get()}:\n\n")
                
                # Write chains
                for chain in self.current_chains:
                    if not chain:  # Empty separator line
                        file.write("\n")
                        continue
                        
                    # Split chain to get output product and write with prices
                    parts = chain.split(" = ")
                    base_part = parts[0]
                    output_product = parts[1].strip()
                    
                    # Write base chain
                    file.write(f"{base_part} = {output_product}")
                    
                    # Add price and cost if available
                    if output_product in self.product_prices:
                        price = self.product_prices[output_product]
                        cost = self.get_chain_cost(chain)
                        file.write(f" ---- Sell Price: {price} | Cost: {cost}")
                    
                    file.write("\n")
                    
            messagebox.showinfo("Success", "Results exported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting results: {str(e)}")

    def import_results(self):
        """Import results from a text file"""
        try:
            # Get file to import
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Import Results"
            )
            
            if not file_path:  # If user cancels
                return
                
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Display imported content
            self.result_text.delete(1.0, END)
            
            # Process the content line by line to apply colors
            lines = content.split('\n')
            for line in lines:
                if not line.strip():
                    self.result_text.insert(END, "\n")
                    continue
                    
                if ":" in line and "Chains" in line:  # Header line
                    self.result_text.insert(END, line + "\n\n")
                    continue
                    
                # Process chain line
                if " = " in line:
                    parts = line.split(" + ")
                    self.result_text.insert(END, parts[0])
                    
                    for part in parts[1:]:
                        if "=" in part:
                            final_parts = part.split(" = ")
                            self.result_text.insert(END, " ")
                            self.result_text.insert(END, "+", "plus")
                            self.result_text.insert(END, f" {final_parts[0]} ")
                            self.result_text.insert(END, "=", "equals")
                            
                            # Handle output product and prices
                            if "----" in final_parts[1]:
                                product_price_parts = final_parts[1].split(" ---- ")
                                self.result_text.insert(END, f" {product_price_parts[0]}")
                                
                                # Handle price and cost
                                if len(product_price_parts) > 1:
                                    self.result_text.insert(END, " ---- ")
                                    price_cost_parts = product_price_parts[1].split(" | ")
                                    self.result_text.insert(END, price_cost_parts[0], "price")
                                    if len(price_cost_parts) > 1:
                                        self.result_text.insert(END, " | ")
                                        self.result_text.insert(END, price_cost_parts[1], "cost")
                            else:
                                self.result_text.insert(END, f" {final_parts[1]}")
                        else:
                            self.result_text.insert(END, " ")
                            self.result_text.insert(END, "+", "plus")
                            self.result_text.insert(END, f" {part}")
                    
                    self.result_text.insert(END, "\n")
                else:
                    self.result_text.insert(END, line + "\n")
            
            messagebox.showinfo("Success", "Results imported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error importing results: {str(e)}")

    def display_chains(self, chains):
        self.result_text.delete(1.0, END)
        if chains:
            if self.base_product.get() == "ALL":
                self.result_text.insert(END, "Chains for all products:\n\n")
            else:
                self.result_text.insert(END, f"Chains starting from {self.base_product.get()}:\n\n")
                
            for chain in chains:
                if not chain:
                    self.result_text.insert(END, "\n")
                    continue
                    
                parts = chain.split(" + ")
                self.result_text.insert(END, parts[0])
                
                for part in parts[1:]:
                    if "=" in part:
                        final_parts = part.split(" = ")
                        self.result_text.insert(END, " ")
                        self.result_text.insert(END, "+", "plus")
                        self.result_text.insert(END, f" {final_parts[0]} ")
                        self.result_text.insert(END, "=", "equals")
                        
                        # Make the output product clickable
                        output_product = final_parts[1].strip()
                        self.result_text.insert(END, " ")
                        if output_product in self.product_properties:
                            self.result_text.insert(END, output_product, "clickable")
                        else:
                            self.result_text.insert(END, output_product)
                        
                        if output_product in self.product_prices:
                            self.result_text.insert(END, " ---- ")
                            self.result_text.insert(END, f"Sell Price: {self.product_prices[output_product]}", "price")
                            self.result_text.insert(END, " | ")
                            self.result_text.insert(END, f"Cost: {self.get_chain_cost(chain)}", "cost")
                    else:
                        self.result_text.insert(END, " ")
                        self.result_text.insert(END, "+", "plus")
                        self.result_text.insert(END, f" {part}")
                
                self.result_text.insert(END, "\n")
        else:
            self.result_text.insert(END, "No chains found")

    def build_recipe_chains(self, base_product, max_depth=15):
        def find_next_recipes(current_value, visited, depth=0):
            if depth >= max_depth or current_value in visited:
                return []
                
            chains = []
            visited.add(current_value)
            
            for recipe in self.mix_recipes:
                if recipe["Product"] == current_value:
                    new_chain = [(current_value, recipe["Mixer"], recipe["Output"])]
                    chains.append(new_chain)
                    next_chains = find_next_recipes(recipe["Output"], visited.copy(), depth + 1)
                    for next_chain in next_chains:
                        chains.append(new_chain + next_chain)
                        
                if recipe["Mixer"] == current_value:
                    new_chain = [(recipe["Product"], current_value, recipe["Output"])]
                    chains.append(new_chain)
                    next_chains = find_next_recipes(recipe["Output"], visited.copy(), depth + 1)
                    for next_chain in next_chains:
                        chains.append(new_chain + next_chain)
                        
            return chains

        all_chains = find_next_recipes(base_product, set())
        formatted_chains = []
        seen = set()
        
        for chain in all_chains:
            if not chain:
                continue
                
            elements = []
            current = base_product
            
            for product, mixer, output in chain:
                if product == current:
                    elements.append(mixer)
                elif mixer == current:
                    elements.append(product)
                current = output
            
            formatted = f"{base_product} + {' + '.join(elements)} = {chain[-1][2]}"
            if formatted not in seen:
                formatted_chains.append(formatted)
                seen.add(formatted)
        
        return formatted_chains

    def find_chains(self):
        if not self.mix_recipes:
            try:
                with open('Products.json', 'r') as file:
                    data = json.load(file)
                    self.mix_recipes = data.get("MixRecipes", [])
                    prices_list = data.get("ProductPrices", [])
                    self.product_prices = {item["String"]: item["Int"] for item in prices_list}
                    self.file_label.config(text="Using: Products.json")
            except Exception as e:
                messagebox.showerror("Error", "Please select a valid JSON file or ensure Products.json exists in the current directory")
                return
        
        try:
            if self.base_product.get() == "ALL":
                all_chains = []
                for product in self.base_products[1:]:  # Skip "ALL" option
                    product_chains = self.build_recipe_chains(product)
                    if product_chains:
                        all_chains.extend(product_chains)
                        all_chains.append("")
                
                if all_chains and all_chains[-1] == "":
                    all_chains.pop()
                    
                self.current_chains = all_chains
            else:
                self.current_chains = self.build_recipe_chains(self.base_product.get())
            
            sorted_chains = self.sort_chains(self.current_chains)
            self.display_chains(sorted_chains)
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            raise

def main():
    root = Tk()
    app = ProductFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()