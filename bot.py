import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import threading
import random
import alpaca_trade_api as tradeapi

DATA_FILE = "equities.json"

key = ""
secret_key = ""

def fetch_mock_api(symbol):
    """Simulates fetching the current market price."""
    return {"price": 100.0}

def mock_chatgpt_response(message):
    """Simulates an AI response."""
    return f"Mock response to: {message}"

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading Bot")
        self.equities = self.load_equities()
        self.running = True

        # --- Form Frame (Adding Equities) ---
        self.form_frame = tk.Frame(root)
        self.form_frame.pack(pady=10)

        tk.Label(self.form_frame, text="Symbol:").grid(row=0, column=0)
        self.symbol_entry = tk.Entry(self.form_frame)
        self.symbol_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.form_frame, text="Levels:").grid(row=0, column=2)
        self.levels_entry = tk.Entry(self.form_frame)
        self.levels_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.form_frame, text="Drawdown %:").grid(row=0, column=4)
        self.drawdown_entry = tk.Entry(self.form_frame)
        self.drawdown_entry.grid(row=0, column=5, padx=5)

        self.add_button = tk.Button(self.form_frame, text="Add Equity", command=self.add_equity)
        self.add_button.grid(row=0, column=6, padx=5)

        # --- Table (Treeview) ---
        self.tree = ttk.Treeview(root, columns=("Symbol", "Position", "Entry Price", "Levels", "Status"), show='headings')
        for col in ["Symbol", "Position", "Entry Price", "Levels", "Status"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10)

        # --- System Controls ---
        self.toggle_system_button = tk.Button(root, text="Toggle Selected System", command=self.toggle_selected_system)
        self.toggle_system_button.pack(pady=5)

        self.remove_button = tk.Button(root, text="Remove Selected Equity", command=self.remove_selected_equity)
        self.remove_button.pack(pady=5)

        # --- AI Chat Component ---
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(pady=10)

        self.chat_input = tk.Entry(self.chat_frame, width=50)
        self.chat_input.grid(row=0, column=0, padx=5) # Grid used because send_button uses grid

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1)

        self.chat_output = tk.Text(root, height=5, width=60, state=tk.DISABLED)
        self.chat_output.pack(pady=5)

        # Initial table load
        self.refresh_table()

        # Start background thread for auto-updates
        self.auto_update_thread = threading.Thread(target=self.auto_update, daemon=True)
        self.auto_update_thread.start()

    def add_equity(self):
        symbol = self.symbol_entry.get().upper()
        levels_val = self.levels_entry.get()
        drawdown_val = self.drawdown_entry.get()

        # Input Validation
        if not symbol or not levels_val.isdigit() or not drawdown_val.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Invalid Input. Ensure Levels is a number and Drawdown is a decimal.")
            return
        
        levels = int(levels_val)
        drawdown_pct = float(drawdown_val) / 100
        entry_price = fetch_mock_api(symbol)['price']

        # Logic to calculate entry levels
        level_prices = {i+1: round(entry_price * (1 - drawdown_pct * (i + 1)), 2) for i in range(levels)}

        self.equities[symbol] = {
            "position": 0,
            "entry_price": entry_price,
            "levels": level_prices,
            "drawdown":drawdown,
            "status": "Off"
        }
        self.save_equities()
        self.refresh_table()
        # Clear fields after adding
        self.symbol_entry.delete(0, tk.END)
        self.levels_entry.delete(0, tk.END)
        self.drawdown_entry.delete(0, tk.END)

    def toggle_selected_system(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No Equity Selected")
            return
        
        for item in selected_items:
            symbol = self.tree.item(item)['values'][0]
            current_status = self.equities[symbol]['status']
            self.equities[symbol]['status'] = "On" if current_status == "Off" else "Off"

        self.save_equities()
        self.refresh_table()

    def remove_selected_equity(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No Equity Selected")
            return
        
        for item in selected_items:
            symbol = self.tree.item(item)['values'][0] # Fixed 'self.item' typo
            if symbol in self.equities:
                del self.equities[symbol]

        self.save_equities()
        self.refresh_table()

    def send_message(self):
        message = self.chat_input.get()
        if not message:
            return
        
        response = mock_chatgpt_response(message)

        self.chat_output.config(state=tk.NORMAL)
        self.chat_output.insert(tk.END, f"You: {message}\nBot: {response}\n\n")
        self.chat_output.see(tk.END) # Auto-scroll to bottom
        self.chat_output.config(state=tk.DISABLED)
        self.chat_input.delete(0, tk.END)

    def fetch_alpaca_data(self, symbol):
        try:
            barset = api.get_latest_trade(symbol)
        return {"price":barset.price}
    except Exception as e:
        return {"price":-1}

    def check_existing_orders(self, symbol, price):
        try:
            orders = api.list_orders(status='open', symbols=symbol)
            for order in orders:
                if float(order.limit_price) == price:
                    return True
        except Exception as e:
            messagebox.showerror("API Error", f"Error Checking Orders {e}")
        return False
    
    def get_max_entry_price(self, symbol):
        try:
            orders = api.list_orders(status="filled", symbol=symbol, limit=50)
            prices = [float(order.filled_avg_price) for order in orders if order.filled_avg_price]
            return max(prices) if prices else -1
        except Exception as e:
            messagebox.showerror("API error", f"Error Fetching Orders {e}")
            return 0
        
        def trade_system(self):
            for symbol, data in self.equities.items():
                if data['status'] == 'On':
                    position_exists = False
                    try:
                        position = api.get_position(symbol)
                        entry_price = self.get_max_entry_price(symbol)
                        position_exists = True
                    except Exception as e:
                        api.submit_order(
                            symbol = symbol,
                            qty=1,
                            side="buy",
                            type="market",
                            time_in_force="gtc"
                        )
                        messagebox.showinfo("Order Placed", f"Intial Order Placed for {symbol}")
                        time.sleep(2)
                        entry_price = self.get_max_entry_price(symbol)
                    print(entry_price)
                    level_prices = {i+1:round(entry_price*(1-data['drawdown']*(i+1)), 2) for i in range(len(data['levels']))}
                    existing_levels = self.equities.get(symbol, {}).get('levels', {})
                    for level, price in level_prices.items():
                        if level in self.equities[symbol]['levels']:
                            self.place_order(symbol, price, level)


    def refresh_table(self):
        # Clear current table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Repopulate from data dictionary
        for symbol, data in self.equities.items():
            self.tree.insert("", "end", values=(
                symbol,
                data['position'],
                data['entry_price'],
                str(data['levels']),
                data['status']
            ))

    def update_prices(self):
        # This function runs in the background thread. 
        # For now, it just prints, but you can add live price logic here.
        pass

    def auto_update(self):
        while self.running:
            time.sleep(5)
            self.update_prices()

    def save_equities(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.equities, f)

    def load_equities(self):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        
    def on_close(self):
        self.running = False
        self.save_equities()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = TradingBotGUI(root)
    # Ensure background thread stops when window closes
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()