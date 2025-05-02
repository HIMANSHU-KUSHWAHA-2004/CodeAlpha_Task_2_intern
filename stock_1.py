import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt

API_KEY = "HC352CN6R1YY8F8H"

root = tk.Tk()
root.title("Multi-Stock Live Tracker")

# --- FIXED SIZE SETUP ---
window_width = 1000
window_height = 400

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.configure(bg="#1e1e1e")  # Dark theme background
root.resizable(False, False)  # Fixed size

# --- STYLING CONSTANTS ---
FONT = ("Arial", 12)
HEADER_FONT = ("Arial", 15, "bold")
FG_COLOR = "white"
BG_COLOR = "#1e1e1e"
ENTRY_BG = "#2e2e2e"
BUTTON_BG = "#333333"

# --- TRACKING VARIABLES ---
current_row = 160  # Start lower to leave space for headers and input area
tracked_stocks = {}

# --- MAIN HEADING ---
title_label = tk.Label(root, text="📊 STOCK PORTFOLIO TRACKER", font=("Arial", 25, "bold"),
                       bg=BG_COLOR, fg="#00ff99")
title_label.place(x=50, y=10, width=900)

# --- INPUT SECTION ---
symbol_entry = tk.Entry(root, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=('arial', 18), width=40)
symbol_entry.place(x=50, y=70)

tk.Button(root, text="Start Tracking", font=("Arial", 12),
          command=lambda: add_stock(), bg=BUTTON_BG, fg=FG_COLOR, width=18).place(x=600, y=70)

tk.Button(root, text="Refresh All Stats", font=("Arial", 12),
          command=lambda: refresh_all(), bg=BUTTON_BG, fg=FG_COLOR, width=18).place(x=800, y=70)

# --- HEADER ---
headers = ["Stock", "Current Price", "Profit/Loss", "Change", "Actions", "Graph"]

# Calculate column width
total_width = 1000
num_columns = len(headers)
column_width = total_width // num_columns

# Place headers using .place()
for col, header in enumerate(headers):
    x_position = col * column_width
    tk.Label(root, text=header, font=HEADER_FONT, bg=BG_COLOR, fg=FG_COLOR)\
        .place(x=x_position, y=120, width=column_width, height=30)

# --- GRAPH FUNCTION ---
def show_stock_graph(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")

        if data.empty:
            messagebox.showerror("Error", f"No graph data found for {symbol}.")
            return

        plt.style.use("dark_background")
        fig = plt.figure(figsize=(10, 5), facecolor="#1e1e1e")
        fig.canvas.manager.set_window_title(f"{symbol} Price Chart")

        ax = plt.gca()
        ax.set_facecolor("#2a2a2a")

        plt.plot(data.index, data['Close'], color="#00ff99", linewidth=2, label='Close Price')

        plt.title(f"{symbol} - Intraday Price Chart", color="white")
        plt.xlabel("Time", color="lightgray")
        plt.ylabel("Price", color="lightgray")
        plt.grid(color="#444444", linestyle="--", linewidth=0.5)
        plt.tick_params(colors='lightgray')
        plt.legend(facecolor="#2e2e2e", edgecolor="gray")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Could not load graph for {symbol}:\n{e}")

# --- STOCK DATA FETCH ---
def fetch_stock_data(symbol, row_labels):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")

        if data.empty:
            messagebox.showerror("Error", f"No data found for {symbol}.")
            delete_stock(symbol)
            return

        current_price = data['Close'].iloc[-1]
        opening_price = data['Open'].iloc[0]

        # Check if the stock is Indian (ticker ends with .NS or .BO for NSE or BSE)
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            # Indian stock, display in INR
            row_labels[1].config(text=f"₹{current_price:.2f}")
            row_labels[2].config(text=f"₹{current_price - opening_price:.2f}")
        else:
            # Foreign stock, display in USD
            row_labels[1].config(text=f"${current_price:.2f}")
            row_labels[2].config(text=f"${current_price - opening_price:.2f}")

        # Profit/Loss calculation
        profit_loss = current_price - opening_price
        if profit_loss >= 0:
            row_labels[2].config(fg="green")
        else:
            row_labels[2].config(fg="red")

        # Percent change calculation
        percent_change = (profit_loss / opening_price) * 100
        row_labels[3].config(text=f"{percent_change:.2f}%")

        root.after(5000, lambda: fetch_stock_data(symbol, row_labels))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data for {symbol}:\n{e}")

# --- ADD STOCK ---
def add_stock():
    global current_row

    symbol = symbol_entry.get().upper()
    if not symbol or symbol in tracked_stocks:
        return

    row_labels = []
    for col in range(4):
        lbl = tk.Label(root, text="—", font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        lbl.place(x=col * column_width, y=current_row, width=column_width, height=30)
        row_labels.append(lbl)

    # Display stock name
    row_labels[0].config(text=symbol)

    delete_button = tk.Button(root, text="Delete", command=lambda s=symbol: delete_stock(s),
                              bg=BUTTON_BG, fg=FG_COLOR)
    delete_button.place(x=4 * column_width + 35, y=current_row , width=100, height=30)

    graph_button = tk.Button(root, text="📈 Graph", command=lambda s=symbol: show_stock_graph(s),
                             bg=BUTTON_BG, fg=FG_COLOR)
    graph_button.place(x=5 * column_width + 35, y=current_row, width=100, height=30)

    tracked_stocks[symbol] = (row_labels, delete_button, graph_button)
    fetch_stock_data(symbol, row_labels)
    current_row += 35  # Move to the next row

# --- DELETE STOCK ---
def delete_stock(symbol):
    if symbol in tracked_stocks:
        row_labels, delete_button, graph_button = tracked_stocks.pop(symbol)
        for lbl in row_labels:
            lbl.place_forget()
        delete_button.place_forget()
        graph_button.place_forget()
        rearrange_rows()
        messagebox.showinfo("Deleted", f"{symbol} has been removed.")

# --- REARRANGE GRID ---
def rearrange_rows():
    global current_row
    current_row = 150
    for symbol, (row_labels, delete_button, graph_button) in tracked_stocks.items():
        for i, lbl in enumerate(row_labels):
            lbl.place(x=i * column_width, y=current_row, width=column_width, height=30)
        delete_button.place(x=4 * column_width, y=current_row, width=150, height=30)
        graph_button.place(x=5 * column_width, y=current_row, width=150, height=30)
        current_row += 35

# --- REFRESH ALL ---
def refresh_all():
    for symbol, (row_labels, _, _) in tracked_stocks.items():
        fetch_stock_data(symbol, row_labels)

root.mainloop()
