import streamlit as st
import urllib.request
import csv
import random
import time

# 1. 設定網頁標題同 Icon
st.set_page_config(page_title="今晚食咩餸老虎機", page_icon="🎰", layout="centered")

# 2. 快取數據 (每 10 分鐘先重新讀一次 Google Sheet，令個 App 反應極快)
@st.cache_data(ttl=600)
def load_menu():
    # 呢條係你個「餸菜庫」發佈出嚟嘅 CSV 連結
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9u6bG8XJG5y4KLGtdZs6NdcgUfZq3jXF_TQfdZ5ZW1LiMAwDXXJEwOJ6Fulz5iHFb3Jojl8FNMAW6/pub?output=csv"
    menu = []
    try:
        req = urllib.request.Request(csv_url)
        with urllib.request.urlopen(req) as response:
            lines = [l.decode('utf-8') for l in response.readlines()]
        
        reader = csv.reader(lines)
        headers = next(reader)
        col_index = headers.index('餸菜名') if '餸菜名' in headers else 0
            
        for row in reader:
            if len(row) > col_index and row[col_index].strip():
                menu.append(row[col_index].strip())
    except Exception as e:
        st.error("讀取餐單失敗，轉用後備名單...")
        menu = ["番茄炒蛋 🍅", "煎三文魚 🐟", "落西營盤買外賣 🥡"]
        
    return menu

# 3. 網頁 UI 介面
st.title("🎰 今晚食咩餸？")
st.write("老婆大人 Anthea 專屬！大腦死機嗰陣，㩒下面粒掣幫你諗。")
st.write("---")

# 載入餸菜庫
menu_list = load_menu()

# 4. 抽籤大掣
if st.button("🎲 幫我諗！", type="primary", use_container_width=True):
    if len(menu_list) < 3:
        st.warning("餐單唔夠 3 款餸呀！")
    else:
        # 扮老虎機攪珠，營造緊張氣氛
        with st.spinner('老虎機攪珠中... 幫緊你幫緊你...'):
            time.sleep(1.5) # 停 1.5 秒
        
        options = random.sample(menu_list, 3)
        st.success("🎉 抽中咗啦！")
        
        # 用 3 個 Column 靚靚地排好賽果
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**選擇 A**\n\n### {options[0]}")
        with col2:
            st.warning(f"**選擇 B**\n\n### {options[1]}")
        with col3:
            st.error(f"**選擇 C**\n\n### {options[2]}")
            
        st.write("---")
        st.markdown("💡 **Cap 圖掟入 WhatsApp 話畀老公知啦！**")
