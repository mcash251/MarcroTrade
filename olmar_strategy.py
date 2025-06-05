import csv
import math


def load_spy_prices(filename):
    """Load close prices for SPY from CSV."""
    dates = []
    closes = []
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip first row with tickers
        header = next(reader)  # actual header row
        for row in reader:
            if not row:
                continue
            date = row[0]
            try:
                close = float(row[4])
            except ValueError:
                continue
            dates.append(date)
            closes.append(close)
    return dates, [closes]


def olmar(prices, window=25, leverage=0.2):
    """Run a simplified OLMAR backtest.

    prices: list of list where each sublist contains daily close prices for one asset.
    Returns a list of portfolio values over time.
    """
    n_assets = len(prices)
    n_days = len(prices[0])
    # initial equal weights scaled by leverage
    weights = [leverage / n_assets for _ in range(n_assets)]
    portfolio = [1.0]

    for t in range(window, n_days - 1):
        # compute moving averages for each asset
        ma = []
        for i in range(n_assets):
            window_slice = prices[i][t - window + 1 : t + 1]
            ma.append(sum(window_slice) / window)

        # expected price relatives based on mean reversion
        predicted = [ma[i] / prices[i][t] for i in range(n_assets)]

        # update weights proportionally to predicted returns
        new_weights = [weights[i] * predicted[i] for i in range(n_assets)]
        total = sum(new_weights)
        if total > 0:
            new_weights = [leverage * w / total for w in new_weights]
        weights = new_weights

        # compute daily portfolio return
        daily_returns = [prices[i][t + 1] / prices[i][t] - 1 for i in range(n_assets)]
        portfolio_return = 1 + sum(weights[i] * r for i, r in enumerate(daily_returns))
        portfolio.append(portfolio[-1] * portfolio_return)

    return portfolio


def main():
    dates, price_list = load_spy_prices("SPY15yrHistory.csv")
    portfolio = olmar(price_list, window=25, leverage=0.2)
    final_value = portfolio[-1]
    years = len(portfolio) / 252
    cagr = final_value ** (1 / years) - 1
    drawdown = 0.0
    peak = portfolio[0]
    for v in portfolio:
        if v > peak:
            peak = v
        drawdown = min(drawdown, v / peak - 1)
    print(f"Final value: {final_value:.2f}")
    print(f"CAGR: {cagr*100:.2f}%")
    print(f"Max drawdown: {drawdown*100:.2f}%")


if __name__ == "__main__":
    main()
