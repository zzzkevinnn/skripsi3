from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import os
import math

app = Flask(__name__)



# HALAMAN UTAMA 
@app.route('/dashboard')
def dashboard():
    return render_template('/Utama/dashboard.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('/register.html')



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


def load_json():
    with open('test.json', 'r') as file:
        return json.load(file)



# sssssssssssssssssssssssssssssssssssssssss
def get_stock_details(codes):
    stock_data = []
    for code in codes:
        stock = yf.Ticker(code)
        info = stock.info
        stock_data.append({
            "code": code,
            "name": info.get("longName", "N/A"),
            "price": info.get("currentPrice", "N/A"),
        })
    return stock_data



# -----------------------------------------------

PROFILE_DIR = "./json_file/"  # Direktori tempat file JSON sejajar dengan app.py

def list_profiles():
    files = os.listdir(PROFILE_DIR)
    return [os.path.splitext(file)[0] for file in files if file.endswith('.json')]
@app.route('/edit', methods=['GET', 'POST'])


def edit():
    with open('list-1.json') as file:
        stocks = json.load(file)

    
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
        hari = int(request.form.get('hari'))
        minimal_roc = float(request.form.get('minimal_roc'))

        end_date = datetime.now()
        start_date = end_date - timedelta(days=hari)
        minimal_volume = int(request.form.get('volume'))

        # Store the parameters hari, start_date, and end_date in a JSON file
        time = {
            "hari": hari,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        with open('time.json', 'w') as file:
            json.dump(time, file, indent=4)

        # Load stock symbols from JSON file
        with open('list-1.json') as file:
            stocks = json.load(file)

        lulus = []

        for stock_symbol in stocks:
            try:
                stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
                stock_name = yf.Ticker(stock_symbol).info.get('shortName', 'Unknown Name')

                all_time_high = stock_data['Close'].max()
                last_close = stock_data['Close'].iloc[-1]
                start_date_close = stock_data['Close'][0]
                volume_real = (stock_data['Close'] * stock_data['Volume']).mean()
                deviasi = stock_data["Close"].std()
                roc = ((last_close - start_date_close) / start_date_close) * 100
                rocp = roc/hari 
                deviasiper = (deviasi/last_close)* 100 
                rocdev = (rocp / deviasiper) * 100 



                if last_close == all_time_high:
                    if roc >= minimal_roc:
                        avg_close = stock_data['Close'].mean()
                        if avg_close >= minimal_roc:
                            if volume_real > minimal_volume:
                                lulus.append({
                                    "roc": math.floor(roc),
                                    "kode_saham": stock_symbol,
                                    "volume": f"{math.floor(volume_real):,}",
                                    "nama_saham": stock_name,
                                    "harga_hari_ini": last_close,
                                    "harga_awal": start_date_close,
                                    "rata_rata": math.floor(avg_close),
                                    "link_saham": f"https://finance.yahoo.com/quote/{stock_symbol}",
                                    "deviasi":f"{(deviasi):.2f}",
                                    "deviasiper":f"{(deviasiper ):.2f}",
                                    "rocPerDev":f"{(deviasi):.2f}",
                                    # "rocdev":f"{(((roc/hari)/deviasi)*100):.2f}",
                                    "rocdev":f"{(rocdev):.2f}",
                                    "rocp"   :f"{(rocp):.2f}",
                                 
                                })
            except Exception as e:
                print(f"Failed to retrieve data for {stock_symbol}: {str(e)}")

        if lulus:
            df = pd.DataFrame(lulus)
            df.to_excel("stock_analysis.xlsx", index=False)
            with open('stock_analysis.json', 'w') as file:
                json.dump(lulus, file, indent=4)

        return render_template('/Hasil/riwayat.html', lulus=lulus, total=len(lulus), hari=hari , time=time)

    return render_template('/Utama/perhitungan.html')


# HASIL -------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/Hasil/riwayat')
def riwayat():
    try:
        with open('stock_analysis.json') as file:
            time = json.load(file)
        with open('time.json') as file:
            lulus = json.load(file)
    except FileNotFoundError:
        lulus = []
    
    return render_template('/Hasil/riwayat.html', lulus=lulus, total=len(lulus), time=time)


if __name__ == '__main__':
    app.run(debug=True)
