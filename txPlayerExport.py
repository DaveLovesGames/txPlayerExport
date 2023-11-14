import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import csv
from datetime import datetime

class PlayerDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Data Filter")

        # Initialize an empty list to store player data
        self.players_data = []

        # Set up the frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        # Set up the frame for the treeview
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Add the 'Upload JSON' button
        self.upload_button = tk.Button(button_frame, text="Upload JSON", command=self.load_json)
        self.upload_button.pack(side=tk.LEFT, padx=10)

        # Add the 'Export to CSV' button
        self.export_button = tk.Button(button_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(side=tk.RIGHT, padx=10)

        # Set up the Treeview to display the data
        self.tree = ttk.Treeview(self.tree_frame, columns=('playername', 'discordID', 'lastConnectionDate'), show='headings')
        self.tree.heading('playername', text='Player Name', command=lambda: self.treeview_sort_column(self.tree, 'playername', False))
        self.tree.heading('discordID', text='Discord ID', command=lambda: self.treeview_sort_column(self.tree, 'discordID', False))
        self.tree.heading('lastConnectionDate', text='Last Connection Date', command=lambda: self.treeview_sort_column(self.tree, 'lastConnectionDate', False))
        self.tree.column('playername', stretch=tk.YES)
        self.tree.column('discordID', stretch=tk.YES)
        self.tree.column('lastConnectionDate', stretch=tk.YES)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.process_players(data.get('players', []))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while reading the file: {e}")

    def process_players(self, players):
        self.players_data = []
        for player in players:
            last_connection_date = datetime.utcfromtimestamp(player.get('tsLastConnection', 0)).strftime('%Y-%m-%d %H:%M:%S')
            discord_id = None
            for id_string in player.get('ids', []):
                if id_string.startswith('discord:'):
                    discord_id = id_string.split(':')[1]
                    break
            self.players_data.append({
                'playername': player.get('displayName', 'N/A'),
                'discordID': discord_id,
                'lastConnectionDate': last_connection_date
            })
        self.update_display()

    def update_display(self):
        # Clear the existing data in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insert new player data
        for player in self.players_data:
            self.tree.insert('', 'end', values=(player['playername'], player['discordID'], player['lastConnectionDate']))

    def export_to_csv(self):
        if self.players_data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=["playername", "discordID", "lastConnectionDate"])
                        writer.writeheader()
                        writer.writerows(self.players_data)
                    messagebox.showinfo("Success", "The data was successfully exported to CSV.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while writing to the file: {e}")
        else:
            messagebox.showinfo("Info", "There is no data to export.")

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # Reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerDataApp(root)
    root.mainloop()
