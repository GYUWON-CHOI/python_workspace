import streamlit as st
from news_crawler import crawl_news, create_dataframe
from most_keywords import generate_wordcloud_from_url

url = "https://news.naver.com/main/ranking/popularDay.naver"

st.title('SIMPLE NEWS')

search = st.text_input("검색할 키워드를 입력해주세요:", "")
page = 1
page2 = 2

if st.button('검색'):
    if search:
        st.write('검색 중...')
        news_titles, final_urls, news_contents, news_dates = crawl_news(search, page, page2)
        st.write("검색된 기사 갯수: 총 ", (page2 + 1 - page) * 10, '개')
        st.write("\n[뉴스 내용]")
        st.write(news_contents)

        news_df = create_dataframe(news_titles, final_urls, news_contents, news_dates, search)
        
        st.success("검색이 완료되었습니다.")
        st.stop()
    else:
        st.warning("검색어를 입력해주세요.")

# 워드클라우드 섹션 추가
st.sidebar.title('Top KeyWord')  # 사이드바에 제목 추가
fig = generate_wordcloud_from_url(url)
st.pyplot(fig)  # 워드클라우드 생성 함수 호출하여 출력
