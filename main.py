"""DSPy サンプルコード: 質問応答と Chain of Thought"""

import os

import dspy


def basic_qa():
    """基本的な質問応答の例"""
    predict = dspy.Predict("question -> answer")
    result = predict(question="東京タワーの高さは？")
    print(f"[Basic QA]\n  Q: 東京タワーの高さは？\n  A: {result.answer}\n")


def chain_of_thought():
    """Chain of Thought（段階的推論）の例"""
    cot = dspy.ChainOfThought("question -> answer")
    result = cot(question="1から10までの合計はいくつですか？")
    print(f"[Chain of Thought]\n  Q: 1から10までの合計はいくつですか？")
    print(f"  Reasoning: {result.reasoning}")
    print(f"  A: {result.answer}\n")


class Summarizer(dspy.Signature):
    """文章を日本語で簡潔に要約する"""

    text: str = dspy.InputField(desc="要約する文章")
    summary: str = dspy.OutputField(desc="日本語の簡潔な要約")


def summarize():
    """カスタム Signature を使った要約の例"""
    summarize_cot = dspy.ChainOfThought(Summarizer)
    text = (
        "DSPy is a framework for algorithmically optimizing LM prompts and weights, "
        "especially when LMs are used one or more times within a pipeline. "
        "Using DSPy, you can focus on defining what your system should do, "
        "rather than manually crafting prompts."
    )
    result = summarize_cot(text=text)
    print(f"[Summarize]\n  Input: {text[:60]}...")
    print(f"  Summary: {result.summary}\n")


def main():
    # LM の設定（環境変数 OPENAI_API_KEY が必要）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY 環境変数を設定してください")
        print("  export OPENAI_API_KEY='sk-...'")
        return

    lm = dspy.LM("openai/gpt-4o-mini")
    dspy.configure(lm=lm)

    basic_qa()
    chain_of_thought()
    summarize()


if __name__ == "__main__":
    main()
