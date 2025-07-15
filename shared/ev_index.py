import pandas as pd

def get_latest_ev_adoption():
    df = pd.read_csv("data/EV_Adoption.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['Date'])

    # Clean numeric fields
    ev_cols = ['EV Four-wheeler Sales', 'EV Two-wheeler Sales', 'EV Three-wheeler Sales']
    for col in ev_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

    df['Total Vehicle Sales'] = pd.to_numeric(df['Total Vehicle Sales'].astype(str).str.replace(',', ''), errors='coerce')

    df['EV Total Sales'] = df[ev_cols].sum(axis=1)
    df['EV Adoption Rate'] = df['EV Total Sales'] / df['Total Vehicle Sales']
    df['Month'] = df['Date'].dt.strftime('%b-%Y')

    latest = df.sort_values("Date").iloc[-1]
    return {
        "rate": latest["EV Adoption Rate"],
        "month": latest["Month"],
        "ev_units": int(latest["EV Total Sales"]),
    }