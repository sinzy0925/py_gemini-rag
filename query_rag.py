# query_rag.py (事前判定機能付き)
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- .envファイルから環境変数を読み込む ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("APIキーが.envファイルに設定されていません。")
client = genai.Client(api_key=api_key) 

# --- ストア名を設定 ---
FILE_SEARCH_STORE_NAME = "fileSearchStores/gas-documentation-rag-store-eh3fonwv95f9" # あなたのストア名に設定済み

# ▼▼▼【ここからが新しい関数】▼▼▼
def is_question_about_gas(question: str) -> bool:
    """
    質問がGoogle Apps Scriptに関連しているかどうかを判定する関数
    """
    print("  - 質問内容を判定中...")
    try:
        # 判定用のシンプルなプロンプト
        prompt = f"""
        以下のユーザーからの質問は、プログラミング言語の「Google Apps Script (GAS)または、Gemini-api」に関連する内容ですか？
        関連している場合は "Yes"、関連していない場合は "No" とだけ答えてください。

        質問: "{question}"
        """
        
        # 高速なモデルで判定
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0) # 創造性はいらないので温度を0に
        )
        
        # 回答が"Yes"を含んでいるかどうかで判定
        print(f"  - 判定結果: {response.text.strip()}")
        return "yes" in response.text.lower()
    except Exception as e:
        print(f"  - 判定中にエラーが発生しました: {e}")
        return False # エラー時は安全側に倒し、処理を続行しない
# ▲▲▲【ここまでが新しい関数】▲▲▲

if FILE_SEARCH_STORE_NAME == "ここにストア名を貼り付け":
    print("エラー: `FILE_SEARCH_STORE_NAME`に変数を設定してください。")
else:
    question = input("GASまたはgemini-apiに関する質問を入力してください。＝＞ # ")

    instractions="""
# 指示
考えるのは英語で考えること
出力は日本語で出力すること  

"""

    while question:
        # ▼▼▼【ここからが新しいロジック】▼▼▼
        if is_question_about_gas(instractions + question):
            # 質問がGASに関連している場合のみ、RAGを実行
            print("\n🤖 AIが回答を生成中...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[FILE_SEARCH_STORE_NAME]
                            )
                        )
                    ]
                )
            )
            print("\n--- 回答 ---")
            print(response.text)
            #print("\n--- 引用元情報 ---")
            #print(response.candidates[0].grounding_metadata)
            ###
            # grounding_metadataオブジェクトを取得
            metadata = response.candidates[0].grounding_metadata
            if metadata:
                print("\n--- 引用元の詳細 ---")
                for i, chunk in enumerate(metadata.grounding_chunks):
                    source_file = chunk.retrieved_context.title
                    retrieved_text = chunk.retrieved_context.text
                    print(f"\n【引用 {i+1}】")
                    print(f"  ファイル名: {source_file}")
                    print(f"  内容の冒頭: {retrieved_text[:100]}...")
            else:
                # 引用元が見つからなかった場合（RAGが機能しなかった場合）
                print("\n--- 引用元情報 ---")
                print("  (この回答はアップロードされたドキュメントからは引用されていません)")

            ###
        else:
            # 質問がGASに関係ない場合は、定型文を返す
            print("\n--- 回答 ---")
            print("申し訳ありませんが、私はGoogle Apps Scriptに関する質問にのみお答えできます。")
        # ▲▲▲【ここまでが新しいロジック】▲▲▲
            
        question = input("\n次の質問をどうぞ (終了するには Enter のみ): ")

print("プログラムを終了します。")