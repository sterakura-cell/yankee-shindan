#!/usr/bin/env python3
"""USD/JPY multi-timeframe technical report from Twelve Data JSON files.

Usage: python3 -I analyze.py <data_dir> [out_dir]
Reads td_{1min,5min,15min,1h,1day}.json (timezone Asia/Tokyo) and prints a report.
If out_dir is given, writes PNG charts there (needs mplfinance).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else None


def load(iv):
    d = json.loads((DATA / f"td_{iv}.json").read_text())
    df = pd.DataFrame(d["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    df = df.set_index("datetime").sort_index()
    return df[["open", "high", "low", "close"]]


def sma(s, n):
    return s.rolling(n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn
    return 100 - 100 / (1 + rs)


def macd(s, f=12, sl=26, sig=9):
    m = ema(s, f) - ema(s, sl)
    si = ema(m, sig)
    return m, si, m - si


def atr(df, n=14):
    pc = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def bollinger(s, n=20, k=2.0):
    m = sma(s, n)
    sd = s.rolling(n).std(ddof=0)
    return m, m + k * sd, m - k * sd


def ichimoku(df):
    h, l, c = df["high"], df["low"], df["close"]
    tenkan = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kijun = (h.rolling(26).max() + l.rolling(26).min()) / 2
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    chikou = c.shift(-26)
    return tenkan, kijun, span_a, span_b, chikou


def swings(df, w=3, n=4):
    """Return recent fractal swing highs/lows (last n each)."""
    h, l = df["high"], df["low"]
    hi = [(t, v) for t, v in h.items() if v == h.loc[:t].tail(w + 1).max() and v == h.loc[t:].head(w + 1).max()]
    lo = [(t, v) for t, v in l.items() if v == l.loc[:t].tail(w + 1).min() and v == l.loc[t:].head(w + 1).min()]
    return hi[-n:], lo[-n:]


def fmt(x):
    return f"{x:.3f}" if isinstance(x, (float, np.floating)) and not np.isnan(x) else "n/a"


def report_tf(name, df, ma_list, ichi=False):
    c = df["close"]
    last = df.iloc[-1]
    out = [f"\n=== {name} | last bar {df.index[-1]:%m-%d %H:%M} O {last.open:.3f} H {last.high:.3f} L {last.low:.3f} C {last.close:.3f}"]
    for n in ma_list:
        v = sma(c, n).iloc[-1]
        prev = sma(c, n).iloc[-6] if len(c) > n + 6 else np.nan
        slope = "↑" if v > prev else "↓" if v < prev else "→"
        rel = "above" if last.close > v else "below"
        out.append(f"  SMA{n:<4} {fmt(v)} {slope}  price {rel} ({(last.close - v) * 100:+.1f} sen)")
    for n in (9, 21):
        v = ema(c, n).iloc[-1]
        out.append(f"  EMA{n:<4} {fmt(v)}  price {'above' if last.close > v else 'below'}")
    m, u, lo = bollinger(c)
    width = (u.iloc[-1] - lo.iloc[-1]) * 100
    width_prev = (u.iloc[-11] - lo.iloc[-11]) * 100
    pos = (last.close - lo.iloc[-1]) / (u.iloc[-1] - lo.iloc[-1]) * 100
    out.append(f"  BB(20,2) upper {fmt(u.iloc[-1])} mid {fmt(m.iloc[-1])} lower {fmt(lo.iloc[-1])} width {width:.1f} sen ({'expanding' if width > width_prev else 'contracting'}) %B {pos:.0f}%")
    r = rsi(c)
    out.append(f"  RSI14 {r.iloc[-1]:.1f} (5 bars ago {r.iloc[-6]:.1f})")
    mm, ms, mh = macd(c)
    out.append(f"  MACD {mm.iloc[-1]:.4f} signal {ms.iloc[-1]:.4f} hist {mh.iloc[-1]:+.4f} ({'rising' if mh.iloc[-1] > mh.iloc[-2] else 'falling'})")
    a = atr(df)
    out.append(f"  ATR14 {a.iloc[-1] * 100:.1f} sen")
    if ichi:
        t, k, sa, sb, ch = ichimoku(df)
        cloud_top, cloud_bot = max(sa.iloc[-1], sb.iloc[-1]), min(sa.iloc[-1], sb.iloc[-1])
        where = "above cloud" if last.close > cloud_top else "below cloud" if last.close < cloud_bot else "inside cloud"
        out.append(f"  Ichimoku tenkan {fmt(t.iloc[-1])} kijun {fmt(k.iloc[-1])} cloud {fmt(cloud_bot)}-{fmt(cloud_top)} -> price {where}")
    hi, lo_ = swings(df)
    out.append("  swing highs: " + ", ".join(f"{v:.3f}@{t:%m-%d %H:%M}" for t, v in hi))
    out.append("  swing lows : " + ", ".join(f"{v:.3f}@{t:%m-%d %H:%M}" for t, v in lo_))
    # last 6 candles
    tail = df.tail(6)
    cs = []
    for t, r_ in tail.iterrows():
        body = r_.close - r_.open
        rng = r_.high - r_.low
        kind = "bull" if body > 0 else "bear" if body < 0 else "doji"
        uw = (r_.high - max(r_.open, r_.close)) * 100
        lw = (min(r_.open, r_.close) - r_.low) * 100
        cs.append(f"{t:%H:%M} {kind} body {abs(body) * 100:.1f} uw {uw:.1f} lw {lw:.1f}")
    out.append("  last candles: " + " | ".join(cs))
    return "\n".join(out)


def main():
    m1, m5, m15, h1, d1 = (load(iv) for iv in ("1min", "5min", "15min", "1h", "1day"))
    now = m1.index[-1]
    print(f"USD/JPY report (Asia/Tokyo) data through {now:%Y-%m-%d %H:%M}  last {m1['close'].iloc[-1]:.3f}")

    # Daily pivots from previous completed day
    prev = d1.iloc[-2]
    today = d1.iloc[-1]
    P = (prev.high + prev.low + prev.close) / 3
    R1, S1 = 2 * P - prev.low, 2 * P - prev.high
    R2, S2 = P + (prev.high - prev.low), P - (prev.high - prev.low)
    print(f"\nPrev day ({d1.index[-2]:%m-%d}) H {prev.high:.3f} L {prev.low:.3f} C {prev.close:.3f}")
    print(f"Today    ({d1.index[-1]:%m-%d}) O {today.open:.3f} H {today.high:.3f} L {today.low:.3f} range {(today.high - today.low) * 100:.0f} sen")
    print(f"Pivots: S2 {S2:.3f} S1 {S1:.3f} P {P:.3f} R1 {R1:.3f} R2 {R2:.3f}")
    # Tokyo session (09:00-15:00 JST today)
    tk = m5[(m5.index >= now.normalize() + pd.Timedelta(hours=9)) & (m5.index < now.normalize() + pd.Timedelta(hours=15))]
    if len(tk):
        print(f"Tokyo session H {tk.high.max():.3f} L {tk.low.min():.3f}")
    ld = m5[m5.index >= now.normalize() + pd.Timedelta(hours=16)]
    if len(ld):
        print(f"London so far H {ld.high.max():.3f} L {ld.low.min():.3f}")

    print(report_tf("DAILY", d1, [5, 21, 75, 200], ichi=True))
    print(report_tf("1H", h1, [20, 75, 200], ichi=True))
    print(report_tf("15M", m15, [20, 75, 200]))
    print(report_tf("5M", m5, [5, 20, 75, 200]))
    print(report_tf("1M", m1, [5, 20, 75]))

    if OUT:
        import mplfinance as mpf

        OUT.mkdir(parents=True, exist_ok=True)
        style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"font.size": 8})

        def plot(df, n, title, fname, mas, ichi=False, bb=True):
            d = df.tail(n).copy()
            full = df
            adds = []
            for ma, col in zip(mas, ["#e6a800", "#888888", "#00b0c8", "#c040c0"]):
                adds.append(mpf.make_addplot(sma(full["close"], ma).tail(n), color=col, width=0.9))
            if bb:
                m, u, lo = bollinger(full["close"])
                adds.append(mpf.make_addplot(u.tail(n), color="#ff8c00", width=0.7, linestyle="--"))
                adds.append(mpf.make_addplot(lo.tail(n), color="#ff8c00", width=0.7, linestyle="--"))
            if ichi:
                t, k, sa, sb, _ = ichimoku(full)
                adds.append(mpf.make_addplot(t.tail(n), color="#d33", width=0.8))
                adds.append(mpf.make_addplot(k.tail(n), color="#33a", width=0.8))
                adds.append(mpf.make_addplot(sa.tail(n), color="#6c6", width=0.5))
                adds.append(mpf.make_addplot(sb.tail(n), color="#c66", width=0.5))
            r = rsi(full["close"]).tail(n)
            adds.append(mpf.make_addplot(r, panel=1, color="#555", ylabel="RSI", ylim=(0, 100)))
            adds.append(mpf.make_addplot(pd.Series(70, index=r.index), panel=1, color="#bbb", width=0.5))
            adds.append(mpf.make_addplot(pd.Series(30, index=r.index), panel=1, color="#bbb", width=0.5))
            mpf.plot(d, type="candle", style=style, addplot=adds, title=title, ylabel="USD/JPY",
                     panel_ratios=(3, 1), figsize=(12, 7), savefig=dict(fname=str(OUT / fname), dpi=130),
                     datetime_format="%m-%d %H:%M", xrotation=0, tight_layout=True)

        plot(m5, 180, "USD/JPY 5min  SMA5/20/75/200 + BB(20,2)", "usdjpy_5m.png", [5, 20, 75, 200])
        plot(m15, 160, "USD/JPY 15min  SMA20/75/200 + BB", "usdjpy_15m.png", [20, 75, 200])
        plot(h1, 200, "USD/JPY 1H  SMA20/75/200 + BB + Ichimoku", "usdjpy_1h.png", [20, 75, 200], ichi=True)
        plot(d1, 160, "USD/JPY Daily  SMA21/75/200 + BB + Ichimoku", "usdjpy_daily.png", [21, 75, 200], ichi=True)
        print(f"\ncharts written to {OUT}")


if __name__ == "__main__":
    main()
