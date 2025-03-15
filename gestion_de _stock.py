import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
import csv

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="store"
)
cursor = conn.cursor()

# Création des tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price INT NOT NULL,
    quantity INT NOT NULL,
    id_category INT,
    FOREIGN KEY (id_category) REFERENCES category(id) ON DELETE CASCADE
)
""")
conn.commit()

# Interface graphique
class StockManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")
        
        self.tree = ttk.Treeview(root, columns=("ID", "Nom", "Description", "Prix", "Quantité", "Catégorie"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Quantité", text="Quantité")
        self.tree.heading("Catégorie", text="Catégorie")
        self.tree.pack()
        
        self.load_data()
        
        self.btn_add = tk.Button(root, text="Ajouter Produit", command=self.add_product)
        self.btn_add.pack()
        
        self.btn_delete = tk.Button(root, text="Supprimer Produit", command=self.delete_product)
        self.btn_delete.pack()
        
        self.btn_export = tk.Button(root, text="Exporter CSV", command=self.export_csv)
        self.btn_export.pack()
        
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        cursor.execute("""
        SELECT product.id, product.name, product.description, product.price, product.quantity, category.name
        FROM product
        LEFT JOIN category ON product.id_category = category.id
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
    
    def add_product(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Ajouter un Produit")
        tk.Label(new_window, text="Nom").grid(row=0, column=0)
        entry_name = tk.Entry(new_window)
        entry_name.grid(row=0, column=1)
        
        tk.Label(new_window, text="Description").grid(row=1, column=0)
        entry_description = tk.Entry(new_window)
        entry_description.grid(row=1, column=1)
        
        tk.Label(new_window, text="Prix").grid(row=2, column=0)
        entry_price = tk.Entry(new_window)
        entry_price.grid(row=2, column=1)
        
        tk.Label(new_window, text="Quantité").grid(row=3, column=0)
        entry_quantity = tk.Entry(new_window)
        entry_quantity.grid(row=3, column=1)
        
        tk.Label(new_window, text="Catégorie").grid(row=4, column=0)
        cursor.execute("SELECT id, name FROM category")
        categories = cursor.fetchall()
        category_dict = {str(cat[1]): cat[0] for cat in categories}
        category_names = list(category_dict.keys())
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(new_window, textvariable=category_var, values=category_names)
        category_dropdown.grid(row=4, column=1)
        
        def save_product():
            name = entry_name.get()
            description = entry_description.get()
            price = entry_price.get()
            quantity = entry_quantity.get()
            category_name = category_var.get()
            id_category = category_dict.get(category_name, None)
            
            cursor.execute("INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)",
                           (name, description, price, quantity, id_category))
            conn.commit()
            self.load_data()
            new_window.destroy()
        
        tk.Button(new_window, text="Sauvegarder", command=save_product).grid(row=5, column=1)
    
    def delete_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            product_id = item["values"][0]
            cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            conn.commit()
            self.load_data()
        else:
            messagebox.showwarning("Alerte", "Veuillez sélectionner un produit à supprimer")
    
    def export_csv(self):
        with open("stock.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nom", "Description", "Prix", "Quantité", "Catégorie"])
            cursor.execute("""
            SELECT product.id, product.name, product.description, product.price, product.quantity, category.name
            FROM product
            LEFT JOIN category ON product.id_category = category.id
            """)
            writer.writerows(cursor.fetchall())
        messagebox.showinfo("Succès", "Exportation réussie")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockManager(root)
    root.mainloop()

# Fermeture de la connexion
def close_connection():
    cursor.close()
    conn.close()

root.protocol("WM_DELETE_WINDOW", close_connection)