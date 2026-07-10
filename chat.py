import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# riwayat percakapan, dimulai dengan aturan (system prompt)
messages = [
    {
        "role": "system",
        "content": "Kamu adalah tutor pemrograman yang sabar dan ramah. Jawab dengan Bahasa Indonesia sederhana. Jika tidak yakin, katakan tidak tahu, jangan mengarang.",
    }
]

print("Chatbot siap! Ketik 'keluar' untuk berhenti.\n")

while True:
    pertanyaan = input("Kamu: ")

    if pertanyaan.lower() == "keluar":
        print("Sampai jumpa! 👋")
        break

    # 1. tambahkan pesanmu ke riwayat
    messages.append({"role": "user", "content": pertanyaan})

    # 2. kirim SELURUH riwayat -> di sinilah "ingatan"-nya
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
    )

    jawaban = response.choices[0].message.content
    print("AI:", jawaban, "\n")

    # 3. simpan jawaban AI ke riwayat juga
    messages.append({"role": "assistant", "content": jawaban})