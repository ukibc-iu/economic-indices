import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def compute_retail_index():
    try:
        df = pd.read_csv("data/Retail_Health.csv")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        # Clean numeric columns
        numeric_cols = ['CCI', 'Inflation', 'Private Consumption', 'UPI Transactions', 'Repo Rate', 'Per Capita NNI']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Directionality adjustment
        df['Inflation'] = -df['Inflation']
        df['Repo Rate'] = -df['Repo Rate']

        df_clean = df.dropna(subset=numeric_cols).copy()

        # === PCA ===
        training_end = pd.to_datetime("2024-03-01")
        df_train = df_clean[df_clean['Date'] <= training_end].copy()

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(df_train[numeric_cols])
        pca = PCA(n_components=1)
        train_index = pca.fit_transform(X_train_scaled)

        X_all_scaled = scaler.transform(df_clean[numeric_cols])
        df_clean['Retail Index Raw'] = pca.transform(X_all_scaled)
        min_val, max_val = train_index.min(), train_index.max()
        df_clean['Retail Index'] = (df_clean['Retail Index Raw'] - min_val) / (max_val - min_val)
        df_clean['Retail Index'] = df_clean['Retail Index'].clip(0, 1)

        df_clean = df_clean.sort_values("Date")
        latest = df_clean.iloc[-1]
        prev = df_clean.iloc[-2]

        return prev["Retail Index"], latest["Retail Index"], latest["Date"].strftime('%b-%y')

    except Exception as e:
        print("Retail Index error:", e)
        return None, None, "–"