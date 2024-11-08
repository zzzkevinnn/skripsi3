from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)



# HALAMAN UTAMA 
@app.route('/dashboard')
def dashboard():
    return render_template('/Utama/dashboard.html')



def read_file():
    with open('list-1.json') as file:
        stocks = json.load(file)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    files = read_file()
    return render_template('/edit.html')


@app.route('/editProfileSaham', methods=['POST'])
def editProfileSaham():
    return  render_template('/editProfileSaham.html')


@app.route('/', methods=['GET', 'POST'])
def login():

    return render_template('/login.html')



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
