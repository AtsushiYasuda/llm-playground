# llm-playground

DSPy を使った LLM 実験用プロジェクト。

## セットアップ

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール & venv 作成
uv sync

# 環境変数の設定
export OPENAI_API_KEY='sk-...'
```

## 実行

```bash
uv run python main.py
```

## サンプル内容

- **Basic QA** - `dspy.Predict` による基本的な質問応答
- **Chain of Thought** - `dspy.ChainOfThought` による段階的推論
- **Summarize** - カスタム `dspy.Signature` を使った文章要約
