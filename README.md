# ヤンキータイプ診断

12問に答えると、あなたの中のヤンキーを16タイプに分類するネタ診断サイト。
本番: **https://yankee.soter-info.com**

「16タイプ診断」シリーズの1つ（[わんこ](https://wanko.soter-info.com) / [にゃんこ](https://neko.soter-info.com) / ヤンキー / [夜職](https://yorushoku.soter-info.com)）。全て同じエンジン。

---

## 技術スタック / 特徴

- **ビルド不要の静的サイト**。`index.html` 1ファイルに HTML/CSS/JS 全部入り（フレームワーク・npm依存なし）。
- ホスティングは **GitHub Pages**（`main` ブランチのルートを配信）。`git push` で自動デプロイ。
- イラストは `img/<CODE>.png` を表示、読み込み失敗時は JS内蔵のSVG（`yankeeSVG()`）にフォールバック。
- テーマは黒×金×赤（特攻服イメージ）。GA4は未設置（TODO）。

## ファイル構成

```
index.html            サイト本体（診断ロジック・16タイプ・SVGイラスト・シェア機能）
CNAME                 独自ドメイン（yankee.soter-info.com）
sitemap.xml           サイトマップ
og.png                トップOGP画像（16タイプのグリッド）※自動生成物
all16.png             ChatGPTで生成した4x4グリッド原画（.gitignore対象・分割元）
img/<CODE>.png        タイプ別イラスト16枚（all16.pngを分割・透過化したもの）
card/<CODE>.png       タイプ別シェアカード16枚 ※自動生成物
t/<CODE>.html         タイプ別シェアページ（OGP付き、/?type=CODE へ誘導）※自動生成物
tools/build-assets.js og.png/card/t を img/ から再生成するスクリプト
```

## 診断の仕組み

**4軸 × 2極 = 16タイプ**。各タイプは4文字コード。

| 軸 | 左極 | 右極 |
|----|------|------|
| 1 スタンス | **K** 硬派 | **N** 軟派 |
| 2 立ち位置 | **B** 番長 | **O** 一匹狼 |
| 3 気質 | **A** 熱血 | **C** クール |
| 4 戦い方 | **T** 武闘派 | **S** 知略派 |

例: `KOAS` = 硬派・一匹狼・熱血・知略派 =「カツアゲ未遂リーゼント」。
12問（各軸3問）に回答→軸ごとに多数決→`TYPES[code]` を表示。ロジックは `index.html` の `AXES`/`QUESTIONS`/`TYPES`/`finish()`。

## コンセプト

「見た目は強面ヤンキー × 中身は残念でかわいい」ギャップ。各タイプに **`mic`（マイクパフォーマンス風の決め台詞）** を持たせている（ブレイキングダウン風味だが特定個人の台詞は使わない）。男8/女8のバランス。

## よくある編集

すべて `index.html` 内。
- **決め台詞や説明を変える** → `TYPES` の該当コードの `mic`/`desc`/`catch` を編集。
- **質問を変える** → `QUESTIONS`（`axis`0〜3、`p`は各軸の極キー）。
- **タイプ名を変える** → `TYPES[code].name` と `tools/build-assets.js` の `CONFIG.names` の**両方**を更新（カード画像タイトルに使うため）。

## イラストの差し替え（AI画像）

このサイトの画像はChatGPTで「4×4グリッド16体」を1枚生成→分割・白背景透過化して `img/` に配置したもの。差し替え手順:
1. 新しい `img/<CODE>.png`（透過PNG）を配置。
2. `cd tools && npm install && node build-assets.js` で `og.png`/`card`/`t` を再生成。
3. push。※画像が無くても `yankeeSVG()` のSVGにフォールバックする。

## デプロイ

```
git add -A && git commit -m "説明" && git push
gh api repos/sterakura-cell/yankee-shindan/pages/builds/latest --jq .status  # "built"で反映
```

### ドメイン / DNS / HTTPS（設定済み・通常触らない）
- `CNAME` に `yankee.soter-info.com`。DNSは **Squarespace Domains**（CNAME yankee→sterakura-cell.github.io）。HTTPS強制済み。

## TODO
- GA4計測タグ未設置（他サイトは導入済み）。

## リポジトリ
`sterakura-cell/yankee-shindan`（public）。
