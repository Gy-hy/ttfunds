import matplotlib.pyplot as plt
import pandas as pd


def plot_nav(code: str, df: pd.DataFrame, savepath: str = None):
    plt.figure(figsize=(10, 5))
    plt.plot(df["x"], df["y"], label=f"Fund {code}")
    plt.legend()
    plt.title(f"Fund {code} NAV History")
    if savepath:
        plt.savefig(savepath)
    else:
        plt.show()