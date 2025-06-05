import csv
import math


def load_spy_prices(filename):
    """Load SPY close prices from a CSV file."""
    dates = []
    closes = []
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip tickers row
        next(reader)  # skip header row
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
    return dates, closes


def mean_reversion_strategy(prices, window=20, threshold=0.02):
    """Simple mean-reversion strategy.

    Buy when price dips below (1 - threshold) * moving average.
    Hold for one day and exit at next close.
    Returns the portfolio value series.
    """
    portfolio = [1.0]
    n_days = len(prices)
    for t in range(window, n_days - 1):
        ma = sum(prices[t - window + 1 : t + 1]) / window
        price_today = prices[t]
        price_next = prices[t + 1]
        if price_today < (1 - threshold) * ma:
            portfolio.append(portfolio[-1] * price_next / price_today)
        else:
            portfolio.append(portfolio[-1])
    return portfolio


def main():
    dates, closes = load_spy_prices("SPY15yrHistory.csv")
    portfolio = mean_reversion_strategy(closes, window=20, threshold=0.02)
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
