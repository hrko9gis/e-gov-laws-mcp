# 法令データMCPサーバー

デジタル庁が公開している法令APIを利用して、法令データを検索できるMCP（Model Context Protocol）サーバーです。

## 機能

- 条件を設定したデータの検索、取得

## 利用可能なツール
#### 1. list_laws

指定条件に該当する法令データの一覧を取得します

#### 2. search_laws

キーワードで法令を検索します

#### 3. get_law

law_id, law_num, law_revision_id のいずれかを指定して法令本文を取得します

#### 4. get_law_revisions

law_id または law_num を指定して法令の履歴一覧を取得します

#### 5. get_law_file

law_id, law_num, law_revision_id のいずれかを指定して法令本文ファイルを取得します

## 依存関係

pip install aiohttp mcp

## 使い方（自分の環境で動作した手順）

ローカルにクローンして使用する場合：

```bash
# リポジトリをクローン
git clone https://github.com/hrko9gis/e-gov-laws-mcp.git
cd e-gov-laws-mcp

# Python仮想環境を使用
uv venv
.venv\Scripts\activate
pip install aiohttp mcp
```

## Claude Desktop での使用

Claude Desktop でMCPサーバーを追加して利用することができます。

1. Claude Desktop で設定画面を開きます

2. このMCPサーバーを追加します
```json
{
    "mcpServers": {
        "e-gov-laws-mcp": {
            "command": "/Users/***/.local/bin/uv",
            "args": [
                "--directory",
                "＜e-gov-laws-mcp.pyが存在するディレクトリを絶対パスで指定＞"
                "run",
                "e-gov-laws-mcp.py"
            ]
        }
    }
}
```

3. 保存します

4. 接続します

## Claude Desktop での使用（自分の環境で動作した設定）
Claude Desktop でMCPサーバーを追加して利用することができます。

1. Claude Desktop で設定画面を開きます

2. このMCPサーバーを追加します
```json
{
    "mcpServers": {
        "e-gov-laws-mcp": {
            "command": "＜e-gov-laws-mcpのディレクトリを絶対パスで指定＞\\venv\\Scripts\\python.exe",
            "args": ["＜e-gov-laws-mcpのディレクトリを絶対パスで指定＞\\e-gov-laws-mcp.py"]
        }
    }
}
```

3. 保存します

4. 接続します


## ライセンス

MIT

