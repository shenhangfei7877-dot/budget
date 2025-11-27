import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re

# 页面设置
st.set_page_config(page_title="2026预算可视化看板", layout="wide", page_icon="📊")

# CSS样式美化
st.markdown("""
<style>
    /* 全局配色方案 */
    :root {
        --primary-blue: #0052cc;
        --light-blue-bg: #e6f0ff;
        --rise-red: #ff4d4f;
        --fall-green: #52c41a;
        --text-dark: #1f1f1f;
        --text-gray: #666;
        --border-light: #d9d9d9;
    }
    
    /* KPI卡片样式 */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid var(--border-light);
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.08);
        transition: all 0.3s ease;
        margin-bottom: 16px;
    }
    .kpi-card:hover {
        box-shadow: 0 6px 20px rgba(0, 82, 204, 0.15);
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 0.95rem;
        color: var(--text-gray);
        font-weight: 500;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value-2026 {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-blue);
        margin: 8px 0;
        line-height: 1.2;
    }
    .kpi-value-2025 {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-gray);
        margin: 4px 0;
    }
    .kpi-change {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 8px;
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    .kpi-change.rise {
        color: var(--rise-red);
        background-color: rgba(255, 77, 79, 0.1);
    }
    .kpi-change.fall {
        color: var(--fall-green);
        background-color: rgba(82, 196, 26, 0.1);
    }
    
    /* 管理层关注区域 */
    .attention-box {
        background: linear-gradient(135deg, #fff9e6 0%, #fffbf0 100%);
        padding: 24px;
        border-radius: 12px;
        border-left: 4px solid #faad14;
        box-shadow: 0 2px 8px rgba(250, 173, 20, 0.1);
    }
    .attention-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #d46b08;
        margin-bottom: 12px;
    }
    
    /* 分区标题 */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--primary-blue);
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 3px solid var(--primary-blue);
    }
    
    /* 小结区域 */
    .summary-box {
        background: linear-gradient(135deg, var(--light-blue-bg) 0%, #f0f5ff 100%);
        padding: 28px;
        border-radius: 12px;
        border: 1px solid #adc6ff;
        box-shadow: 0 2px 8px rgba(0, 82, 204, 0.08);
    }
    .summary-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--primary-blue);
        margin-bottom: 16px;
    }
    .summary-content {
        font-size: 1.15rem;
        line-height: 2;
        color: var(--text-dark);
    }
    
    /* Streamlit原生组件优化 */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--primary-blue) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: var(--text-gray) !important;
        font-weight: 500 !important;
    }
    
    /* 侧边栏优化 */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
    
    /* 通用文本样式 */
    .metric-unit {
        font-size: 0.9rem;
        color: var(--text-gray);
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

def clean_header(df):
    """
    处理Excel的多级表头（合并单元格），将其展平为单层列名
    """
    new_columns = []
    for col in df.columns:
        # col 是一个元组，例如 ('2025年度收入按季度分', '1Q25') 或 ('2026年\n营业收入', 'Unnamed: 5_level_1')
        c1 = str(col[0]).strip()
        c2 = str(col[1]).strip()
        
        # 逻辑：如果第二行是 Unnamed（即没有子标题），就用第一行
        # 如果第二行有实意（例如 1Q25），就优先用第二行
        if 'Unnamed' in c2 or c2 == 'nan':
            final_col = c1
        else:
            final_col = c2
            
        # 清理换行符和多余空格
        final_col = final_col.replace('\n', '').replace('\r', '').replace(' ', '')
        new_columns.append(final_col)
    
    df.columns = new_columns
    return df

def format_text_list(text, color='inherit'):
    """
    将 '1、xxx 2、xxx' 格式的文本转换为换行显示的HTML
    按"1、""2、""3、"等数字顿号分段，支持自定义颜色
    """
    if pd.isna(text) or text == 0:
        return "无"
    text = str(text)
    # 使用正则在"数字、"前加换行和段落间距
    formatted = re.sub(r'(\d+、)', r'<div style="margin-top:12px; color:' + color + ';"><b>\1</b>', text)
    # 为每个段落添加结束标签（在下一个段落开始前或文本末尾）
    formatted = re.sub(r'</div><div', r'</div></div><div', formatted)
    # 如果没有以div开始，说明第一段没有数字序号，补上开始标签
    if not formatted.startswith('<div'):
        formatted = '<div style="color:' + color + ';">' + formatted
    # 确保最后有结束标签
    if not formatted.endswith('</div>'):
        formatted += '</div>'
    return formatted

def load_data(uploaded_file):
    try:
        # 关键修改：header=[11, 12] 读取两行作为表头（处理合并单元格）
        df = pd.read_excel(uploaded_file, header=[11, 12], engine='openpyxl')
        
        # 展平列名
        df = clean_header(df)
        
        # 显示成功信息
        st.sidebar.success(f"✅ 文件读取成功：{len(df)} 行数据")
        
        # 过滤掉空行
        if '公司简称' in df.columns:
            df = df[df['公司简称'].notna()]
            st.sidebar.info(f"📊 共 {len(df)} 个公司主体")
            return df
        else:
            st.error("未找到'公司简称'列，请检查表头格式是否变动。")
            return None
    except Exception as e:
        st.error(f"文件读取失败: {str(e)}")
        return None

# --- 侧边栏 ---
st.sidebar.header("🎛️ 控制面板")
uploaded_file = st.sidebar.file_uploader("📂 上传2026预算小结 (Excel)", type=["xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        companies = df['公司简称'].unique().tolist()
        selected_company = st.sidebar.selectbox("🏢 选择公司主体", companies)
        
        # 获取选中行数据
        row = df[df['公司简称'] == selected_company].iloc[0]
        
        # --- 顶部标题区 ---
        st.title(f"{selected_company}")
        st.markdown("2026年全面预算概览")
        
        # --- 第一部分：核心指标 & 管理层关注 ---
        # 布局：左侧 3个KPI卡片，右侧 1个大的管理层关注框
        top_left, top_right = st.columns([3, 2])
        
        with top_left:
            # 数据提取
            rev_26 = pd.to_numeric(row.get('2026年营业收入'), errors='coerce')
            rev_25 = pd.to_numeric(row.get('2025年营业收入'), errors='coerce')
            prof_26 = pd.to_numeric(row.get('2026净利润'), errors='coerce')
            prof_25 = pd.to_numeric(row.get('2025净利润'), errors='coerce')
            margin_26 = row.get('2026毛利率', 0)
            
            # 格式化 - 使用文字显示变化
            rev_26_str = f"**{rev_26:,.0f}**" if pd.notna(rev_26) else "-"
            rev_25_str = f"**{rev_25:,.0f}**" if pd.notna(rev_25) else "-"
            
            if pd.notna(rev_26) and pd.notna(rev_25):
                delta = rev_26 - rev_25
                if delta > 0:
                    rev_change = f'<span class="metric-change increase">同比增加 {delta:,.0f} 万元</span>'
                elif delta < 0:
                    rev_change = f'<span class="metric-change decrease">同比减少 {abs(delta):,.0f} 万元</span>'
                else:
                    rev_change = '<span class="metric-change">与去年持平</span>'
            else:
                rev_change = "-"
            
            prof_26_str = f"**{prof_26:,.0f}**" if pd.notna(prof_26) else "-"
            prof_25_str = f"**{prof_25:,.0f}**" if pd.notna(prof_25) else "-"
            
            if pd.notna(prof_26) and pd.notna(prof_25):
                delta = prof_26 - prof_25
                if delta > 0:
                    prof_change = f'<span class="metric-change increase">同比增加 {delta:,.0f} 万元</span>'
                elif delta < 0:
                    prof_change = f'<span class="metric-change decrease">同比减少 {abs(delta):,.0f} 万元</span>'
                else:
                    prof_change = '<span class="metric-change">与去年持平</span>'
            else:
                prof_change = "-"
            
            try:
                m_val = float(margin_26) * 100 if float(margin_26) < 5 else float(margin_26)
                margin_str = f"{m_val:.0f}%"  # 整数位
            except:
                margin_str = str(margin_26)

            # 显示指标
            k1, k2, k3 = st.columns(3)
            
            with k1:
                st.markdown(f"### 💰 2026年营业收入")
                st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{rev_26:,.0f} 万元</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:1.1rem; color:#666; margin-bottom:5px;'>2025年：{rev_25:,.0f} 万元</div>", unsafe_allow_html=True)
                st.markdown(rev_change, unsafe_allow_html=True)
            
            with k2:
                st.markdown(f"### 💵 2026年净利润")
                st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{prof_26:,.0f} 万元</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:1.1rem; color:#666; margin-bottom:5px;'>2025年：{prof_25:,.0f} 万元</div>", unsafe_allow_html=True)
                st.markdown(prof_change, unsafe_allow_html=True)
            
            with k3:
                st.markdown(f"### 📊 2026年综合毛利率")
                st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{margin_str}</div>", unsafe_allow_html=True)

        with top_right:
            st.markdown("#### ⚠️ 提请管理层关注")
            attention_text = row.get('提请管理层关注', '无')
            st.markdown(format_text_list(attention_text), unsafe_allow_html=True)

        st.markdown("---")

        # --- 第二部分：收入分析 ---
        st.markdown('<div class="section-title">📈 收入分析</div>', unsafe_allow_html=True)
        
        # 收入折线图 - 独占整行
        st.markdown("##### 📊 季度收入趋势对比")
        quarters = ['1Q', '2Q', '3Q', '4Q']
        y25 = [pd.to_numeric(row.get(f'{q}25'), errors='coerce') for q in quarters]
        y26 = [pd.to_numeric(row.get(f'{q}26'), errors='coerce') for q in quarters]
        # 填充0
        y25 = [x if pd.notna(x) else 0 for x in y25]
        y26 = [x if pd.notna(x) else 0 for x in y26]

        fig = go.Figure()
        # 2025灰色线条
        fig.add_trace(go.Scatter(
            x=quarters, y=y25, 
            name='2025年 (预估)', 
            mode='lines+markers+text',
            line=dict(color='#95a5a6', width=4),
            marker=dict(size=12, color='#95a5a6'),
            text=[f'{v:,.0f} 万元' for v in y25],
            textposition='top center',
            textfont=dict(size=14, color='#666')
        ))
        # 2026蓝色线条
        fig.add_trace(go.Scatter(
            x=quarters, y=y26, 
            name='2026年 (预算)', 
            mode='lines+markers+text',
            line=dict(color='#0052cc', width=4),
            marker=dict(size=12, color='#0052cc'),
            text=[f'{v:,.0f} 万元' for v in y26],
            textposition='top center',
            textfont=dict(size=16, color='#0052cc')
        ))
        fig.update_layout(
            height=400, 
            margin=dict(l=60, r=60, t=60, b=60),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="center", 
                x=0.5,
                font=dict(size=14)
            ),
            xaxis=dict(
                title=dict(text="季度", font=dict(size=16)),
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                title=dict(text="收入 (万元)", font=dict(size=16)),
                tickfont=dict(size=14)
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 备注和集团内外占比放在折线图下方
        col_remark, col_pie = st.columns([1, 1])
        
        with col_remark:
            st.markdown("##### 📝 收入变动备注")
            remark_text = row.get('备注1：收入环比变动原因', '无')
            st.info(f"**环比变动原因：**\n\n{remark_text}")
        
        with col_pie:
            st.markdown("##### 🏛️ 集团内外收入分布")
            in_group = pd.to_numeric(row.get('集团内'), errors='coerce')
            out_group = pd.to_numeric(row.get('集团外'), errors='coerce')
            
            if pd.notna(in_group) and pd.notna(out_group) and (in_group + out_group) > 0:
                group_df = pd.DataFrame({
                    '类型': ['集团内', '集团外'],
                    '金额': [in_group, out_group]
                })
                fig_group = px.pie(
                    group_df, 
                    values='金额', 
                    names='类型',
                    color_discrete_sequence=['#0052cc', '#95a5a6']
                )
                fig_group.update_traces(
                    textposition='inside',
                    textinfo='label+value+percent',
                    texttemplate='<b>%{label}</b><br>%{value:,.0f} 万元<br>(%{percent})',
                    textfont_size=14
                )
                fig_group.update_layout(
                    height=320, 
                    margin=dict(l=10, r=10, t=10, b=10), 
                    showlegend=False
                )
                st.plotly_chart(fig_group, use_container_width=True)
            else:
                st.info("暂无集团内外数据")

        # --- 第三部分：费用分析 (左图右文) ---
        st.markdown("---")
        st.markdown('<div class="section-title">💰 费用与成本</div>', unsafe_allow_html=True)
        col_exp_chart, col_exp_text = st.columns([1, 1])

        with col_exp_chart:
            # 准备费用数据
            sale = pd.to_numeric(row.get('2026销售费用'), errors='coerce') or 0
            admin = pd.to_numeric(row.get('2026管理费用'), errors='coerce') or 0
            rd = pd.to_numeric(row.get('2026研发费用'), errors='coerce') or 0
            
            exp_df = pd.DataFrame({
                'Type': ['销售', '管理', '研发'],
                'Value': [sale, admin, rd]
            })
            
            if exp_df['Value'].sum() > 0:
                fig_pie = px.pie(
                    exp_df, 
                    values='Value', 
                    names='Type', 
                    title="2026年期间费用结构",
                    color_discrete_sequence=['#0052cc', '#4a90e2', '#74b9ff']
                )
                fig_pie.update_traces(
                    textposition='inside', 
                    textinfo='label+value+percent',
                    texttemplate='<b>%{label}</b><br>%{value:,.0f} 万元<br>(%{percent})',
                    textfont_size=14
                )
                fig_pie.update_layout(
                    height=380, 
                    margin=dict(l=20, r=20, t=50, b=20),
                    title_font_size=16
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.write("暂无费用数据")

        with col_exp_text:
            st.markdown("##### 📋 费用明细说明")
            tab1, tab2, tab3, tab4 = st.tabs(["销售", "管理", "研发", "毛利备注"])
            
            # 使用模糊匹配查找备注列（因为列名太长，直接用包含匹配）
            def get_col_contains(df_row, keyword):
                for c in df_row.index:
                    if keyword in str(c):
                        return df_row[c]
                return "无"

            with tab1:
                sale_rate = row.get('2026年销售费用率', 0)
                try:
                    rate_val = float(sale_rate) * 100 if float(sale_rate) < 5 else float(sale_rate)
                    rate_str = f"{rate_val:.0f}%"  # 整数位
                except:
                    rate_str = str(sale_rate)
                st.write(f"**金额:** {sale:,.0f} 万元 | **费率:** {rate_str}")
                note = get_col_contains(row, "备注3")
                st.markdown(format_text_list(note), unsafe_allow_html=True)
            
            with tab2:
                admin_rate = row.get('2026年管理费用率', 0)
                try:
                    rate_val = float(admin_rate) * 100 if float(admin_rate) < 5 else float(admin_rate)
                    rate_str = f"{rate_val:.0f}%"  # 整数位
                except:
                    rate_str = str(admin_rate)
                st.write(f"**金额:** {admin:,.0f} 万元 | **费率:** {rate_str}")
                note = get_col_contains(row, "备注4")
                st.markdown(format_text_list(note), unsafe_allow_html=True)

            with tab3:
                rd_rate = row.get('2026年研发费用率', 0)
                try:
                    rate_val = float(rd_rate) * 100 if float(rd_rate) < 5 else float(rd_rate)
                    rate_str = f"{rate_val:.0f}%"  # 整数位
                except:
                    rate_str = str(rd_rate)
                st.write(f"**金额:** {rd:,.0f} 万元 | **费率:** {rate_str}")
                note = get_col_contains(row, "备注5（请填写")
                st.markdown(format_text_list(note), unsafe_allow_html=True)
                
            with tab4:
                note = get_col_contains(row, "备注2")
                st.markdown(format_text_list(note), unsafe_allow_html=True)
        
        # --- 资金缺口部分（费用后面）---
        st.markdown("---")
        st.markdown('<div class="section-title">💵 资金投入情况</div>', unsafe_allow_html=True)
        fund_left, fund_right = st.columns([1, 1])
        
        with fund_left:
            cash_gap = row.get('资金投入（缺口）', '无')
            st.metric("资金缺口/投入 (万元)", str(cash_gap))
        
        with fund_right:
            st.markdown("##### 📝 资金缺口说明")
            # 查找备注5资金缺口相关
            fund_note = get_col_contains(row, "备注5：")
            if fund_note == "无":
                fund_note = get_col_contains(row, "资金缺口")
            # 资金缺口说明使用黑色字体
            st.markdown(f"<div style='color:#1f1f1f; font-size:1rem;'>{format_text_list(fund_note, color='#1f1f1f')}</div>", unsafe_allow_html=True)

        # --- 第四部分：底部小结 ---
        st.markdown("---")
        st.markdown("<h3 style='font-size:1.5rem; font-weight:bold;'>📋 2026年预算执行小结</h3>", unsafe_allow_html=True)
        summary_text = row.get('小结', '暂无小结')
        # 小结部分使用黑色字体，按"1、2、3、"分段
        st.markdown(f"<div style='font-size:1.1rem; line-height:1.8; color:#1f1f1f;'>{format_text_list(summary_text, color='#1f1f1f')}</div>", unsafe_allow_html=True)

else:
    st.info("👋 请在左侧上传 Excel 文件 (2026预算小结.xlsx)")
