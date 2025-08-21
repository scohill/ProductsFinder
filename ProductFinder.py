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
        
        self.base_products = [
            "ALL",
            "ogkush",
            "sourdiesel",
            "greencrack",
            "granddaddypurple",
            "meth",
            "cocaine"
        ]
        
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
        
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#333")
        style.configure("TLabel", padding=6, font=('Helvetica', 10))
        style.configure("TEntry", padding=6)
        
        self.json_file_path = StringVar()
        self.base_product = StringVar(value=self.base_products[0])
        self.sort_method = StringVar(value="Default")
        self.mix_recipes = None
        self.product_prices = {}
        self.product_properties = {}
        self.current_chains = []
        self.current_bubble = None
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        recipe_frame = ttk.Frame(file_frame)
        recipe_frame.grid(row=0, column=0, sticky=(W, E), pady=2)
        
        self.file_label = ttk.Label(recipe_frame, text="No recipe file selected", wraplength=300)
        self.file_label.grid(row=0, column=0, sticky=W)
        ttk.Button(recipe_frame, text="Select Recipe File", 
                  command=self.select_file).grid(row=0, column=1, padx=5)
        
        prop_frame = ttk.Frame(main_frame)
        prop_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        self.properties_enabled = BooleanVar(value=True)
        self.toggle_button = ttk.Checkbutton(prop_frame, 
                                           text="Enable Properties", 
                                           variable=self.properties_enabled)
        self.toggle_button.grid(row=0, column=0, padx=5)
        
        self.prop_dir_label = ttk.Label(prop_frame, text="No properties directory selected", 
                                      wraplength=300)
        self.prop_dir_label.grid(row=0, column=1, sticky=W)
        ttk.Button(prop_frame, text="Select Properties Directory", 
                  command=self.select_properties_dir).grid(row=0, column=2, padx=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        ttk.Label(input_frame, text="Select base product:").grid(row=0, column=0, sticky=W)
        
        product_dropdown = ttk.Combobox(input_frame, 
                                      textvariable=self.base_product,
                                      values=self.base_products,
                                      state="readonly",
                                      width=20)
        product_dropdown.grid(row=0, column=1, sticky=(W, E), padx=5)
        
        ttk.Button(input_frame, text="Find Chains", command=self.find_chains).grid(row=0, column=2, padx=5)
        
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
        
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=4, column=0, columnspan=2, sticky=(W, E), pady=5)
        
        ttk.Button(export_frame, text="Export Results", 
                  command=self.export_results).grid(row=0, column=0, padx=5)
        ttk.Button(export_frame, text="Import Results", 
                  command=self.import_results).grid(row=0, column=1, padx=5)
        
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=5, column=0, columnspan=2, sticky=(N, W, E, S), pady=5)
        
        self.result_text = Text(result_frame, wrap=WORD, width=80, height=20, 
                              font=('Courier', 11),
                              cursor="hand2")
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.tag_configure("plus", foreground="green")
        self.result_text.tag_configure("equals", foreground="red")
        self.result_text.tag_configure("price", foreground="green")
        self.result_text.tag_configure("cost", foreground="red")
        self.result_text.tag_configure("highlight", background="lightblue")
        self.result_text.tag_configure("clickable", underline=True)
        
        self.result_text.bind("<Button-1>", self.highlight_line)
        
        self.result_text.grid(row=0, column=0, sticky=(N, W, E, S))
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
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
        dir_path = filedialog.askdirectory(title="Select Properties Directory")
        if dir_path:
            self.prop_dir_label.config(text=f"Selected: {dir_path}")
            self.load_properties(dir_path)

    def load_properties(self, directory):
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
                        continue
        except Exception as e:
            if directory != "CreatedProducts":
                messagebox.showerror("Error", f"Error loading prop
