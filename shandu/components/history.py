import streamlit as st
from datetime import datetime

def render_history_tab():
    st.header("历史记录")
    
    if not st.session_state.history:
        st.info("暂无历史记录")
        return
        
    for idx, item in enumerate(reversed(st.session_state.history)):
        with st.expander(
            f"#{len(st.session_state.history)-idx} {item['type'].upper()}: {item['query'][:50]}..."
        ):
            st.markdown(item['results'])
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("删除", key=f"del_{idx}"):
                    st.session_state.history.remove(item)
                    st.rerun()
            with col1:
                st.caption(f"创建时间: {item.get('timestamp', '未知')}")