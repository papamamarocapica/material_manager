# material_manager
# 教材リンク管理アプリ

Flask + SQLite + Docker で構築
講義資料・参考URL・メモを一元管理する Webアプリ

## 主な機能
- 教材リンクの一覧表示
- 新規登録
- 編集
- 削除
- キーワード検索
- 科目名絞り込み
- お気に入り登録

## 使用技術
- Flask
- SQLite
- Gunicorn
- Docker / Docker Compose

## ディレクトリ構成
```text
flask_material_manager/
├─ app/
│  ├─ static/
│  │  └─ style.css
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ form.html
│  │  └─ index.html
│  ├─ __init__.py
│  ├─ db.py
│  └─ routes.py
├─ .env.example
├─ compose.yaml
├─ Dockerfile
├─ README.md
├─ requirements.txt
├─ wsgi.py
└─ .env
```

## ローカル起動手順
1. `.env.example` を `.env` にコピーする
2. 以下を実行する

```
docker compose up -d --build
```

3. ブラウザで以下にアクセスする

```text
http://localhost:5000
```

## 停止
```bash
docker compose down
```

## 工夫点
- SQLite を使って軽量に構築
- Docker Compose と named volume を使って DB データが消えないようにした
- EC2 上でも `docker compose up -d --build` で再現しやすい構成

## EC2 で動かす
1. GitHub からコードを clone
2. `.env` を作成
3. EC2 のセキュリティグループで 5000 番ポートを許可
4. `docker compose up -d --build`
5. `http://localhost:5000/` へアクセス

## 苦労点
- コンテナ再作成時に DB が消えないよう volume を設定したこと
- EC2 側のセキュリティグループ設定が必要だったこと
- Dockerfile だけで依存関係を完結させ、EC2 に直接ライブラリを入れていないこと
