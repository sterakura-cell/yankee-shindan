# fx-analysis

ドル円スキャルピング用の分析ツール（Twelve Data の価格データを使用）。

## 使い方
```
sh fetch.sh data            # 1分足〜日足のデータを取得（無料キーがあれば環境変数 TWELVEDATA_API_KEY を参照）
python3 -I analyze.py data charts   # 指標レポートを表示し、charts/ にPNGを出力
pip install pandas numpy matplotlib mplfinance
```

## 運用ルール（2026-10-20 時点）
- 1時間足の20本線・75本線の上なら買いだけ、下なら売りだけ
- 5分足の陽線/陰線が3本以上続いた直後は入らない。止まった足（ヒゲ）を1本見てから
- 損切り = 5分足ATR×1.4（目安6銭）、利確 = ATR×2.8（目安12銭）
- 取引は21:30〜24:00、最大4回、2連敗で終了、指標の前後5分は入らない
- 15:00〜17:00（ロンドン初動）は入らない
