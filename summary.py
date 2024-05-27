from openai import OpenAI
import os
import re

client = OpenAI(api_key="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")

def extract_title(content):
    title_pattern = r'Title: (.*)$'
    match = re.search(title_pattern, content, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None

def extract_link(content):
    link_pattern = r'Link: (.*)$'
    match = re.search(link_pattern, content, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None

def summarize_files(folder_path):
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.txt')]
    summaries = []

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 뉴스를 핵심 문장으로 요약해주는 문장의 끝맺음이 확실한 훌륭한 기자이다."},
                {"role": "user", "content": f"{content}를 3~4줄 이하로 요약해줘."}
            ],
            max_tokens=300,
            stream=True,
        )

        summary = ""
        title = extract_title(content)  # 타이틀 추출
        link = extract_link(content)    # 링크 추출
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                summary += chunk.choices[0].delta.content

        summaries.append({'file_path': file_path, 'summary': summary, 'link': link, 'title': title})

    return summaries
