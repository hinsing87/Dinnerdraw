import streamlit as st
import urllib.request
import csv
import random
import requests
import os
from urllib.parse import quote

# 1. 設定網頁標題同 Icon
st.set_page_config(page_title="今晚食咩餸", page_icon="🍽️", layout="centered")

# 2. 快取數據
@st.cache_data(ttl=600)
def load_menu():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9u6bG8XJG5y4KLGtdZs6NdcgUfZq3jXF_TQfdZ5ZW1LiMAwDXXJewOJ6FuIz5iHFb3Jojl8FNMAW6/pub?output=csv"
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
        st.error(f"讀取餐單失敗 (錯誤詳情: {e})")
        menu = ["番茄炒蛋 🍅", "煎三文魚 🐟", "落西營盤買外賣 🥡", "蒸水蛋 🥚", "西蘭花炒肉片 🥦"]
    return menu

# 3. 初始化 Session State (鎖死抽中嘅 5 個餸)
if 'options' not in st.session_state:
    st.session_state.options = []

st.title("🍽️ 今晚食咩餸？")
st.write("老婆大人 Anthea 專屬！幫你抽出 5 個選擇，鍾意邊樣就剔邊樣，再撳 SEND 直接 WhatsApp 老公！")
st.write("---")

menu_list = load_menu()

# 4. 抽籤大掣
if st.button("🎲 重新抽 5 款餸"):
    if len(menu_list) < 5:
        st.warning("餐單唔夠 5 款餸呀，幫你出晒佢！")
        st.session_state.options = menu_list
    else:
        st.session_state.options = random.sample(menu_list, 5)

# 5. 顯示選項俾老婆打勾 (Multi-select)
if st.session_state.options:
    st.write("### 👇 請選擇你想食嘅餸（可多選）：")
    
    selected_items = []
    for option in st.session_state.options:
        # 用 checkbox 做到可以剔幾個
        if st.checkbox(option):
            selected_items.append(option)
            
    st.write("---")
    
    # 6. SEND 畀老公大掣
    if st.button("📤 SEND 畀老公！", type="primary", use_container_width=True):
        if not selected_items:
            st.warning("喂喂！你最少要剔一樣先可以 SEND 㗎！")
        else:
            # 準備 WhatsApp 訊息內容
            items_str = "\n".join([f"✅ {item}" for item in selected_items])
            message = f"老婆大人 Anthea 已經落單啦！🍽️\n今晚想食：\n\n{items_str}\n\n(收到請準備！)"
            
            # 讀取 Streamlit Secrets 入面嘅 API Key
            # 兼容寫法：如果搵唔到 Secrets，就試吓搵系統環境變數
            try:
                phone = st.secrets["WHATSAPP_NUMBER"]
                api_key = st.secrets["CALLMEBOT_API_KEY"]
            except:
                phone = os.environ.get("WHATSAPP_NUMBER")
                api_key = os.environ.get("CALLMEBOT_API_KEY")
            
            if phone and api_key:
                # 呼叫 CallMeBot API 發送 WhatsApp
                url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={quote(message)}&apikey={api_key}"
                res = requests.get(url)
                
                if res.status_code == 200:
                    st.success("🎉 成功 SEND 咗畀老公啦！等食大餐啦！")
                    st.balloons() # 放氣球慶祝效果
                else:
                    st.error(f"出事！傳送失敗: {res.text}")
            else:
                st.error("⚠️ 未設定好 WHATSAPP_NUMBER 或 CALLMEBOT_API_KEY！")
