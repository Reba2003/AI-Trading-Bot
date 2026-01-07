import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import threading
import os
import alpaca_trade_api as tradeapi
from openai import OpenAI


DATA_FILE = "equities.json"
ALPACA_KEY = "ALPACA_KEY"
ALPACA_SECRET = "ALPACA_SECRET"
ALPACA_URL = "https://paper-api.alpaca.markets"
OPENAI_KEY = "YOUR_OPENAI_KEY"


api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL, api_version="v2")
ai_client = OpenAI(api_key=OPENAI_KEY)

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading Bot | Professional Version")
        self.equities = self.load_equities()
        self.running = True

        # Build UI Components (Form, Table, Chat)
        self._setup_ui()
        self.refresh_table()

        
        self.engine_thread = threading.Thread(target=self.main_engine_loop, daemon=True)
        self.engine_thread.start()

    def _setup_ui(self):
        """Standard UI Setup logic."""
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=10)
        
        # Symbol, Levels, Drawdown entries
        self.symbol_entry = self._create_label_entry("Symbol:", 0)
        self.levels_entry = self._create_label_entry("Levels:", 2)
        self.drawdown_entry = self._create_label_entry("Drawdown %:", 4)
        
        tk.Button(self.form_frame, text="Add Equity", command=self.add_equity).grid(row=0, column=6, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("Symbol", "Pos", "Entry", "Levels", "Status"), show='headings')
        for col in ["Symbol", "Pos", "Entry", "Levels", "Status"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10)

        # AI Chat Section
        self.chat_input = tk.Entry(self.root, width=50)
        self.chat_input.pack(pady=5)
        tk.Button(self.root, text="Ask AI Risk Manager", command=self.send_ai_message).pack()
        self.chat_output = tk.Text(self.root, height=8, width=70, state=tk.DISABLED)
        self.chat_output.pack(pady=10)

    def _create_label_entry(self, text, col):
        tk.Label(self.form_frame, text=text).grid(row=0, column=col)
        entry = tk.Entry(self.form_frame, width=10)
        entry.grid(row=0, column=col+1, padx=5)
        return entry

    # --- Live API Integration Logic ---
    def fetch_live_price(self, symbol):
        """Fetches latest trade price from Alpaca."""
        try:
            return float(api.get_latest_trade(symbol).price)
        except Exception as e:
            print(f"Alpaca Fetch Error: {e}")
            return -1

    def send_ai_message(self):
        """Threaded AI communication to prevent UI lag."""
        user_query = self.chat_input.get()
        if not user_query: return
        
        def ai_task():
            try:
                # Include portfolio context so the AI knows what you're trading
                context = f"Current Portfolio: {json.dumps(self.equities)}"
                response = ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a Quant Risk Manager. Evaluate this portfolio."},
                        {"role": "user", "content": f"{context}\n\nUser Question: {user_query}"}
                    ]
                )
                self.update_chat_ui(user_query, response.choices[0].message.content)
            except Exception as e:
                self.update_chat_ui(user_query, f"AI Error: {str(e)}")

        threading.Thread(target=ai_task, daemon=True).start()

    def update_chat_ui(self, query, reply):
        self.chat_output.config(state=tk.NORMAL)
        self.chat_output.insert(tk.END, f"YOU: {query}\nAI: {reply}\n\n")
        self.chat_output.see(tk.END)
        self.chat_output.config(state=tk.DISABLED)
        self.chat_input.delete(0, tk.END)

    def main_engine_loop(self):
        """The 'Heart' of the bot: Executes trades in background."""
        while self.running:
            for symbol, data in list(self.equities.items()):
                if data['status'] == "On":
                    self.process_trade_logic(symbol, data)
            time.sleep(60) # Standard 1-minute interval for Martingale check

    def process_trade_logic(self, symbol, data):
        """Placeholder for Martingale execution logic."""
        # 1. Check current Alpaca position
        # 2. Compare current price vs levels
        # 3. Submit limit orders if price hits levels
        pass

    # --- Persistence Helpers ---
    def save_equities(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.equities, f, indent=4)

    def load_equities(self):
        if not os.path.exists(DATA_FILE): return {}
        try:
            with open(DATA_FILE, 'r') as f: return json.load(f)
        except: return {}

    def refresh_table(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for sym, d in self.equities.items():
            self.tree.insert("", "end", values=(sym, d['position'], d['entry_price'], "Active", d['status']))

    def add_equity(self):
        sym = self.symbol_entry.get().upper()
        if not sym: return
        self.equities[sym] = {"position": 0, "entry_price": 0, "status": "Off", "levels": {}}
        self.save_equities()
        self.refresh_table()

if __name__ == '__main__':
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
