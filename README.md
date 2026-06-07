# 蔵メイト (Kura-Mate)

冷蔵庫を「蔵」として捉え、食材の情報をデータ化して最適に管理する、スマート在庫・レシピ管理アプリケーションです。

---

## 1. プロジェクト概要

本プロジェクトは、家庭内での食材廃棄（フードロス）の削減を目的としています。冷蔵庫内の在庫状況と賞味期限を可視化することで、二重買いの防止や計画的な消費をサポートします。大学のデータベース講義の最終課題として、要件定義からデータベース設計、インフラ構築までを一貫して単独で開発しました。

### 主な機能

- **食材在庫管理（CRUD）**: 食材の登録・一覧表示・編集・削除を実装。
- **カテゴリー分類**: 12種類のカテゴリー（野菜、肉、魚、果物、乳製品、冷凍食品、飲み物、惣菜、お菓子、加工食品、調味料、その他）でマスター管理。各カテゴリーには表示用のカラーコードを保持。
- **賞味期限アラート**: 賞味期限までの残日数をバックエンドで自動計算。期限切れ（当日含む）と期限間近（3日以内）を判定し、画面上で視覚的に区別。在庫の総数・期限切れ件数・期限間近件数も集計して表示。
- **検索・フィルタリング**: 食材名によるキーワード検索と、カテゴリー別の絞り込み。
- **レシピ登録・管理**: レシピ（料理名・作り方）と、それに必要な食材カテゴリー・分量を登録・一覧・詳細表示・削除。中間テーブルを介してレシピと食材カテゴリーを多対多で管理。

---

## 2. システム構成 (Architecture)

保守性と拡張性を考慮した **Web 3層アーキテクチャ** を採用しています。

| 層 (Layer)        | 使用技術                       | 役割                          |
| ---------------- | -------------------------- | --------------------------- |
| **Presentation** | HTML5, CSS3, Jinja2        | ブラウザへの画面表示・動的なUI構築          |
| **Application**  | Python, Flask, SQLAlchemy  | ビジネスロジックの処理、ORMによるDB連携      |
| **Data**         | PostgreSQL                 | 食材・レシピデータの永続化・管理            |

---

## 3. インフラ構成 (Infrastructure)

**Docker / Docker Compose** を活用し、OS環境に依存しない再現性の高い開発・実行環境を構築しています。

- **コンテナ構成**:
  - `app`: Flaskサーバー（Python実行環境）
  - `db`: PostgreSQLデータベースサーバー
- **起動順序への対応**: アプリ起動時にDB接続が確立するまで最大30回リトライする処理を実装。コンテナ同時起動時に「DBが未起動の状態でアプリが接続を試みて落ちる」問題を防止しています。
- **マスターデータの自動投入**: 初回起動時にカテゴリーのマスターデータを自動生成。

---

## 4. データベース設計 (Database Design)

リレーショナルデータベース（RDB）による構造化データの管理を行っています。第3正規化を意識し、カテゴリー情報を独立したマスターテーブルに分離することで、データの冗長性と不整合を防いでいます。

### テーブル構成

| テーブル | 主なカラム | 役割 |
| --- | --- | --- |
| `categories` | id (PK), name, color | カテゴリーのマスター。表示用カラーコードを保持 |
| `ingredients` | id (PK), name, quantity, expiry_date, category_id (FK→categories) | 食材在庫。カテゴリーは名前を直接持たずIDで参照 |
| `recipes` | id (PK), title, instructions, created_at | レシピ（料理名・作り方） |
| `recipe_ingredients` | id (PK), recipe_id (FK→recipes), category_id (FK→categories), quantity | レシピと食材カテゴリーをつなぐ中間テーブル |

### 設計上の工夫

- **第3正規化**: `ingredients` はカテゴリー名を直接持たず `category_id` で `categories` を参照。カテゴリー情報の更新が一箇所で完結する設計。
- **多対多リレーションの解消**: レシピと食材カテゴリーの多対多の関係を、中間テーブル `recipe_ingredients` で解消。
- **ユニーク制約**: `recipe_ingredients` の (`recipe_id`, `category_id`) に複合ユニーク制約を設定し、同一レシピ内でのカテゴリー重複を防止。

---

## 5. セットアップ・実行方法

### 動作要件

- Docker / Docker Compose がインストールされていること

### 起動手順

1. リポジトリをクローンします。
2. `infra` ディレクトリへ移動します。

   ```
   cd smart-recipe-app/infra
   ```

3. コンテナをビルド・起動します。

   ```
   docker-compose up --build -d
   ```

4. ブラウザで以下のURLにアクセスします。
   <http://localhost:8080>

---

## 6. 使用技術まとめ

- **言語**: Python
- **Webフレームワーク**: Flask
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **データベース**: PostgreSQL
- **テンプレートエンジン**: Jinja2
- **フロントエンド**: HTML, CSS
- **インフラ**: Docker, Docker Compose

---

## 7. 実際のアプリ動作動画

**Sequence.01_1.mp4**

https://private-user-images.githubusercontent.com/169261943/566077820-9a52851e-1fe6-484d-8c3d-5c5ca62f9e95.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODA4MTY3OTQsIm5iZiI6MTc4MDgxNjQ5NCwicGF0aCI6Ii8xNjkyNjE5NDMvNTY2MDc3ODIwLTlhNTI4NTFlLTFmZTYtNDg0ZC04YzNkLTVjNWNhNjJmOWU5NS5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjA3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYwN1QwNzE0NTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00ODVjNTg1YTI0YzdiMTA4ZjlkNTc5NDUwZmFlN2NjMGY1MGRjMDkyNDgxMDI1ZTg2NjVkYmU5ZmZlOTQ0Mjc4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.aFkQxu6AufSIGTXtLxK4IXS1ZSCJ954I9t0yhDr97h4

> **注意**: 上記の動画リンクは GitHub が発行する署名付きの一時URL（有効期限あり）です。表示されない場合は、GitHub のREADME編集画面に動画ファイルを直接ドラッグ&ドロップして貼り直してください。GitHub が永続的な参照を自動生成します。
