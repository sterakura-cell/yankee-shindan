#!/bin/sh
# Fetch USD/JPY candles from Twelve Data into $1
set -e
mkdir -p "$1"
for iv in 1min 5min 15min 1h 1day; do
  curl -sS -m 30 -A "Mozilla/5.0" -o "$1/td_$iv.json" "https://api.twelvedata.com/time_series?symbol=USD/JPY&interval=$iv&outputsize=1000&timezone=Asia/Tokyo&apikey=${TWELVEDATA_API_KEY:-demo}"
done
