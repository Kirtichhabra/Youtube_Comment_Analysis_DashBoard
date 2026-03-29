import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Set up the page config
st.set_page_config(page_title="YouTube Comments Dashboard", layout="wide")

@st.cache_data
def load_and_process_data():
    # 1. Load the CSV file
    file_path = '/Users/admin/youtube_transacript/commentssummary.csv'
    # Using names since the CSV has a trailing comma causing a 3rd empty column
    df = pd.read_csv(file_path, names=['Raw_Comment', 'VideoID', 'Extra'], header=0)
    
    # 2. Clean the comment text
    # The CSV format is like: "comment no 1 : ""C aav se"""
    df['Comment'] = df['Raw_Comment'].str.extract(r'comment no \d+\s*:\s*""(.*?)""')
    # Fallback in case regex misses some unformatted strings
    df['Comment'] = df['Comment'].fillna(df['Raw_Comment']) 
    
    # 3. Categorize comments based on keywords
    def categorize_comment(comment):
        c = str(comment).lower().strip()
        
        # 1. Demand (Test/PDF/PYQ/Playlists/More lectures)
        if re.search(r'\b(test|pdf|pyq|playlist|playlists|lavo|lavjo|karavo|chalu rakhjo|module|video jova joiye)\b', c):
            return '1. Demand (Test/PDF/PYQ)'
        
        # 2. Course/Payment Related
        elif re.search(r'\b(course|payment|app|application|fee|purchase|bench|otopay|999|helpline|number chalu|number nthi lagto|pay)\b', c):
            return '2. Course/Payment'
        
        # 4. Negative Comments (Complaints, missing things)
        elif re.search(r'\b(nathi|bandh|bekar|boring|nakamu|aochi rakho|sari nathi)\b', c):
            return '4. Negative Comments'
        
        # 5. Thankyou/Excellent/Praise
        elif re.search(r'\b(thank|jordar|mast|saras|good|excellent|best|jakaas|salute|amganig|moj|super|nice|awesome|wah|tq|tnq|tnx|pragati|fire|maj|aabhar|congratulations)\b', c) or '🙏' in c or '❤' in c or '🔥' in c:
            return '5. Thank you / Excellent'
            
        # 3. Answer/Number Related
        elif re.search(r'^([a-d])$|^\d+/[a-d]$|\d+', c) or len(c) <= 2:
            return '3. Answer / Number'
            
        # 6. Others
        else:
            return '6. Others'
            
    df['Category'] = df['Comment'].apply(categorize_comment)
    return df

# Load data
df = load_and_process_data()

# --- DASHBOARD UI ---
st.title("📊 YouTube Comments Analysis Dashboard")
st.markdown("This dashboard automatically categorizes YouTube comments and displays insights.")

# Top-level metrics
category_counts = df['Category'].value_counts().reset_index()
category_counts.columns = ['Category', 'Count']

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Comment Distribution (Pie Chart)")
    fig = px.pie(category_counts, values='Count', names='Category', hole=0.4, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Count by Category")
    st.dataframe(category_counts, use_container_width=True, hide_index=True)
    
st.divider()

# Separate Tabs for Comments
st.subheader("View Actual Comments by Category")
tab1, tab2, tab3, tab4 = st.tabs(["Demand (Test/PDF/PYQ)", "Course & Payment", "Negative Comments", "All Comments"])

with tab1:
    st.table(df[df['Category'] == '1. Demand (Test/PDF/PYQ)'][['Comment', 'VideoID']])
    
with tab2:
    st.table(df[df['Category'] == '2. Course/Payment'][['Comment', 'VideoID']])

with tab3:
    st.table(df[df['Category'] == '4. Negative Comments'][['Comment', 'VideoID']])

with tab4:
    st.dataframe(df[['Category', 'Comment', 'VideoID']], use_container_width=True)