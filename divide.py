import re

def split_news_from_file(filename):
    # 파일 읽기
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    # 각 뉴스를 나누는 패턴 찾기
    pattern = r'Title: (.*?)\nDate: (.*?)\nLink: (.*?)\nContent: \[\s*(.*?)\s*\]\s*'
    news_matches = re.findall(pattern, text, re.DOTALL)

    # 각 뉴스를 파일로 저장
    for idx, match in enumerate(news_matches, start=1):
        title, date, link, content = match
        # content 내용이 비어있는 경우 처리
        if not content.strip():
            continue
        # content에서 뉴스 본문 내용 추출
        content_pattern = r'\[([\[\]]*?)\]\s*(.*?)\"'
        content_match = re.search(content_pattern, content)
        if content_match:
            content = content_match.group(2).strip()
        output_filename = f"news_{idx}.txt"
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(f"Title: {title}\n")
            file.write(f"Date: {date}\n")
            file.write(f"Link: {link}\n")
            # content의 앞뒤 공백을 제거하고 저장
            file.write(f"Content: {content.strip()}\n")
