from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

PROFILE_DIR = "."  # Direktori tempat file JSON sejajar dengan app.py

# HALAMAN UTAMA 
@app.route('/dashboard')
def dashboard():
    return render_template('/Utama/dashboard.html')

DATA_FILE = 'notes.json'

# default ----------------------------------------------------
def read_notes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Fungsi untuk menulis data ke file JSON
def write_notes(notes):
    with open(DATA_FILE, 'w') as f:
        json.dump(notes, f, indent=4)
# -------------------------------------------------------------
# Halaman utama untuk menampilkan semua catatan

# Fungsi untuk menyimpan data profil
def load_profile(profile_name):
    file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
    if not os.path.exists(file_path):
        return []  # Kembalikan daftar kosong jika file tidak ditemukan
    with open(file_path, 'r') as f:
        return json.load(f)
    
def save_profile(profile_name, stocks):
    file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
    with open(file_path, 'w') as f:
        json.dump(stocks, f, indent=4)

# Fungsi untuk mendapatkan daftar profil (file JSON)
def list_profiles():
    files = os.listdir(PROFILE_DIR)
    return [os.path.splitext(file)[0] for file in files if file.endswith('.json')]
# baru ----------------------------------------------------------------
@app.route('/create_profile', methods=['POST'])
def create_profile():
    profile_name = request.form['profile_name']
    file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")

    if os.path.exists(file_path):
        return "Profile already exists!", 400  # Jika profil sudah ada

    # Membuat file baru untuk profil
    save_profile(profile_name, [])
    return redirect(url_for('index'))

# ----------------------------------------------------------------p

# Menambah catatan baru
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        notes = read_notes()
        note = {
            "id": len(notes) + 1,
            "title": title,
            "content": content
        }
        notes.append(note)
        write_notes(notes)
        return redirect(url_for('index'))
    return render_template('add_note.html')


# Mengedit catatan
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    notes = read_notes()
    note = next((note for note in notes if note['id'] == note_id), None)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if note:
            note['title'] = title
            note['content'] = content
            write_notes(notes)
        return redirect(url_for('index'))
    return render_template('edit_note.html', note=note)

# Menghapus catatan
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    notes = read_notes()
    notes = [note for note in notes if note['id'] != note_id]
    write_notes(notes)
    return redirect(url_for('index'))


# -----------------------------------------------
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    with open('list-1.json') as file:
        stocks = json.load(file)

    
    data = load_data()
    if request.method == 'POST':
        new_stock = request.form.get('new_stock')
        delete_stock = request.form.get('delete_stock')

        # Add new stock symbol
        if new_stock:
            if new_stock not in stocks:
                stocks.append(new_stock)

        # Delete selected stock symbol
        if delete_stock:
            if delete_stock in stocks:
                stocks.remove(delete_stock)
    profiles = list_profiles()
                
    return render_template('/edit.html', stocks=stocks, profiles=profiles)



DATA_FILE = "data.json"

# Fungsi untuk memuat data dari JSON
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Fungsi untuk menyimpan data ke JSON
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Route untuk halaman utama
@app.route("/index")
def index():
    data = load_data()
    return render_template("index.html", profiles=data)

# Route untuk menampilkan profil
@app.route("/profile/<profile_name>")
def profile(profile_name):
    data = load_data()
    profile_data = data.get(profile_name, [])
    return render_template("profile.html", profile_name=profile_name, stocks=profile_data)

# Route untuk menambahkan saham
@app.route("/profile/<profile_name>/add", methods=["POST"])
def add_stock(profile_name):
    symbol = request.form.get("symbol")
    data = load_data()
    
    # Ambil data saham dari Yahoo Finance
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.info
        stock_data = {
            "symbol": symbol,
            "name": stock_info.get("longName", "Unknown"),
            "price": stock_info.get("regularMarketPrice", 0),
        }
        data.setdefault(profile_name, []).append(stock_data)
        save_data(data)
        return redirect(url_for("profile", profile_name=profile_name))
    except Exception as e:
        return f"Error fetching stock data: {e}"

# Route untuk menghapus saham
@app.route("/profile/<profile_name>/delete/<symbol>")
def delete_stock(profile_name, symbol):
    data = load_data()
    profile_data = data.get(profile_name, [])
    data[profile_name] = [stock for stock in profile_data if stock["symbol"] != symbol]
    save_data(data)
    return redirect(url_for("profile", profile_name=profile_name))

# Route untuk mengedit saham
@app.route("/profile/<profile_name>/edit/<symbol>", methods=["GET", "POST"])
def edit_stock(profile_name, symbol):
    data = load_data()
    profile_data = data.get(profile_name, [])
    stock = next((s for s in profile_data if s["symbol"] == symbol), None)
    
    if request.method == "POST":
        stock["name"] = request.form.get("name")
        stock["price"] = float(request.form.get("price"))
        save_data(data)
        return redirect(url_for("profile", profile_name=profile_name))
    
    return render_template("edit_stock.html", profile_name=profile_name, stock=stock)

@app.route("/add_profile", methods=["POST"])
def add_profile():
    profile_name = request.form.get("new_profile").strip()
    if not profile_name:
        return redirect(url_for("index"))  # Jika nama kosong, kembali ke halaman utama
    
    data = load_data()
    if profile_name not in data:
        data[profile_name] = []  # Tambahkan profil baru sebagai array kosong
        save_data(data)
    
    return redirect(url_for("index"))

# d-----------------------------------------------------------------------------------------
@app.route("/profile/<profile_name>")
def profiles(profile_name):
    data = load_data()
    profile_data = data.get(profile_name, [])
    return render_template("profile.html", profile_name=profile_name, stocks=profile_data)



@app.route('/editProfileSaham', methods=['POST'])
def editProfileSaham():
    
    return  render_template('/editProfileSaham.html')


@app.route('/', methods=['GET', 'POST'])
def login():

    return render_template('/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    return render_template('/register.html')
# EDITING SAHAM -------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/Edit/editSaham', methods=['GET', 'POST'])
def editSaham():
    # Load stock symbols from JSON file
    with open('list-1.json') as file:
        stocks = json.load(file)

    if request.method == 'POST':
        new_stock = request.form.get('new_stock')
        delete_stock = request.form.get('delete_stock')

        # Add new stock symbol
        if new_stock:
            if new_stock not in stocks:
                stocks.append(new_stock)

        # Delete selected stock symbol
        if delete_stock:
            if delete_stock in stocks:
                stocks.remove(delete_stock)

        # Save the updated stock list back to the JSON file
        with open('list-1.json', 'w') as file:
            json.dump(stocks, file)

    return render_template('/Edit/editSaham.html', stocks=stocks)
# PERHITUNGAN  -------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/perhitungan', methods=['GET', 'POST'])
def perhitungan():
    if request.method == 'POST':
        minggu = int(request.form.get('minggu'))
        min_roc = float(request.form.get('min_roc'))
        min_mean = float(request.form.get('min_mean'))
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=minggu)

        # Load stock symbols from JSON file
        with open('list-1.json') as file:
            stocks = json.load(file)

        lulus = []

        for stock_symbol in stocks:
            try:
                stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

                all_time_high = stock_data['Close'].max()
                last_close = stock_data['Close'].iloc[-1]
                start_date_close = stock_data['Close'][0]

                

                if last_close == all_time_high :
                    roc = ((last_close - start_date_close) / start_date_close) * 100
                    if roc >= min_roc:
                        # Calculate the average closing price over the weeks
                        avg_close = stock_data['Close'].mean()
                        if avg_close >= min_mean:
                            lulus.append({
                                "roc": roc,
                                "kode_saham": stock_symbol,
                                "harga_hari_ini": last_close,
                                "harga_awal": start_date_close,
                                "rata_rata": avg_close,  # Include average closing price
                                "link_saham": f"https://finance.yahoo.com/quote/{stock_symbol}"
                        })
            except Exception as e:
                print(f"Failed to retrieve data for {stock_symbol}: {str(e)}")

        if lulus:
            df = pd.DataFrame(lulus)
            df.to_excel("stock_analysis.xlsx", index=False)

            # Save the analysis results to a JSON file
            with open('stock_analysis.json', 'w') as file:
                json.dump(lulus, file, indent=4)

        return render_template('result.html', lulus=lulus, total=len(lulus), minggu=minggu)

    return render_template('/Utama/perhitungan.html')

# HASIL -------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/Hasil/riwayat')
def riwayat():
    try:
        with open('stock_analysis.json') as file:
            lulus = json.load(file)
    except FileNotFoundError:
        lulus = []
    
    return render_template('/Hasil/riwayat.html', lulus=lulus, total=len(lulus))


if __name__ == '__main__':
    app.run(debug=True)
