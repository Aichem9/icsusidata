import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="수시 전형 결과 시각화", layout="wide")
st.title("\ud559\ubc8c\ubcc0 \ub300\ud559 \uc218\uc2dc \uacb0\uacfc \uc2dc\uac01\ud654")

uploaded_files = st.file_uploader("\ud30c\uc77c\uc744 \uc5ec\ub7ec \uac1c \uc5c5\ub85c\ub4dc\ud574\uc8fc\uc138\uc694 (.xlsx)", type=["xlsx"], accept_multiple_files=True)

@st.cache_data
def load_and_combine(files):
    dfs = []
    for file in files:
        try:
            df = pd.read_excel(file, sheet_name=None)
            sheet = list(df.keys())[0]
            df = df[sheet].copy()
            year = int(''.join([s for s in str(file.name) if s.isdigit()])[:4])
            df['년도'] = year
            dfs.append(df)
        except:
            st.warning(f"{file.name} \ud30c\uc77c\uc744 \ucc98\ub9ac\ud560 \uc218 \uc5c6\uc5b4\uc694.")
    return pd.concat(dfs, ignore_index=True)

if uploaded_files:
    data = load_and_combine(uploaded_files)

    required_columns = ['대학', '전과목', '최종', '년도']
    for col in required_columns:
        if col not in data.columns:
            st.error(f"필수 컬럼 {col} 이(가) 누락되었습니다.")

    data = data.dropna(subset=['전과목', '최종', '대학'])
    data['전과목'] = pd.to_numeric(data['전과목'], errors='coerce')
    data = data.dropna(subset=['전과목'])

    years = sorted(data['년도'].unique())
    selected_years = st.multiselect("\ubcf4\uace0\uc790 \ud55c \ub144\ub3c4\ub97c \uc120\ud0dd\ud574\uc8fc\uc138\uc694", years, default=years)
    filtered_data = data[data['년도'].isin(selected_years)]

    # 선택 필터 확장
    대학_list = sorted(filtered_data['대학'].unique())
    선택_대학 = st.multiselect("\ub300\ud559 \uc120\ud0dd (\uc120\ud0dd\ud558\uc9c0 \uc54a\uc73c\uba74 \uc804\uccb4)", 대학_list, default=대학_list)
    filtered_data = filtered_data[filtered_data['대학'].isin(선택_대학)]

    if '전형명' in filtered_data.columns:
        전형_list = sorted(filtered_data['전형명'].dropna().unique())
        선택_전형 = st.multiselect("전형명 선택 (선택하지 않으면 전체)", 전형_list, default=전형_list)
        filtered_data = filtered_data[filtered_data['전형명'].isin(선택_전형)]

    if '계열' in filtered_data.columns:
        계열_list = sorted(filtered_data['계열'].dropna().unique())
        선택_계열 = st.multiselect("계열 선택 (선택하지 않으면 전체)", 계열_list, default=계열_list)
        filtered_data = filtered_data[filtered_data['계열'].isin(선택_계열)]

    if '지역' in filtered_data.columns:
        지역_list = sorted(filtered_data['지역'].dropna().unique())
        선택_지역 = st.multiselect("지역 선택 (선택하지 않으면 전체)", 지역_list, default=지역_list)
        filtered_data = filtered_data[filtered_data['지역'].isin(선택_지역)]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("\ud569\uaca9\uc0ac \uc804\uacfc\ubaa9 \uc2dc\uac01\ud654")
        pass_df = filtered_data[filtered_data['최종'] == '합']
        if not pass_df.empty:
            fig1 = px.box(pass_df, x='대학', y='전과목', color='년도', points='all')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("\ud569\uaca9\uc0ac \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.")

    with col2:
        st.subheader("\ubd88\ud569\uaca9\uc0ac \uc804\uacfc\ubaa9 \uc2dc\uac01\ud654")
        fail_df = filtered_data[filtered_data['최종'] == '불']
        if not fail_df.empty:
            fig2 = px.box(fail_df, x='대학', y='전과목', color='년도', points='all')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("\ubd88\ud569\uaca9\uc0ac \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.")

    with st.expander("\ud574\ub2f9 \ub370\uc774\ud130 \ubcf4\uae30"):
        st.dataframe(filtered_data.sort_values(by=['년도', '대학']))

    st.subheader("\ud559\ubc8c\ubcc0 \ud569\uaca9\ub960 & \ud3c9\uade0 \uc131\uc801")
    agg = filtered_data.groupby(['년도', '대학']).agg(합격률=('최종', lambda x: (x == '합').mean() * 100), 평균성적=('전과목', 'mean')).reset_index()
    st.dataframe(agg)
    fig3 = px.bar(agg, x='대학', y='합격률', color='년도', barmode='group', title="합격률 비교")
    st.plotly_chart(fig3, use_container_width=True)
    fig4 = px.line(agg, x='대학', y='평균성적', color='년도', markers=True, title="대학별 평균 성적 추이")
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("과목별 성적 분포 비교")
    과목들 = ['국수영사', '국수영과']
    available_cols = [col for col in 과목들 if col in filtered_data.columns]
    for subject in available_cols:
        st.markdown(f"#### {subject} 성적 분포 (합격자 기준)")
        sub_df = filtered_data[(filtered_data['최종'] == '합') & (filtered_data[subject].notna())]
        sub_df[subject] = pd.to_numeric(sub_df[subject], errors='coerce')
        fig_sub = px.box(sub_df, x='대학', y=subject, color='년도', points='all', title=f"대학별 {subject} 성적")
        st.plotly_chart(fig_sub, use_container_width=True)

        st.markdown(f"#### {subject} 성적 분포 (불합격자 기준)")
        sub_df_fail = filtered_data[(filtered_data['최종'] == '불') & (filtered_data[subject].notna())]
        sub_df_fail[subject] = pd.to_numeric(sub_df_fail[subject], errors='coerce')
        if not sub_df_fail.empty:
            fig_fail = px.box(sub_df_fail, x='대학', y=subject, color='년도', points='all', title=f"불합격자 {subject} 성적")
            st.plotly_chart(fig_fail, use_container_width=True)

    st.subheader("과목별 평균 성적 추이")
    for subject in available_cols:
        mean_df = filtered_data.copy()
        mean_df[subject] = pd.to_numeric(mean_df[subject], errors='coerce')
        mean_agg = mean_df.groupby(['년도', '대학'])[subject].mean().reset_index()
        fig_avg = px.line(mean_agg, x='대학', y=subject, color='년도', markers=True, title=f"{subject} 평균 성적 추이")
        st.plotly_chart(fig_avg, use_container_width=True)
