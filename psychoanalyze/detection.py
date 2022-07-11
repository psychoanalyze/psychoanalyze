def load(df):
    df = df.reset_index()
    df["Reference Charge (nC)"] = df["Amp2"] * df["Width2"]
    df = df[df["Reference Charge (nC)"] == 0]
    return df
