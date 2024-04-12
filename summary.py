from openai import OpenAI
import os

client = OpenAI(api_key="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")


def summarize_files(folder_path):
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(
        folder_path) if file.endswith('.txt')]
    summaries = []

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"{content}를 2~3줄 분량의 핵심 문장으로 요약해줘",
                }
            ],
            max_tokens=150,
            stream=True,
        )

        summary = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                summary += chunk.choices[0].delta.content

        summaries.append({'file_path': file_path, 'summary': summary})

    return summaries
