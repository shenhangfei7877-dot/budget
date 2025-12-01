import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re

# 页面设置
st.set_page_config(page_title="2026预算可视化看板", layout="wide")

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
    
    /* 树形表格样式 */
    .tree-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 1.1rem;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-radius: 8px;
        overflow: hidden;
    }
    .tree-table th {
        background: linear-gradient(135deg, #0052cc 0%, #0066ff 100%);
        color: white;
        padding: 16px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 1.15rem;
        border-bottom: 3px solid #003d99;
    }
    .tree-table td {
        padding: 14px 12px;
        border-bottom: 1px solid #e8e8e8;
    }
    .tree-row-root {
        background: #f0f5ff;
        font-weight: 700;
        font-size: 1.2rem;
        color: #0052cc;
    }
    .tree-row-parent {
        background: #fff9e6;
        font-weight: 600;
        color: #d46b08;
    }
    .tree-row-child {
        background: white;
        color: #333;
    }
    .tree-row-normal {
        background: white;
        color: #333;
    }
    .tree-row:hover {
        background: #f5f5f5 !important;
    }
    .tree-indent-0 { padding-left: 12px; }
    .tree-indent-1 { padding-left: 32px; }
    .tree-indent-2 { padding-left: 52px; }
    .tree-icon {
        display: inline-block;
        width: 16px;
        margin-right: 8px;
        font-weight: bold;
    }
    .progress-bar-container {
        width: 100%;
        background: #e8e8e8;
        border-radius: 4px;
        height: 24px;
        position: relative;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 8px;
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .progress-bar-high { background: linear-gradient(90deg, #0052cc 0%, #0066ff 100%); }
    .progress-bar-medium { background: linear-gradient(90deg, #4a90e2 0%, #74b9ff 100%); }
    .progress-bar-low { background: linear-gradient(90deg, #95a5a6 0%, #b0bec5 100%); }
    .amount-cell {
        font-family: 'Consolas', 'Monaco', monospace;
        font-weight: 600;
        text-align: right;
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
    if pd.isna(text) or text == 0 or text == '' or str(text).strip() == '':
        return "无"
    
    text = str(text).strip()
    
    # 检查是否包含数字顿号格式
    if not re.search(r'\d+、', text):
        # 如果没有数字顿号，直接返回原文本
        return f'<div style="color:{color}; line-height:2;">{text}</div>'
    
    # 按照数字顿号分割文本
    parts = re.split(r'(\d+、)', text)
    
    result = '<div style="line-height:2;">'
    i = 0
    while i < len(parts):
        if re.match(r'\d+、', parts[i]):
            # 这是一个编号
            number = parts[i]
            content = parts[i+1] if i+1 < len(parts) else ''
            result += f'<div style="margin-top:8px; color:{color};"><b>{number}</b>{content.strip()}</div>'
            i += 2
        else:
            # 这是第一段文本（在第一个编号之前）
            if parts[i].strip():
                result += f'<div style="color:{color};">{parts[i].strip()}</div>'
            i += 1
    
    result += '</div>'
    return result

def load_data(uploaded_file):
    try:
        # 关键修改：header=[11, 12] 读取两行作为表头（处理合并单元格）
        df = pd.read_excel(uploaded_file, header=[11, 12], engine='openpyxl')
        
        # 展平列名
        df = clean_header(df)
        
        # 显示成功信息
        st.sidebar.success(f" 文件读取成功：{len(df)} 行数据")
        
        # 过滤掉空行
        if '公司简称' in df.columns:
            df = df[df['公司简称'].notna()]
            st.sidebar.info(f" 共 {len(df)} 个公司主体")
            return df
        else:
            st.error("未找到'公司简称'列，请检查表头格式是否变动。")
            return None
    except Exception as e:
        st.error(f"文件读取失败: {str(e)}")
        return None

# --- 侧边栏 ---
st.sidebar.header("控制面板")
uploaded_file = st.sidebar.file_uploader("📂 上传2026预算小结 (Excel)", type=["xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        companies = df['公司简称'].unique().tolist()
        selected_company = st.sidebar.selectbox("选择公司主体", companies)
        
        # 获取选中行数据
        row = df[df['公司简称'] == selected_company].iloc[0]
        
        # --- 顶部标题区 ---
        st.title(f"{selected_company}")
        st.markdown("2026年全面预算概览")
        
        # --- 第一部分：核心指标 ---
        # 数据提取
        rev_26 = pd.to_numeric(row.get('2026年营业收入'), errors='coerce')
        rev_25 = pd.to_numeric(row.get('2025年营业收入'), errors='coerce')
        prof_26 = pd.to_numeric(row.get('2026净利润'), errors='coerce')
        prof_25 = pd.to_numeric(row.get('2025净利润'), errors='coerce')
        margin_26 = row.get('2026毛利率', 0)
        margin_25 = row.get('2025毛利率', 0)
        
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
            m_val_26 = float(margin_26) * 100 if float(margin_26) < 5 else float(margin_26)
            margin_26_str = f"{m_val_26:.0f}%"  # 整数位
        except:
            margin_26_str = str(margin_26)
        
        try:
            m_val_25 = float(margin_25) * 100 if float(margin_25) < 5 else float(margin_25)
            margin_25_str = f"{m_val_25:.0f}%"  # 整数位
        except:
            margin_25_str = str(margin_25)

        # 显示指标
        k1, k2, k3 = st.columns(3)
        
        with k1:
            st.markdown(f"###  2026年营业收入")
            st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{rev_26:,.0f} 万元</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.1rem; color:#666; margin-bottom:5px;'>2025年：{rev_25:,.0f} 万元</div>", unsafe_allow_html=True)
            st.markdown(rev_change, unsafe_allow_html=True)
        
        with k2:
            st.markdown(f"###  2026年净利润")
            st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{prof_26:,.0f} 万元</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.1rem; color:#666; margin-bottom:5px;'>2025年：{prof_25:,.0f} 万元</div>", unsafe_allow_html=True)
            st.markdown(prof_change, unsafe_allow_html=True)
        
        with k3:
            st.markdown(f"###  2026年综合毛利率") 
            st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; margin:10px 0; color:#0052cc;'>{margin_26_str}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.1rem; font-weight:bold; color:#333; margin-bottom:5px;'>2025年：{margin_25_str}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # --- 第二部分：收入分析 ---
        st.markdown('<div class="section-title"> 收入分析</div>', unsafe_allow_html=True)
        
        # 收入折线图 - 独占整行
        st.markdown("#####  季度收入趋势对比")
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
            st.markdown("#####  收入变动备注")
            remark_text = row.get('备注1：收入环比变动原因', '无')
            st.info(f"**环比变动原因：**\n\n{remark_text}")
        
        with col_pie:
            st.markdown("#####  集团内外收入分布")
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
        st.markdown('<div class="section-title"> 费用与成本</div>', unsafe_allow_html=True)
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
            st.markdown("#####  费用明细说明")
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
        
        # --- 固定成本费用部分 (树形表格) ---
        st.markdown("---")
        st.markdown('<div class="section-title">固定成本费用</div>', unsafe_allow_html=True)
        
        # 提取固定成本数据
        fixed_cost_total = pd.to_numeric(row.get('固定成本费用合计', 0), errors='coerce')
        fixed_cost_total = 0 if pd.isna(fixed_cost_total) else fixed_cost_total
        
        # 各项固定成本数据
        salary_total = pd.to_numeric(row.get('职工薪酬-小计', 0), errors='coerce')
        salary_total = 0 if pd.isna(salary_total) else salary_total
        
        salary_sales = pd.to_numeric(row.get('职工薪酬-销售', 0), errors='coerce')
        salary_sales = 0 if pd.isna(salary_sales) else salary_sales
        
        salary_admin = pd.to_numeric(row.get('职工薪酬-管理', 0), errors='coerce')
        salary_admin = 0 if pd.isna(salary_admin) else salary_admin
        
        salary_production = pd.to_numeric(row.get('职工薪酬-生产', 0), errors='coerce')
        salary_production = 0 if pd.isna(salary_production) else salary_production
        
        salary_rd = pd.to_numeric(row.get('职工薪酬-研发', 0), errors='coerce')
        salary_rd = 0 if pd.isna(salary_rd) else salary_rd
        
        depreciation = pd.to_numeric(row.get('折旧费', 0), errors='coerce')
        depreciation = 0 if pd.isna(depreciation) else depreciation
        
        rent = pd.to_numeric(row.get('房租物业费', 0), errors='coerce')
        rent = 0 if pd.isna(rent) else rent
        
        other_cost = pd.to_numeric(row.get('其他', 0), errors='coerce')
        other_cost = 0 if pd.isna(other_cost) else other_cost
        
        long_term_deferred = pd.to_numeric(row.get('长期待摊费用', 0), errors='coerce')
        long_term_deferred = 0 if pd.isna(long_term_deferred) else long_term_deferred
        
        amortization = pd.to_numeric(row.get('无形资产摊销', 0), errors='coerce')
        amortization = 0 if pd.isna(amortization) else amortization
        
        # 树形表格CSS样式
        tree_table_css = """
        <style>
            .tree-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 1.1rem;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border-radius: 8px;
                overflow: hidden;
            }
            .tree-table th {
                background: linear-gradient(135deg, #0052cc 0%, #0066ff 100%);
                color: white;
                padding: 16px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 1.15rem;
                border-bottom: 3px solid #003d99;
            }
            .tree-table td {
                padding: 14px 12px;
                border-bottom: 1px solid #e8e8e8;
            }
            .tree-row-root {
                background: #f0f5ff;
                font-weight: 700;
                font-size: 1.2rem;
                color: #0052cc;
            }
            .tree-row-parent {
                background: #fff9e6;
                font-weight: 600;
                color: #d46b08;
            }
            .tree-row-child {
                background: white;
                color: #333;
            }
            .tree-row-normal {
                background: white;
                color: #333;
            }
            .tree-row:hover {
                background: #f5f5f5 !important;
            }
            .tree-indent-0 { padding-left: 12px; }
            .tree-indent-1 { padding-left: 32px; }
            .tree-indent-2 { padding-left: 52px; }
            .tree-icon {
                display: inline-block;
                width: 16px;
                margin-right: 8px;
                font-weight: bold;
            }
            .progress-bar-container {
                width: 100%;
                background: #e8e8e8;
                border-radius: 4px;
                height: 24px;
                position: relative;
                overflow: hidden;
            }
            .progress-bar {
                height: 100%;
                border-radius: 4px;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
                color: white;
                font-weight: 600;
                font-size: 0.95rem;
            }
            .progress-bar-high { background: linear-gradient(90deg, #0052cc 0%, #0066ff 100%); }
            .progress-bar-medium { background: linear-gradient(90deg, #4a90e2 0%, #74b9ff 100%); }
            .progress-bar-low { background: linear-gradient(90deg, #95a5a6 0%, #b0bec5 100%); }
            .amount-cell {
                font-family: 'Consolas', 'Monaco', monospace;
                font-weight: 600;
                text-align: right;
            }
        </style>
        """
        st.markdown(tree_table_css, unsafe_allow_html=True)
        
        # 定义辅助函数
        def format_amount(value):
            if value == 0:
                return ""
            return f"{value:,.0f}"
        
        def get_percentage(value, total):
            if total == 0:
                return 0
            return (value / total) * 100
        
        def render_progress_bar(percentage):
            if percentage >= 50:
                bar_class = "progress-bar-high"
            elif percentage >= 20:
                bar_class = "progress-bar-medium"
            else:
                bar_class = "progress-bar-low"
            
            bar_html = f'<div class="progress-bar-container"><div class="progress-bar {bar_class}" style="width: {percentage}%;">{percentage:.0f}%</div></div>'
            return bar_html
        
        # 生成表格HTML
        table_html = '<table class="tree-table"><thead><tr><th style="width: 45%;">成本项目</th><th style="width: 25%; text-align: right;">金额(万元)</th><th style="width: 30%;">占比结构</th></tr></thead><tbody>'
        
        # 根节点
        total_pct = 100
        table_html += f'<tr class="tree-row tree-row-root"><td class="tree-indent-0"><span class="tree-icon">▼</span>固定成本费用合计</td><td class="amount-cell">{format_amount(fixed_cost_total)}</td><td>{render_progress_bar(total_pct)}</td></tr>'
        
        # 职工薪酬小计
        salary_pct = get_percentage(salary_total, fixed_cost_total)
        table_html += f'<tr class="tree-row tree-row-parent"><td class="tree-indent-1"><span class="tree-icon">▶</span>职工薪酬-小计</td><td class="amount-cell">{format_amount(salary_total)}</td><td>{render_progress_bar(salary_pct)}</td></tr>'
        
        # 职工薪酬子项
        salary_items = [
            ('├── 职工薪酬-销售', salary_sales),
            ('├── 职工薪酬-管理', salary_admin),
            ('├── 职工薪酬-生产', salary_production),
            ('└── 职工薪酬-研发', salary_rd)
        ]
        
        for item_name, item_value in salary_items:
            item_pct = get_percentage(item_value, fixed_cost_total)
            table_html += f'<tr class="tree-row tree-row-child"><td class="tree-indent-2">{item_name}</td><td class="amount-cell">{format_amount(item_value)}</td><td>{render_progress_bar(item_pct)}</td></tr>'
        
        # 其他固定成本项目
        other_items = [
            ('折旧费', depreciation),
            ('房租物业费', rent),
            ('其他', other_cost),
            ('长期待摊费用', long_term_deferred),
            ('无形资产摊销', amortization)
        ]
        
        for item_name, item_value in other_items:
            item_pct = get_percentage(item_value, fixed_cost_total)
            table_html += f'<tr class="tree-row tree-row-normal"><td class="tree-indent-1">{item_name}</td><td class="amount-cell">{format_amount(item_value)}</td><td>{render_progress_bar(item_pct)}</td></tr>'
        
        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # --- 资金缺口部分（费用后面）结合现金流量情况 ---
        st.markdown("---")
        st.markdown('<div class="section-title"> 资金投入与现金流量情况</div>', unsafe_allow_html=True)
        
        # 第一行：现金流量指标
        cash_col1, cash_col2, cash_col3, cash_col4 = st.columns(4)
        
        operating_cash = pd.to_numeric(row.get('经营活动产生的现金流量净额', 0), errors='coerce')
        operating_cash = 0 if pd.isna(operating_cash) else operating_cash
        
        investing_cash = pd.to_numeric(row.get('投资活动产生的现金流量净额', 0), errors='coerce')
        investing_cash = 0 if pd.isna(investing_cash) else investing_cash
        
        financing_cash = pd.to_numeric(row.get('筹资活动产生的现金流量净额', 0), errors='coerce')
        financing_cash = 0 if pd.isna(financing_cash) else financing_cash
        
        cash_gap_raw = row.get('资金投入（缺口）', 0)
        # 处理NaN值
        if pd.isna(cash_gap_raw) or cash_gap_raw == '' or str(cash_gap_raw).lower() == 'nan':
            cash_gap = 0
        else:
            try:
                cash_gap = pd.to_numeric(cash_gap_raw, errors='coerce')
                cash_gap = 0 if pd.isna(cash_gap) else cash_gap
            except:
                cash_gap = 0
        
        with cash_col1:
            st.markdown("#####  经营活动现金流")
            color = '#52c41a' if operating_cash >= 0 else '#ff4d4f'
            st.markdown(f"<div style='font-size:1.6rem; font-weight:bold; color:{color};'>{operating_cash:,.0f} 万元</div>", unsafe_allow_html=True)
        
        with cash_col2:
            st.markdown("#####  投资活动现金流")
            color = '#52c41a' if investing_cash >= 0 else '#ff4d4f'
            st.markdown(f"<div style='font-size:1.6rem; font-weight:bold; color:{color};'>{investing_cash:,.0f} 万元</div>", unsafe_allow_html=True)
        
        with cash_col3:
            st.markdown("#####  筹资活动现金流")
            color = '#52c41a' if financing_cash >= 0 else '#ff4d4f'
            st.markdown(f"<div style='font-size:1.6rem; font-weight:bold; color:{color};'>{financing_cash:,.0f} 万元</div>", unsafe_allow_html=True)
        
        with cash_col4:
            st.markdown("#####  资金缺口/投入")
            st.markdown(f"<div style='font-size:1.6rem; font-weight:bold; color:#0052cc;'>{cash_gap:,.0f} 万元</div>", unsafe_allow_html=True)
        
        # 第二行：资金缺口说明
        st.markdown("#####  资金缺口说明")
        fund_note = get_col_contains(row, "备注5：")
        if fund_note == "无":
            fund_note = get_col_contains(row, "资金缺口")
        # 资金缺口说明使用黑色字体
        st.markdown(f"<div style='color:#1f1f1f; font-size:1rem; background:#f0f5ff; padding:20px; border-radius:8px;'>{format_text_list(fund_note, color='#1f1f1f')}</div>", unsafe_allow_html=True)

        # --- 第四部分：底部小结 ---
        st.markdown("---")
        st.markdown("<h3 style='font-size:1.5rem; font-weight:bold;'> 2026年预算执行小结</h3>", unsafe_allow_html=True)
        summary_text = row.get('小结', '暂无小结')
        # 小结部分使用黑色字体，按"1、2、3、"分段
        st.markdown(f"<div style='font-size:1.1rem; line-height:1.8; color:#1f1f1f;'>{format_text_list(summary_text, color='#1f1f1f')}</div>", unsafe_allow_html=True)
        
        # --- 提请管理层关注 (放在预算小结下方) ---
        st.markdown("---")
        st.markdown("<h3 style='font-size:1.5rem; font-weight:bold;'> 提请管理层关注</h3>", unsafe_allow_html=True)
        attention_text = row.get('提请管理层关注', '无')
        st.markdown(f"<div class='attention-box'>{format_text_list(attention_text, color='#d46b08')}</div>", unsafe_allow_html=True)

else:
    st.info("请在左侧上传 Excel 文件 (2026预算小结.xlsx)")
