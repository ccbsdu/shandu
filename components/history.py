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
            if st.button("删除", key=f"del_{idx}"):
                st.session_state.history.remove(item)
                st.rerun()