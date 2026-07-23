# AGENTS.md — ヤンキータイプ診断

AIコーディングエージェント（Codex 等）向けガイド。まず `README.md` を読むこと。ここは要点と注意点のみ。

## これは何か
- あなたの中のヤンキーを16タイプに分類する**静的ネタ診断サイト**。本番 https://yankee.soter-info.com
- **ビルド工程なし**。`index.html` 1枚に全部入り。GitHub Pages（`main` push で自動デプロイ）。

## 触っていい / 触らない
- 編集対象は **`index.html`**（診断ロジック・16タイプ・決め台詞・SVGイラスト・シェア機能）。
- `og.png` / `card/*.png` / `t/*.html` は**自動生成物**。手編集せず `tools/build-assets.js` で再生成。
- `all16.png` はイラスト原画（分割元、.gitignore対象）。`CNAME`・DNS・HTTPSは設定済み、理由なく変更しない。

## 16タイプのコード体系
4軸2極。軸1 `K`/`N`（硬派/軟派）、軸2 `B`/`O`（番長/一匹狼）、軸3 `A`/`C`（熱血/クール）、軸4 `T`/`S`（武闘派/知略派）。
16コード: KBAT KBAS KBCT KBCS KOAT KOAS KOCT KOCS NBAT NBAS NBCT NBCS NOAT NOAS NOCT NOCS

## 重要な整合ルール
- **タイプ名を変えたら** `index.html` の `TYPES[code].name` と `tools/build-assets.js` の `CONFIG.names` の**両方**を更新（不一致だとカード画像タイトルがズレる）。
- 各タイプは `mic`（決め台詞）を必ず持つ。「強面の見た目 × 残念な中身」のギャップが世界観。攻撃的・差別的・暴力賛美にしない。特定実在人物の台詞は使わない。
- 相性文 `match` は `（CODE）名前` 形式。参照名は実在タイプ名と一致させる。追加/削除は不可（16固定）。

## イラスト差し替え
1. `img/<CODE>.png`（透過PNG）を差し替え。2. `cd tools && npm install && node build-assets.js`。3. push。※無くても `yankeeSVG()` にフォールバック。

## デプロイ / 確認
```
git add -A && git commit -m "..." && git push
gh api repos/sterakura-cell/yankee-shindan/pages/builds/latest --jq .status   # "built"
curl -s https://yankee.soter-info.com/ | grep -o '<title>[^<]*</title>'
```
ローカル確認は `index.html` をブラウザで直接開くだけ（サーバ不要）。

## 姉妹サイト
わんこ/にゃんこ/夜職が同構造（コード体系のみ別）。全サイトの結果画面から相互リンクしている。
