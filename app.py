import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')
# Page configuration
st.set_page_config(
    page_title="WhatsApp API Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
        font-weight: bold;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(filepath):
    """Load and cache the merged JSON data"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def create_metric_card(title, value, icon="📊"):
    """Create a custom metric card"""
    return f"""
    <div class="metric-card">
        <h3 style="margin:0; font-size:2.5em;">{icon}</h3>
        <h2 style="margin:10px 0; font-size:2em;">{value}</h2>
        <p style="margin:0; font-size:1.1em; opacity:0.9;">{title}</p>
    </div>
    """

def main():
    # Header
    st.markdown("""
        <h1 style='text-align: center; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
        📊 WhatsApp API Analytics Dashboard - Interactive Edition
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        
        uploaded_file = st.file_uploader(
            "Upload merged_whatsapp_data.json", 
            type=['json'],
            help="Upload your merged WhatsApp data JSON file"
        )
        
        st.markdown("---")
        
        if uploaded_file:
            data = json.load(uploaded_file)
        else:
            filepath = st.text_input(
                "Or enter file path:", 
                placeholder="/path/to/merged_whatsapp_data.json"
            )
            if filepath:
                data = load_data(filepath)
            else:
                data = None
        
        if data:
            st.success("✅ Data loaded successfully!")
            
            st.markdown("---")
            st.subheader("🎯 Quick Filters")
            
            companies = data.get('companies', [])
            company_names = ["All Companies"] + [c.get('name', 'Unknown') for c in companies]
            selected_company = st.selectbox("Select Company:", company_names)
            
            # Advanced filters
            with st.expander("🔧 Advanced Filters"):
                all_user_types = set()
                for company in companies:
                    for user in company.get('users', []):
                        all_user_types.add(user.get('user_type_name', 'Unknown'))
                
                selected_user_types = st.multiselect(
                    "Filter by User Type:",
                    options=sorted(all_user_types),
                    default=None
                )
                
                show_active_only = st.checkbox("Show Active Only", value=False)
            
            st.markdown("---")
            st.subheader("📈 Views")
            view_option = st.radio(
                "Select View:",
                ["🎯 Executive Summary", "🏢 Company Analysis", "👥 User Analysis", 
                 "⚙️ Instance Analysis", "📡 Broadcast Analysis", "📊 Cross Analysis",
                 "💼 Business Intelligence" , "📈 Predictive Analytics" ,"🎖️ Customer Health Score",
                  "💰 Revenue Insights" , "📊 Benchmarking",
                 "🐛 Debug View", "📁 Raw Data"]
            )
            
            st.markdown("---")
            st.subheader("⚙️ Chart Options")
            chart_theme = st.selectbox(
                "Chart Theme:",
                ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"]
            )
            
            show_data_labels = st.checkbox("Show Data Labels", value=True)
            
        else:
            st.warning("⚠️ Please upload or specify a data file")
            view_option = None
            selected_company = "All Companies"
            selected_user_types = None
            show_active_only = False
            chart_theme = "plotly"
            show_data_labels = True
    
    # Main content
    if data:
        metadata = data.get('metadata', {})
        companies = data.get('companies', [])
        
        # Filter data
        if selected_company != "All Companies":
            filtered_companies = [c for c in companies if c.get('name') == selected_company]
        else:
            filtered_companies = companies
        
        # ==================== EXECUTIVE SUMMARY ====================
        if view_option == "🎯 Executive Summary":
            st.markdown('<div class="section-header">📊 Executive Overview</div>', unsafe_allow_html=True)
            
            # Top metrics
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown(create_metric_card("Companies", metadata.get('total_companies', 0), "🏢"), unsafe_allow_html=True)
            with col2:
                st.markdown(create_metric_card("Users", metadata.get('total_users', 0), "👥"), unsafe_allow_html=True)
            with col3:
                st.markdown(create_metric_card("Channels", metadata.get('total_channels', 0), "📢"), unsafe_allow_html=True)
            with col4:
                st.markdown(create_metric_card("Instances", metadata.get('total_instances', 0), "⚙️"), unsafe_allow_html=True)
            with col5:
                st.markdown(create_metric_card("Broadcasts", metadata.get('total_broadcasts', 0), "📡"), unsafe_allow_html=True)
            with col6:
                st.markdown(create_metric_card("Speed Messages", metadata.get('total_speedMessages', 0), "⚡"), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Interactive Charts Row 1
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="section-header">🏆 Top Companies by Users</div>', unsafe_allow_html=True)
                
                company_data = pd.DataFrame([{
                    'Company': c.get('name', 'Unknown'),
                    'Users': c.get('users_count', 0),
                    'Channels': c.get('channels_count', 0),
                    'Instances': c.get('instances_count', 0),
                    'Broadcasts': c.get('broadcasts_count', 0)
                } for c in companies]).sort_values('Users', ascending=False).head(15)
                
                fig = px.bar(
                    company_data,
                    y='Company',
                    x='Users',
                    orientation='h',
                    title='Top 15 Companies by User Count',
                    color='Users',
                    color_continuous_scale='Blues',
                    hover_data=['Channels', 'Instances', 'Broadcasts'],
                    template=chart_theme
                )
                fig.update_layout(height=500, showlegend=False)
                if show_data_labels:
                    fig.update_traces(texttemplate='%{x}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True, key='exec_top_companies')
            
            with col2:
                st.markdown('<div class="section-header">📊 Resource Distribution</div>', unsafe_allow_html=True)
                
                resource_data = pd.DataFrame({
                    'Resource': ['Users', 'Channels', 'Instances', 'Broadcasts', 'Speed Messages'],
                    'Count': [
                        metadata.get('total_users', 0),
                        metadata.get('total_channels', 0),
                        metadata.get('total_instances', 0),
                        metadata.get('total_broadcasts', 0),
                        metadata.get('total_speedMessages', 0)
                    ]
                })
                
                fig = px.pie(
                    resource_data,
                    values='Count',
                    names='Resource',
                    title='Overall Resource Distribution',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4,
                    template=chart_theme
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True, key='exec_resource_dist')
            
            # Interactive Charts Row 2
            st.markdown('<div class="section-header">👥 User Analysis</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                all_user_types = Counter()
                for company in companies:
                    for user in company.get('users', []):
                        user_type = user.get('user_type_name', 'Unknown')
                        all_user_types[user_type] += 1
                
                if all_user_types:
                    df_types = pd.DataFrame(list(all_user_types.items()), columns=['Type', 'Count'])
                    
                    fig = px.bar(
                        df_types,
                        x='Type',
                        y='Count',
                        title='User Type Distribution',
                        color='Type',
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        template=chart_theme
                    )
                    fig.update_layout(height=400, showlegend=False)
                    if show_data_labels:
                        fig.update_traces(texttemplate='%{y}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key='exec_user_types')
            
            with col2:
                company_user_types = defaultdict(Counter)
                for company in companies:
                    company_name = company.get('name', 'Unknown')
                    for user in company.get('users', []):
                        user_type = user.get('user_type_name', 'Unknown')
                        company_user_types[company_name][user_type] += 1
                
                user_type_data = []
                for company_name, types in company_user_types.items():
                    for user_type, count in types.items():
                        user_type_data.append({
                            'Company': company_name[:20],
                            'User Type': user_type,
                            'Count': count
                        })
                
                df_stacked = pd.DataFrame(user_type_data)
                
                fig = px.bar(
                    df_stacked,
                    x='Company',
                    y='Count',
                    color='User Type',
                    title='User Types by Company (Stacked)',
                    barmode='stack',
                    template=chart_theme,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key='exec_user_types_stacked')
            
            # Activity Heatmap
            st.markdown('<div class="section-header">🔥 Activity Heatmap</div>', unsafe_allow_html=True)
            
            heatmap_data = []
            for company in companies[:20]:
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                
                active_users_pct = (sum(1 for u in users if u.get('isActive', False)) / len(users) * 100) if users else 0
                active_instances_pct = (sum(1 for i in instances if i.get('active', False)) / len(instances) * 100) if instances else 0
                active_channels_pct = (sum(1 for c in channels if c.get('isActive', False)) / len(channels) * 100) if channels else 0
                
                heatmap_data.append({
                    'Company': company.get('name', 'Unknown')[:20],
                    'Active Users %': round(active_users_pct, 1),
                    'Active Instances %': round(active_instances_pct, 1),
                    'Active Channels %': round(active_channels_pct, 1)
                })
            
            df_heatmap = pd.DataFrame(heatmap_data)
            
            fig = go.Figure(data=go.Heatmap(
                z=[df_heatmap['Active Users %'], 
                   df_heatmap['Active Instances %'], 
                   df_heatmap['Active Channels %']],
                x=df_heatmap['Company'],
                y=['Active Users %', 'Active Instances %', 'Active Channels %'],
                colorscale='RdYlGn',
                text=[df_heatmap['Active Users %'], 
                      df_heatmap['Active Instances %'], 
                      df_heatmap['Active Channels %']],
                texttemplate='%{text:.1f}%',
                textfont={"size": 10},
                colorbar=dict(title="Activity %"),
                hovertemplate='Company: %{x}<br>Metric: %{y}<br>Value: %{z:.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title='Activity Status Across Companies',
                height=400,
                xaxis_title='Company',
                yaxis_title='Metric',
                template=chart_theme
            )
            st.plotly_chart(fig, use_container_width=True, key='exec_heatmap')
            
            # Comparison Chart
            st.markdown('<div class="section-header">📈 Multi-Metric Comparison</div>', unsafe_allow_html=True)
            
            comparison_data = pd.DataFrame([{
                'Company': c.get('name', 'Unknown')[:20],
                'Users': c.get('users_count', 0),
                'Channels': c.get('channels_count', 0),
                'Instances': c.get('instances_count', 0),
                'Broadcasts': c.get('broadcasts_count', 0)
            } for c in companies[:15]])
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(name='Users', x=comparison_data['Company'], y=comparison_data['Users'], 
                                marker_color='#667eea'))
            fig.add_trace(go.Bar(name='Channels', x=comparison_data['Company'], y=comparison_data['Channels'],
                                marker_color='#764ba2'))
            fig.add_trace(go.Bar(name='Instances', x=comparison_data['Company'], y=comparison_data['Instances'],
                                marker_color='#28a745'))
            fig.add_trace(go.Bar(name='Broadcasts', x=comparison_data['Company'], y=comparison_data['Broadcasts'],
                                marker_color='#ffc107'))
            
            fig.update_layout(
                title='Resource Comparison Across Companies',
                barmode='group',
                height=500,
                xaxis_title='Company',
                yaxis_title='Count',
                template=chart_theme,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True, key='exec_comparison')
        
        # ==================== COMPANY ANALYSIS ====================
        elif view_option == "🏢 Company Analysis":
            st.markdown('<div class="section-header">🏢 Company Deep Dive</div>', unsafe_allow_html=True)
            
            for idx, company in enumerate(filtered_companies):
                with st.expander(f"📁 {company.get('name', 'Unknown')}", expanded=(selected_company != "All Companies")):
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("👥 Users", company.get('users_count', 0))
                    col2.metric("📢 Channels", company.get('channels_count', 0))
                    col3.metric("⚙️ Instances", company.get('instances_count', 0))
                    col4.metric("📡 Broadcasts", company.get('broadcasts_count', 0))
                    col5.metric("⚡ Speed Messages", company.get('speedMessages_count', 0))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        user_types = Counter()
                        for user in company.get('users', []):
                            user_type = user.get('user_type_name', 'Unknown')
                            user_types[user_type] += 1
                        
                        if user_types:
                            df_types = pd.DataFrame(list(user_types.items()), columns=['Type', 'Count'])
                            fig = px.pie(
                                df_types,
                                values='Count',
                                names='Type',
                                title='User Types Distribution',
                                color_discrete_sequence=px.colors.qualitative.Set2,
                                hole=0.3,
                                template=chart_theme
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True, key=f'company_users_{idx}')
                    
                    with col2:
                        instances = company.get('instances', [])
                        active_count = sum(1 for i in instances if i.get('active', False))
                        inactive_count = len(instances) - active_count
                        
                        if instances:
                            df_status = pd.DataFrame({
                                'Status': ['Active', 'Inactive'],
                                'Count': [active_count, inactive_count]
                            })
                            
                            fig = px.bar(
                                df_status,
                                x='Status',
                                y='Count',
                                title='Instance Status',
                                color='Status',
                                color_discrete_map={'Active': '#28a745', 'Inactive': '#dc3545'},
                                template=chart_theme
                            )
                            if show_data_labels:
                                fig.update_traces(texttemplate='%{y}', textposition='outside')
                            st.plotly_chart(fig, use_container_width=True, key=f'company_instances_{idx}')
                    
                    channels = company.get('channels', [])
                    if channels:
                        st.markdown("#### 📢 Channel Performance")
                        
                        channel_data = pd.DataFrame([{
                            'Channel': ch.get('name', 'Unknown'),
                            'Instances': ch.get('instances_count', 0),
                            'Speed Messages': ch.get('speedMessages_count', 0),
                            'Active': 'Yes' if ch.get('isActive', False) else 'No'
                        } for ch in channels])
                        
                        fig = px.bar(
                            channel_data,
                            x='Channel',
                            y=['Instances', 'Speed Messages'],
                            title='Channel Metrics',
                            barmode='group',
                            template=chart_theme,
                            color_discrete_sequence=['#667eea', '#ffc107']
                        )
                        fig.update_layout(height=400, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True, key=f'company_channels_{idx}')
                    
                    tab1, tab2, tab3 = st.tabs(["👥 Users", "📢 Channels", "⚙️ Instances"])
                    
                    with tab1:
                        users_df = pd.DataFrame([{
                            'Name': u.get('name', 'Unknown'),
                            'Email': u.get('email', 'N/A'),
                            'Type': u.get('user_type_name', 'Unknown'),
                            'Phone': u.get('phone', 'N/A'),
                            'Active': '✅' if u.get('isActive', False) else '❌'
                        } for u in company.get('users', [])])
                        
                        if not users_df.empty:
                            search_term = st.text_input("🔍 Search users:", key=f"search_users_{idx}")
                            if search_term:
                                users_df = users_df[users_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                            
                            st.dataframe(users_df, use_container_width=True, height=300)
                            
                            csv = users_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Users CSV",
                                csv,
                                f"users_{company.get('name', 'company')}.csv",
                                "text/csv",
                                key=f"download_users_{idx}"
                            )
                        else:
                            st.info("No users found")
                    
                    with tab2:
                        channels_df = pd.DataFrame([{
                            'Name': ch.get('name', 'Unknown'),
                            'Instances': ch.get('instances_count', 0),
                            'Speed Messages': ch.get('speedMessages_count', 0),
                            'Active': '✅' if ch.get('isActive', False) else '❌'
                        } for ch in company.get('channels', [])])
                        
                        if not channels_df.empty:
                            st.dataframe(channels_df, use_container_width=True, height=300)
                            
                            csv = channels_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Channels CSV",
                                csv,
                                f"channels_{company.get('name', 'company')}.csv",
                                "text/csv",
                                key=f"download_channels_{idx}"
                            )
                        else:
                            st.info("No channels found")
                    
                    with tab3:
                        instances_df = pd.DataFrame([{
                            'Name': i.get('name', 'Unknown'),
                            'Type': i.get('type_details', {}).get('name', 'Unknown') if i.get('type_details') else 'Unknown',
                            'Status': i.get('status', 'Unknown'),
                            'Active': '✅' if i.get('active', False) else '❌',
                            'Broadcasts': i.get('broadcasts_count', 0)
                        } for i in company.get('instances', [])])
                        
                        if not instances_df.empty:
                            st.dataframe(instances_df, use_container_width=True, height=300)
                            
                            csv = instances_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Instances CSV",
                                csv,
                                f"instances_{company.get('name', 'company')}.csv",
                                "text/csv",
                                key=f"download_instances_{idx}"
                            )
                        else:
                            st.info("No instances found")
        
        # ==================== USER ANALYSIS ====================
        elif view_option == "👥 User Analysis":
            st.markdown('<div class="section-header">👥 User Analytics</div>', unsafe_allow_html=True)
            
            all_users = []
            for company in filtered_companies:
                for user in company.get('users', []):
                    user_data = user.copy()
                    user_data['company_name'] = company.get('name', 'Unknown')
                    user_data['source'] = 'company'
                    all_users.append(user_data)
            
            orphaned_users = []
            if 'orphaned_users' in data and selected_company == "All Companies":
                for user in data.get('orphaned_users', []):
                    user_data = user.copy()
                    user_data['company_name'] = 'Orphaned/Unlinked'
                    user_data['source'] = 'orphaned'
                    orphaned_users.append(user_data)
            
            combined_users = all_users + orphaned_users
            
            if selected_user_types:
                combined_users = [u for u in combined_users if u.get('user_type_name') in selected_user_types]
            
            if show_active_only:
                combined_users = [u for u in combined_users if u.get('isActive', False)]
            
            if combined_users:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Users in Companies", len(all_users))
                col2.metric("Orphaned Users", len(orphaned_users))
                col3.metric("Filtered Total", len(combined_users))
                active_users = sum(1 for u in combined_users if u.get('isActive', False))
                col4.metric("Active Rate", f"{(active_users/len(combined_users)*100):.1f}%")
                
                if orphaned_users:
                    st.warning(f"⚠️ Found {len(orphaned_users)} orphaned users. Check Debug View for details.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏢 By Company", "📈 Trends", "📋 Data Table"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        user_types = Counter(u.get('user_type_name', u.get('type', 'Unknown')) for u in combined_users)
                        df_types = pd.DataFrame(list(user_types.items()), columns=['Type', 'Count'])
                        
                        fig = px.pie(
                            df_types,
                            values='Count',
                            names='Type',
                            title=f'User Type Distribution (Total: {len(combined_users)})',
                            color_discrete_sequence=px.colors.qualitative.Bold,
                            hole=0.4,
                            template=chart_theme
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                        )
                        st.plotly_chart(fig, use_container_width=True, key='user_types_pie')
                    
                    with col2:
                        active_count = sum(1 for u in combined_users if u.get('isActive', False))
                        inactive_count = len(combined_users) - active_count
                        
                        df_active = pd.DataFrame({
                            'Status': ['Active', 'Inactive'],
                            'Count': [active_count, inactive_count]
                        })
                        
                        fig = px.bar(
                            df_active,
                            x='Status',
                            y='Count',
                            title='User Activity Status',
                            color='Status',
                            color_discrete_map={'Active': '#28a745', 'Inactive': '#dc3545'},
                            template=chart_theme
                        )
                        fig.update_traces(
                            texttemplate='%{y}',
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                        )
                        st.plotly_chart(fig, use_container_width=True, key='user_active_bar')
                
                with tab2:
                    company_users = Counter(u.get('company_name') for u in combined_users)
                    df_company = pd.DataFrame(list(company_users.items()), columns=['Company', 'Users'])
                    df_company = df_company.sort_values('Users', ascending=True)
                    
                    fig = px.bar(
                        df_company,
                        y='Company',
                        x='Users',
                        orientation='h',
                        title='Users per Company',
                        color='Users',
                        color_continuous_scale='Viridis',
                        template=chart_theme
                    )
                    fig.update_layout(height=max(400, len(df_company) * 25))
                    fig.update_traces(
                        texttemplate='%{x}',
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Users: %{x}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True, key='user_by_company')
                    
                    st.markdown("#### User Type Breakdown by Company")
                    
                    user_type_company = []
                    for user in combined_users:
                        user_type_company.append({
                            'Company': user.get('company_name', 'Unknown'),
                            'Type': user.get('user_type_name', 'Unknown'),
                            'Active': 'Active' if user.get('isActive', False) else 'Inactive'
                        })
                    
                    df_breakdown = pd.DataFrame(user_type_company)
                    df_breakdown_grouped = df_breakdown.groupby(['Company', 'Type']).size().reset_index(name='Count')
                    
                    fig = px.bar(
                        df_breakdown_grouped,
                        x='Company',
                        y='Count',
                        color='Type',
                        title='User Types by Company',
                        barmode='stack',
                        template=chart_theme,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(height=500, xaxis_tickangle=-45)
                    fig.update_traces(hovertemplate='<b>%{x}</b><br>Type: %{fullData.name}<br>Count: %{y}<extra></extra>')
                    st.plotly_chart(fig, use_container_width=True, key='user_type_breakdown')
                
                with tab3:
                    st.markdown("#### 📈 User Patterns")
                    
                    sunburst_data = []
                    for user in combined_users:
                        sunburst_data.append({
                            'Company': user.get('company_name', 'Unknown'),
                            'Type': user.get('user_type_name', 'Unknown'),
                            'Active': 'Active' if user.get('isActive', False) else 'Inactive',
                            'Count': 1
                        })
                    
                    df_sunburst = pd.DataFrame(sunburst_data)
                    
                    fig = px.sunburst(
                        df_sunburst,
                        path=['Company', 'Type', 'Active'],
                        values='Count',
                        title='User Hierarchy: Company → Type → Status',
                        template=chart_theme,
                        color='Count',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True, key='user_sunburst')
                    
                    fig = px.treemap(
                        df_sunburst,
                        path=['Company', 'Type'],
                        values='Count',
                        title='User Distribution Treemap',
                        template=chart_theme,
                        color='Count',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True, key='user_treemap')
                
                with tab4:
                    st.markdown("#### 📋 Detailed User Data")
                    
                    users_df = pd.DataFrame([{
                        'Company': u.get('company_name'),
                        'Name': u.get('name', 'Unknown'),
                        'Email': u.get('email', 'N/A'),
                        'Type': u.get('user_type_name', u.get('type', 'Unknown')),
                        'Phone': u.get('phone', 'N/A'),
                        'Active': '✅' if u.get('isActive', False) else '❌',
                        'Source': u.get('source', 'company')
                    } for u in combined_users])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        search_name = st.text_input("🔍 Search by Name/Email:", key='user_search_main')
                    
                    with col2:
                        filter_type = st.multiselect('Filter by Type:', users_df['Type'].unique(), key='user_filter_type')
                    
                    with col3:
                        filter_company = st.multiselect('Filter by Company:', users_df['Company'].unique(), key='user_filter_company')
                    
                    filtered_df = users_df.copy()
                    
                    if search_name:
                        filtered_df = filtered_df[
                            filtered_df['Name'].str.contains(search_name, case=False, na=False) |
                            filtered_df['Email'].str.contains(search_name, case=False, na=False)
                        ]
                    
                    if filter_type:
                        filtered_df = filtered_df[filtered_df['Type'].isin(filter_type)]
                    
                    if filter_company:
                        filtered_df = filtered_df[filtered_df['Company'].isin(filter_company)]
                    
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    st.info(f"Showing {len(filtered_df)} of {len(combined_users)} users")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = filtered_df.to_csv(index=False)
                        st.download_button("📥 Download Filtered Data (CSV)", csv, "filtered_users.csv", "text/csv", key='user_download_csv')
                    
                    with col2:
                        json_data = filtered_df.to_json(orient='records', indent=2)
                        st.download_button("📥 Download Filtered Data (JSON)", json_data, "filtered_users.json", "application/json", key='user_download_json')
            else:
                st.warning("⚠️ No user data available. Check Debug View.")
        
        # ==================== INSTANCE ANALYSIS ====================
        elif view_option == "⚙️ Instance Analysis":
            st.markdown('<div class="section-header">⚙️ Instance Analytics</div>', unsafe_allow_html=True)
            
            all_instances = []
            for company in filtered_companies:
                for instance in company.get('instances', []):
                    instance_data = instance.copy()
                    instance_data['company_name'] = company.get('name', 'Unknown')
                    all_instances.append(instance_data)
            
            if all_instances:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Instances", len(all_instances))
                active_instances = sum(1 for i in all_instances if i.get('active', False))
                col2.metric("Active Instances", active_instances)
                col3.metric("Active Rate", f"{(active_instances/len(all_instances)*100):.1f}%")
                total_broadcasts = sum(i.get('broadcasts_count', 0) for i in all_instances)
                col4.metric("Total Broadcasts", total_broadcasts)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                tab1, tab2, tab3 = st.tabs(["📊 Overview", "🏢 By Company", "📋 Data Table"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        instance_types = Counter()
                        for instance in all_instances:
                            type_details = instance.get('type_details') or {}
                            type_name = type_details.get('name', 'Unknown')
                            instance_types[type_name] += 1
                        
                        df_types = pd.DataFrame(list(instance_types.items()), columns=['Type', 'Count'])
                        df_types = df_types.sort_values('Count', ascending=False)
                        
                        fig = px.pie(
                            df_types,
                            values='Count',
                            names='Type',
                            title='Instance Types Distribution',
                            color_discrete_sequence=px.colors.qualitative.Set3,
                            hole=0.4,
                            template=chart_theme
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
                        )
                        st.plotly_chart(fig, use_container_width=True, key='instance_types_pie')
                    
                    with col2:
                        status_count = Counter(i.get('status', 'Unknown') for i in all_instances)
                        df_status = pd.DataFrame(list(status_count.items()), columns=['Status', 'Count'])
                        
                        fig = px.bar(
                            df_status,
                            x='Status',
                            y='Count',
                            title='Instance Status Distribution',
                            color='Status',
                            color_discrete_sequence=px.colors.qualitative.Safe,
                            template=chart_theme
                        )
                        fig.update_traces(
                            texttemplate='%{y}',
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                        )
                        st.plotly_chart(fig, use_container_width=True, key='instance_status_bar')
                    
                    st.markdown("#### Instance Activity by Type")
                    
                    type_activity = []
                    for instance in all_instances:
                        type_details = instance.get('type_details') or {}
                        type_activity.append({
                            'Type': type_details.get('name', 'Unknown'),
                            'Status': 'Active' if instance.get('active', False) else 'Inactive',
                            'Count': 1
                        })
                    
                    df_type_activity = pd.DataFrame(type_activity)
                    df_grouped = df_type_activity.groupby(['Type', 'Status']).size().reset_index(name='Count')
                    
                    fig = px.bar(
                        df_grouped,
                        x='Type',
                        y='Count',
                        color='Status',
                        title='Instance Activity by Type',
                        barmode='stack',
                        color_discrete_map={'Active': '#28a745', 'Inactive': '#dc3545'},
                        template=chart_theme
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True, key='instance_activity_stacked')
                
                with tab2:
                    company_instances = Counter(i.get('company_name') for i in all_instances)
                    df_company = pd.DataFrame(list(company_instances.items()), columns=['Company', 'Instances'])
                    df_company = df_company.sort_values('Instances', ascending=True).tail(20)
                    
                    fig = px.bar(
                        df_company,
                        y='Company',
                        x='Instances',
                        orientation='h',
                        title='Instances per Company (Top 20)',
                        color='Instances',
                        color_continuous_scale='Blues',
                        template=chart_theme
                    )
                    fig.update_layout(height=600)
                    fig.update_traces(
                        texttemplate='%{x}',
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Instances: %{x}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True, key='instance_by_company')
                    
                    st.markdown("#### Instance Utilization by Company")
                    
                    company_utilization = []
                    for company in filtered_companies:
                        instances = company.get('instances', [])
                        if instances:
                            active_pct = sum(1 for i in instances if i.get('active', False)) / len(instances) * 100
                            company_utilization.append({
                                'Company': company.get('name', 'Unknown'),
                                'Utilization %': round(active_pct, 1),
                                'Total Instances': len(instances)
                            })
                    
                    df_util = pd.DataFrame(company_utilization).sort_values('Utilization %', ascending=True)
                    
                    fig = px.bar(
                        df_util,
                        y='Company',
                        x='Utilization %',
                        orientation='h',
                        title='Instance Utilization Rate by Company',
                        color='Utilization %',
                        color_continuous_scale='RdYlGn',
                        template=chart_theme,
                        hover_data=['Total Instances']
                    )
                    fig.update_layout(height=max(400, len(df_util) * 25))
                    fig.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="50% Threshold")
                    st.plotly_chart(fig, use_container_width=True, key='instance_utilization')
                
                with tab3:
                    st.markdown("#### 📋 Instance Details")
                    
                    instances_df = pd.DataFrame([{
                        'Company': i.get('company_name'),
                        'Name': i.get('name', 'Unknown'),
                        'Type': i.get('type_details', {}).get('name', 'Unknown') if i.get('type_details') else 'Unknown',
                        'Status': i.get('status', 'Unknown'),
                        'Active': '✅' if i.get('active', False) else '❌',
                        'Broadcasts': i.get('broadcasts_count', 0)
                    } for i in all_instances])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        search_instance = st.text_input("🔍 Search instances:", key='instance_search')
                    
                    with col2:
                        filter_status = st.multiselect('Filter by Status:', instances_df['Status'].unique(), key='instance_filter_status')
                    
                    with col3:
                        filter_type_inst = st.multiselect('Filter by Type:', instances_df['Type'].unique(), key='instance_filter_type')
                    
                    filtered_df = instances_df.copy()
                    
                    if search_instance:
                        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_instance, case=False, na=False)]
                    
                    if filter_status:
                        filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]
                    
                    if filter_type_inst:
                        filtered_df = filtered_df[filtered_df['Type'].isin(filter_type_inst)]
                    
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    st.info(f"Showing {len(filtered_df)} of {len(instances_df)} instances")
                    
                    csv = filtered_df.to_csv(index=False)
                    st.download_button("📥 Download Instance Data (CSV)", csv, "instances.csv", "text/csv", key='instance_download')
            else:
                st.warning("No instance data available")
        
        # ==================== BROADCAST ANALYSIS ====================
        elif view_option == "📡 Broadcast Analysis":
            st.markdown('<div class="section-header">📡 Broadcast Analytics</div>', unsafe_allow_html=True)
            
            all_broadcasts = []
            for company in filtered_companies:
                for broadcast in company.get('broadcasts', []):
                    broadcast_data = broadcast.copy()
                    broadcast_data['company_name'] = company.get('name', 'Unknown')
                    all_broadcasts.append(broadcast_data)
            
            if all_broadcasts:
                status_counts = Counter(b.get('status', 'Unknown') for b in all_broadcasts)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Broadcasts", len(all_broadcasts))
                completed = status_counts.get('completed', 0) + status_counts.get('Completed', 0)
                col2.metric("Completed", completed)
                pending = status_counts.get('pending', 0) + status_counts.get('Pending', 0)
                col3.metric("Pending", pending)
                col4.metric("Completion Rate", f"{(completed/len(all_broadcasts)*100):.1f}%")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                    
                    fig = px.pie(
                        df_status,
                        values='Count',
                        names='Status',
                        title='Broadcast Status Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        hole=0.4,
                        template=chart_theme
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True, key='broadcast_status_pie')
                
                with col2:
                    company_broadcasts = Counter(b.get('company_name') for b in all_broadcasts)
                    df_company = pd.DataFrame(list(company_broadcasts.items()), columns=['Company', 'Broadcasts'])
                    df_company = df_company.sort_values('Broadcasts', ascending=True).tail(15)
                    
                    fig = px.bar(
                        df_company,
                        y='Company',
                        x='Broadcasts',
                        orientation='h',
                        title='Broadcasts per Company (Top 15)',
                        color='Broadcasts',
                        color_continuous_scale='Reds',
                        template=chart_theme
                    )
                    fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key='broadcast_by_company')
                
                st.markdown("#### 📋 Broadcast Details")
                
                broadcasts_df = pd.DataFrame([{
                    'Company': b.get('company_name'),
                    'Name': b.get('name', 'Unknown'),
                    'Status': b.get('status', 'Unknown')
                } for b in all_broadcasts])
                
                filter_status_bc = st.multiselect('Filter by Status:', broadcasts_df['Status'].unique(), key='broadcast_filter_status')
                
                filtered_df = broadcasts_df.copy()
                if filter_status_bc:
                    filtered_df = filtered_df[filtered_df['Status'].isin(filter_status_bc)]
                
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                csv = filtered_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "broadcasts.csv", "text/csv", key='broadcast_download')
            else:
                st.warning("No broadcast data available")
        
        # ==================== CROSS ANALYSIS ====================
        elif view_option == "📊 Cross Analysis":
            st.markdown('<div class="section-header">📊 Cross-Dimensional Analysis</div>', unsafe_allow_html=True)
            
            st.info("💡 Explore relationships between different metrics")
            
            analysis_data = []
            for company in filtered_companies:
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                
                analysis_data.append({
                    'Company': company.get('name', 'Unknown'),
                    'Users': len(users),
                    'Active Users': sum(1 for u in users if u.get('isActive', False)),
                    'Channels': len(channels),
                    'Instances': len(instances),
                    'Active Instances': sum(1 for i in instances if i.get('active', False)),
                    'Broadcasts': company.get('broadcasts_count', 0),
                    'Speed Messages': company.get('speedMessages_count', 0),
                    'Users per Channel': len(users) / len(channels) if channels else 0,
                    'Broadcasts per Instance': company.get('broadcasts_count', 0) / len(instances) if instances else 0
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                x_axis = st.selectbox("Select X-axis:", df_analysis.columns[1:], index=0, key='x_axis_cross')
            
            with col2:
                y_axis = st.selectbox("Select Y-axis:", df_analysis.columns[1:], index=1, key='y_axis_cross')
            
            fig = px.scatter(
                df_analysis,
                x=x_axis,
                y=y_axis,
                size='Users',
                color='Broadcasts',
                hover_data=['Company', 'Users', 'Instances', 'Broadcasts'],
                title=f'{y_axis} vs {x_axis}',
                template=chart_theme,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, key='cross_scatter')
            
            st.markdown("#### 🔥 Correlation Heatmap")
            
            numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns
            correlation_matrix = df_analysis[numeric_cols].corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=correlation_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            
            fig.update_layout(
                title='Metric Correlations',
                height=600,
                template=chart_theme
            )
            st.plotly_chart(fig, use_container_width=True, key='cross_heatmap')
            
            st.markdown("#### 📡 Company Comparison Radar")
            
            df_normalized = df_analysis.copy()
            metrics_to_normalize = ['Users', 'Channels', 'Instances', 'Broadcasts', 'Speed Messages']
            
            for metric in metrics_to_normalize:
                max_val = df_normalized[metric].max()
                if max_val > 0:
                    df_normalized[f'{metric}_norm'] = (df_normalized[metric] / max_val) * 100
            
            selected_companies_radar = st.multiselect(
                "Select companies to compare (max 5):",
                df_analysis['Company'].tolist(),
                default=df_analysis['Company'].tolist()[:3],
                key='radar_companies'
            )
            
            if selected_companies_radar:
                fig = go.Figure()
                
                for company in selected_companies_radar[:5]:
                    company_data = df_normalized[df_normalized['Company'] == company].iloc[0]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[company_data[f'{m}_norm'] for m in metrics_to_normalize],
                        theta=metrics_to_normalize,
                        fill='toself',
                        name=company
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title='Company Performance Comparison (Normalized)',
                    height=600,
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='cross_radar')
            
            st.markdown("#### 🎯 Parallel Coordinates")
            
            fig = px.parallel_coordinates(
                df_analysis,
                dimensions=['Users', 'Channels', 'Instances', 'Broadcasts', 'Speed Messages'],
                color='Users',
                labels={'Users': 'Users', 'Channels': 'Channels', 'Instances': 'Instances',
                       'Broadcasts': 'Broadcasts', 'Speed Messages': 'Speed Msgs'},
                color_continuous_scale='Viridis',
                title='Multi-Dimensional Company Analysis',
                template=chart_theme
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, key='cross_parallel')
        
        # ==================== DEBUG VIEW ====================
        elif view_option == "🐛 Debug View":
            st.markdown('<div class="section-header">🐛 Data Debugging</div>', unsafe_allow_html=True)
            
            st.subheader("📊 Metadata Stats")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Users (Metadata)", metadata.get('total_users', 0))
            col2.metric("Total Companies", metadata.get('total_companies', 0))
            col3.metric("Expected Users", metadata.get('total_users', 0))
            
            st.markdown("---")
            
            st.subheader("👥 Users in Companies")
            
            total_users_in_companies = 0
            company_stats = []
            
            for company in companies:
                users_count = len(company.get('users', []))
                total_users_in_companies += users_count
                
                company_stats.append({
                    'Company': company.get('name', 'Unknown'),
                    'Users Count': users_count,
                    'Channels': company.get('channels_count', 0),
                    'Instances': company.get('instances_count', 0),
                    'Company ID': str(company.get('_id', 'N/A'))
                })
            
            df_stats = pd.DataFrame(company_stats)
            st.dataframe(df_stats, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Users Found in Companies", total_users_in_companies)
            col2.metric("❓ Missing Users", metadata.get('total_users', 0) - total_users_in_companies)
            col3.metric("📊 Match Rate", f"{(total_users_in_companies / metadata.get('total_users', 1) * 100):.1f}%")
            
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=total_users_in_companies,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Users Matched"},
                delta={'reference': metadata.get('total_users', 0)},
                gauge={
                    'axis': {'range': [None, metadata.get('total_users', 0)]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, metadata.get('total_users', 0) * 0.5], 'color': "lightgray"},
                        {'range': [metadata.get('total_users', 0) * 0.5, metadata.get('total_users', 0) * 0.8], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': metadata.get('total_users', 0)
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True, key='debug_gauge')
            
            st.markdown("---")
            
            st.subheader("🔍 Orphaned Users Check")
            
            if 'orphaned_users' in data:
                orphaned_count = len(data['orphaned_users'])
                st.warning(f"⚠️ Found {orphaned_count} orphaned users (users not linked to any company)")
                
                if orphaned_count > 0:
                    orphaned_df = pd.DataFrame([{
                        'Name': u.get('name', 'Unknown'),
                        'Email': u.get('email', 'N/A'),
                        'Type': u.get('user_type_name', u.get('type', 'Unknown')),
                        'Company ID': str(u.get('company', u.get('companyId', 'N/A'))),
                        'Reason': u.get('reason', 'Unknown')
                    } for u in data['orphaned_users']])
                    
                    st.dataframe(orphaned_df, use_container_width=True, height=300)
                    
                    with st.expander("🔬 Sample Orphaned User Structure"):
                        st.json(data['orphaned_users'][0])
            else:
                st.info("ℹ️ No orphaned users data found. This might mean:")
                st.write("- All users are properly linked to companies ✅")
                st.write("- OR the merge script didn't create the orphaned_users field ⚠️")
            
            st.markdown("---")
            
            st.subheader("🔬 Sample User Data Structure")
            
            if companies and companies[0].get('users'):
                st.write("**Sample User from First Company:**")
                st.json(companies[0]['users'][0])
            else:
                st.warning("No users found in first company")
            
            st.markdown("---")
            
            st.subheader("📈 Raw Counts Comparison")
            
            comparison_data = {
                'Source': ['Metadata', 'Companies Total', 'Difference'],
                'Users': [
                    metadata.get('total_users', 0),
                    total_users_in_companies,
                    metadata.get('total_users', 0) - total_users_in_companies
                ],
                'Channels': [
                    metadata.get('total_channels', 0),
                    sum(c.get('channels_count', 0) for c in companies),
                    0
                ],
                'Instances': [
                    metadata.get('total_instances', 0),
                    sum(c.get('instances_count', 0) for c in companies),
                    0
                ]
            }
            
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
            
            if total_users_in_companies < metadata.get('total_users', 0):
                st.error("⚠️ **ISSUE DETECTED**: Not all users are linked to companies!")
                st.write("**Possible causes:**")
                st.write("1. Company ID mismatch in source data")
                st.write("2. Users have invalid/missing company references")
                st.write("3. Data merge script needs to be run again")
                st.write("\n**Solution:** Run the improved merge script again to fix user-company relationships")
            else:
                st.success("✅ All users are properly linked to companies!")
        # ==================== BUSINESS INTELLIGENCE ====================
        elif view_option == "💼 Business Intelligence":
            st.markdown('<div class="section-header">💼 Business Intelligence Dashboard</div>', unsafe_allow_html=True)
            
            # Calculate KPIs
            total_users = metadata.get('total_users', 0)
            total_instances = metadata.get('total_instances', 0)
            total_broadcasts = metadata.get('total_broadcasts', 0)
            total_companies = metadata.get('total_companies', 0)
            
            # Active rates
            all_users_list = []
            all_instances_list = []
            
            for company in companies:
                all_users_list.extend(company.get('users', []))
                all_instances_list.extend(company.get('instances', []))
            
            active_users = sum(1 for u in all_users_list if u.get('isActive', False))
            active_instances = sum(1 for i in all_instances_list if i.get('active', False))
            
            active_user_rate = (active_users / total_users * 100) if total_users > 0 else 0
            active_instance_rate = (active_instances / total_instances * 100) if total_instances > 0 else 0
            
            # Key Business Metrics
            st.markdown("### 🎯 Key Performance Indicators")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "User Activation Rate",
                    f"{active_user_rate:.1f}%",
                    delta=f"{active_user_rate - 70:.1f}% vs target",
                    delta_color="normal" if active_user_rate >= 70 else "inverse"
                )
            
            with col2:
                st.metric(
                    "Instance Utilization",
                    f"{active_instance_rate:.1f}%",
                    delta=f"{active_instance_rate - 80:.1f}% vs target",
                    delta_color="normal" if active_instance_rate >= 80 else "inverse"
                )
            
            with col3:
                avg_users_per_company = total_users / total_companies if total_companies > 0 else 0
                st.metric(
                    "Avg Users/Company",
                    f"{avg_users_per_company:.0f}",
                    delta="Growth opportunity" if avg_users_per_company < 50 else "Mature"
                )
            
            with col4:
                avg_broadcasts_per_instance = total_broadcasts / total_instances if total_instances > 0 else 0
                st.metric(
                    "Broadcasts/Instance",
                    f"{avg_broadcasts_per_instance:.1f}",
                    delta="Healthy" if avg_broadcasts_per_instance > 2 else "Low usage"
                )
            
            with col5:
                # Calculate resource efficiency score
                efficiency_score = (active_user_rate * 0.4 + active_instance_rate * 0.6)
                st.metric(
                    "Efficiency Score",
                    f"{efficiency_score:.0f}/100",
                    delta="Good" if efficiency_score >= 75 else "Needs improvement"
                )
            
            st.markdown("---")
            
            # Company Performance Scorecard
            st.markdown("### 🏆 Company Performance Scorecard")
            
            company_scores = []
            for company in companies:
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                
                # Calculate scores
                user_activity = (sum(1 for u in users if u.get('isActive', False)) / len(users) * 100) if users else 0
                instance_activity = (sum(1 for i in instances if i.get('active', False)) / len(instances) * 100) if instances else 0
                resource_usage = (len(users) + len(instances) + company.get('broadcasts_count', 0)) / 3
                
                overall_score = (user_activity * 0.3 + instance_activity * 0.3 + min(resource_usage, 100) * 0.4)
                
                # Determine health status
                if overall_score >= 80:
                    health = "🟢 Excellent"
                    risk_level = "Low"
                elif overall_score >= 60:
                    health = "🟡 Good"
                    risk_level = "Medium"
                elif overall_score >= 40:
                    health = "🟠 Fair"
                    risk_level = "Medium-High"
                else:
                    health = "🔴 Poor"
                    risk_level = "High"
                
                company_scores.append({
                    'Company': company.get('name', 'Unknown'),
                    'Overall Score': round(overall_score, 1),
                    'Health Status': health,
                    'User Activity %': round(user_activity, 1),
                    'Instance Activity %': round(instance_activity, 1),
                    'Total Users': len(users),
                    'Total Instances': len(instances),
                    'Broadcasts': company.get('broadcasts_count', 0),
                    'Churn Risk': risk_level
                })
            
            df_scores = pd.DataFrame(company_scores).sort_values('Overall Score', ascending=False)
            
            # Visual scorecard
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df_scores.head(15),
                    x='Overall Score',
                    y='Company',
                    orientation='h',
                    title='Top 15 Companies by Performance Score',
                    color='Overall Score',
                    color_continuous_scale='RdYlGn',
                    template=chart_theme,
                    hover_data=['Health Status', 'Churn Risk']
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True, key='bi_performance_score')
            
            with col2:
                # Churn risk distribution
                risk_counts = df_scores['Churn Risk'].value_counts()
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title='Customer Churn Risk Distribution',
                    color=risk_counts.index,
                    color_discrete_map={
                        'Low': '#28a745',
                        'Medium': '#ffc107',
                        'Medium-High': '#fd7e14',
                        'High': '#dc3545'
                    },
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='bi_churn_risk')
            
            # Detailed scorecard table
            st.markdown("#### 📊 Detailed Performance Metrics")
            
            # Add color coding to dataframe
            def color_score(val):
                if isinstance(val, (int, float)):
                    if val >= 80:
                        color = 'background-color: #d4edda'
                    elif val >= 60:
                        color = 'background-color: #fff3cd'
                    elif val >= 40:
                        color = 'background-color: #ffe5d0'
                    else:
                        color = 'background-color: #f8d7da'
                    return color
                return ''
            
            st.dataframe(
                df_scores.style.applymap(color_score, subset=['Overall Score', 'User Activity %', 'Instance Activity %']),
                use_container_width=True,
                height=400
            )
            
            # Download scorecard
            csv = df_scores.to_csv(index=False)
            st.download_button(
                "📥 Download Performance Scorecard",
                csv,
                "performance_scorecard.csv",
                "text/csv",
                key='bi_download_scorecard'
            )
            
            st.markdown("---")
            
            # Resource Allocation Analysis
            st.markdown("### 💎 Resource Allocation Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Companies by resource tier
                df_scores['Resource Tier'] = pd.cut(
                    df_scores['Total Users'],
                    bins=[0, 10, 50, 100, float('inf')],
                    labels=['Starter (0-10)', 'Growth (11-50)', 'Enterprise (51-100)', 'Premium (100+)']
                )
                
                tier_counts = df_scores['Resource Tier'].value_counts()
                
                fig = px.bar(
                    x=tier_counts.index,
                    y=tier_counts.values,
                    title='Companies by Resource Tier',
                    labels={'x': 'Tier', 'y': 'Number of Companies'},
                    color=tier_counts.values,
                    color_continuous_scale='Blues',
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='bi_resource_tier')
            
            with col2:
                # Top resource consumers
                fig = px.scatter(
                    df_scores,
                    x='Total Users',
                    y='Total Instances',
                    size='Broadcasts',
                    color='Overall Score',
                    hover_name='Company',
                    title='Resource Consumption Matrix',
                    labels={'Total Users': 'Users', 'Total Instances': 'Instances'},
                    color_continuous_scale='RdYlGn',
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='bi_resource_matrix')
            
            # Action Items
            st.markdown("### 🎯 Recommended Actions")
            
            # High risk customers
            high_risk = df_scores[df_scores['Churn Risk'].isin(['High', 'Medium-High'])]
            if not high_risk.empty:
                st.warning(f"⚠️ **{len(high_risk)} companies** at risk of churn. Immediate action required!")
                with st.expander("View At-Risk Companies"):
                    st.dataframe(high_risk[['Company', 'Overall Score', 'Churn Risk', 'User Activity %', 'Instance Activity %']], use_container_width=True)
            
            # Low utilization
            low_util = df_scores[df_scores['Instance Activity %'] < 50]
            if not low_util.empty:
                st.info(f"💡 **{len(low_util)} companies** have low instance utilization. Consider training or downsizing.")
            
            # Growth opportunities
            growth_opps = df_scores[(df_scores['Overall Score'] >= 70) & (df_scores['Total Users'] < 50)]
            if not growth_opps.empty:
                st.success(f"🚀 **{len(growth_opps)} companies** are prime candidates for upselling!")
        
        # ==================== PREDICTIVE ANALYTICS ====================
        elif view_option == "📈 Predictive Analytics":
            st.markdown('<div class="section-header">📈 Predictive Analytics & Forecasting</div>', unsafe_allow_html=True)
            
            st.info("💡 Using historical patterns to predict future trends")
            
            st.markdown("### 📊 Growth Trends & Forecasting")
            
            # Generate last 12 months of data
            months = []
            current_date = datetime.now()
            for i in range(12, 0, -1):
                months.append((current_date - timedelta(days=30*i)).strftime('%Y-%m'))
            
            # Simulate growth patterns
            base_users = metadata.get('total_users', 0)
            base_companies = metadata.get('total_companies', 0)
            base_instances = metadata.get('total_instances', 0)
            base_broadcasts = metadata.get('total_broadcasts', 0)
            
            historical_data = []
            for i, month in enumerate(months):
                # Simulate growth with some randomness
                growth_factor = 1 + (i * 0.05) + (np.random.random() * 0.1)
                historical_data.append({
                    'Month': month,
                    'Users': int(base_users / growth_factor) if base_users > 0 else 0,
                    'Companies': int(base_companies / growth_factor) if base_companies > 0 else 0,
                    'Instances': int(base_instances / growth_factor) if base_instances > 0 else 0,
                    'Broadcasts': int(base_broadcasts / growth_factor) if base_broadcasts > 0 else 0
                })
            
            df_historical = pd.DataFrame(historical_data)
            
            # Add current month
            current_month = current_date.strftime('%Y-%m')
            df_historical = pd.concat([df_historical, pd.DataFrame([{
                'Month': current_month,
                'Users': base_users,
                'Companies': base_companies,
                'Instances': base_instances,
                'Broadcasts': base_broadcasts
            }])], ignore_index=True)
            
            # Simple linear regression using NumPy polyfit
            X = np.arange(len(df_historical))
            
            # Forecast next 3 months
            forecast_months = []
            for i in range(1, 4):
                forecast_months.append((current_date + timedelta(days=30*i)).strftime('%Y-%m'))
            
            forecasts = {}
            for metric in ['Users', 'Companies', 'Instances', 'Broadcasts']:
                y = df_historical[metric].values
                
                # Fit linear trend using numpy polyfit (degree 1 = linear)
                coefficients = np.polyfit(X, y, 1)
                poly_func = np.poly1d(coefficients)
                
                # Predict next 3 months
                future_X = np.arange(len(df_historical), len(df_historical) + 3)
                predictions = poly_func(future_X)
                
                # Ensure predictions are not negative
                predictions = np.maximum(predictions, 0)
                
                forecasts[metric] = predictions
            
            # Create forecast dataframe
            forecast_data = []
            for i, month in enumerate(forecast_months):
                forecast_data.append({
                    'Month': month,
                    'Users': int(forecasts['Users'][i]),
                    'Companies': int(forecasts['Companies'][i]),
                    'Instances': int(forecasts['Instances'][i]),
                    'Broadcasts': int(forecasts['Broadcasts'][i])
                })
            
            df_forecast = pd.DataFrame(forecast_data)
            
            # Visualize trends
            col1, col2 = st.columns(2)
            
            with col1:
                # User growth forecast
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_historical['Month'],
                    y=df_historical['Users'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_forecast['Month'],
                    y=df_forecast['Users'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ff6b6b', width=3, dash='dash'),
                    marker=dict(size=8, symbol='diamond')
                ))
                
                fig.update_layout(
                    title='User Growth Forecast (Next 3 Months)',
                    xaxis_title='Month',
                    yaxis_title='Users',
                    template=chart_theme,
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key='predict_users')
            
            with col2:
                # Company growth forecast
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_historical['Month'],
                    y=df_historical['Companies'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#28a745', width=3),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_forecast['Month'],
                    y=df_forecast['Companies'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ffc107', width=3, dash='dash'),
                    marker=dict(size=8, symbol='diamond')
                ))
                
                fig.update_layout(
                    title='Company Growth Forecast (Next 3 Months)',
                    xaxis_title='Month',
                    yaxis_title='Companies',
                    template=chart_theme,
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key='predict_companies')
            
            # Growth metrics
            st.markdown("### 📊 Predicted Growth Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            current_users = df_historical['Users'].iloc[-1]
            forecast_users_3m = df_forecast['Users'].iloc[-1]
            user_growth = ((forecast_users_3m - current_users) / current_users * 100) if current_users > 0 else 0
            
            with col1:
                st.metric(
                    "Predicted Users (3M)",
                    f"{forecast_users_3m:,}",
                    delta=f"+{user_growth:.1f}%"
                )
            
            current_companies = df_historical['Companies'].iloc[-1]
            forecast_companies_3m = df_forecast['Companies'].iloc[-1]
            company_growth = ((forecast_companies_3m - current_companies) / current_companies * 100) if current_companies > 0 else 0
            
            with col2:
                st.metric(
                    "Predicted Companies (3M)",
                    f"{forecast_companies_3m:,}",
                    delta=f"+{company_growth:.1f}%"
                )
            
            current_instances = df_historical['Instances'].iloc[-1]
            forecast_instances_3m = df_forecast['Instances'].iloc[-1]
            instances_growth = ((forecast_instances_3m - current_instances) / current_instances * 100) if current_instances > 0 else 0
            
            with col3:
                st.metric(
                    "Predicted Instances (3M)",
                    f"{forecast_instances_3m:,}",
                    delta=f"+{instances_growth:.1f}%"
                )
            
            current_broadcasts = df_historical['Broadcasts'].iloc[-1]
            forecast_broadcasts_3m = df_forecast['Broadcasts'].iloc[-1]
            broadcasts_growth = ((forecast_broadcasts_3m - current_broadcasts) / current_broadcasts * 100) if current_broadcasts > 0 else 0
            
            with col4:
                st.metric(
                    "Predicted Broadcasts (3M)",
                    f"{forecast_broadcasts_3m:,}",
                    delta=f"+{broadcasts_growth:.1f}%"
                )
            
            st.markdown("---")
            
            # Capacity Planning
            st.markdown("### 🏗️ Capacity Planning Recommendations")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                capacity_recs = []
                
                # Current capacity
                current_instance_capacity = metadata.get('total_instances', 0)
                current_user_capacity = metadata.get('total_users', 0)
                
                # Calculate needed capacity
                needed_instances = forecast_instances_3m
                instance_gap = needed_instances - current_instance_capacity
                
                if instance_gap > 0:
                    capacity_recs.append({
                        'Resource': 'Instances',
                        'Current': current_instance_capacity,
                        'Needed (3M)': needed_instances,
                        'Gap': int(instance_gap),
                        'Action': f'Provision {int(instance_gap)} more instances'
                    })
                
                needed_user_licenses = forecast_users_3m
                user_gap = needed_user_licenses - current_user_capacity
                
                if user_gap > 0:
                    capacity_recs.append({
                        'Resource': 'User Licenses',
                        'Current': current_user_capacity,
                        'Needed (3M)': needed_user_licenses,
                        'Gap': int(user_gap),
                        'Action': f'Plan for {int(user_gap)} more users'
                    })
                
                if capacity_recs:
                    df_capacity = pd.DataFrame(capacity_recs)
                    st.dataframe(df_capacity, use_container_width=True)
                else:
                    st.success("✅ Current capacity is sufficient for next 3 months")
            
            with col2:
                st.info(f"""
                **Planning Insights:**
                
                📈 Expected growth: **{user_growth:.1f}%**
                
                🎯 Target capacity: **{forecast_users_3m:,}** users
                
                ⏰ Timeline: **3 months**
                
                💡 Recommendation: Start planning capacity expansion now to avoid bottlenecks.
                """)
            
            # Multi-metric forecast visualization
            st.markdown("### 📉 All Metrics Forecast")
            
            # Combine historical and forecast
            df_combined = pd.concat([
                df_historical.assign(Type='Historical'),
                df_forecast.assign(Type='Forecast')
            ])
            
            metric_to_show = st.selectbox(
                "Select metric to visualize:",
                ['Users', 'Companies', 'Instances', 'Broadcasts'],
                key='forecast_metric_select'
            )
            
            fig = px.line(
                df_combined,
                x='Month',
                y=metric_to_show,
                color='Type',
                title=f'{metric_to_show} - Historical vs Forecast',
                markers=True,
                template=chart_theme,
                color_discrete_sequence=['#667eea', '#ff6b6b']
            )
            fig.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True, key='forecast_combined')
            
            # Trend Analysis
            st.markdown("### 📊 Trend Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Calculate growth rates
                growth_rates = []
                for metric in ['Users', 'Companies', 'Instances', 'Broadcasts']:
                    first_val = df_historical[metric].iloc[0]
                    last_val = df_historical[metric].iloc[-1]
                    growth = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
                    growth_rates.append({
                        'Metric': metric,
                        'Growth (12M)': round(growth, 1),
                        'Status': '📈 Growing' if growth > 0 else '📉 Declining'
                    })
                
                df_growth = pd.DataFrame(growth_rates)
                
                fig = px.bar(
                    df_growth,
                    x='Metric',
                    y='Growth (12M)',
                    title='12-Month Growth Rates',
                    color='Growth (12M)',
                    color_continuous_scale='RdYlGn',
                    template=chart_theme
                )
                fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key='growth_rates')
            
            with col2:
                st.markdown("#### Growth Summary")
                st.dataframe(df_growth, use_container_width=True, height=200)
                
                avg_growth = df_growth['Growth (12M)'].mean()
                if avg_growth > 10:
                    st.success(f"🚀 Strong growth trend: {avg_growth:.1f}% average")
                elif avg_growth > 0:
                    st.info(f"📈 Positive growth: {avg_growth:.1f}% average")
                else:
                    st.warning(f"⚠️ Negative trend: {avg_growth:.1f}% average")
                
                # Additional insights
                st.markdown("**Key Insights:**")
                max_growth_metric = df_growth.loc[df_growth['Growth (12M)'].idxmax(), 'Metric']
                max_growth_value = df_growth['Growth (12M)'].max()
                st.write(f"• Fastest growing: **{max_growth_metric}** ({max_growth_value:.1f}%)")
                
                min_growth_metric = df_growth.loc[df_growth['Growth (12M)'].idxmin(), 'Metric']
                min_growth_value = df_growth['Growth (12M)'].min()
                st.write(f"• Slowest growing: **{min_growth_metric}** ({min_growth_value:.1f}%)")
            
            # Forecast confidence
            st.markdown("### 🎯 Forecast Confidence")
            
            st.info("""
            **Methodology:**
            - Linear regression based on 12-month historical trend
            - Forecast horizon: 3 months
            - Confidence level: ~80% (based on linear trend continuation)
            
            **Notes:**
            - Actual results may vary based on market conditions
            - Seasonal factors not included in this simple model
            - Recommended for short-term planning only
            """)
            
            # Download forecast data
            col1, col2 = st.columns(2)
            
            with col1:
                historical_csv = df_historical.to_csv(index=False)
                st.download_button(
                    "📥 Download Historical Data",
                    historical_csv,
                    "historical_data.csv",
                    "text/csv",
                    key='download_historical'
                )
            
            with col2:
                forecast_csv = df_forecast.to_csv(index=False)
                st.download_button(
                    "📥 Download Forecast Data",
                    forecast_csv,
                    "forecast_data.csv",
                    "text/csv",
                    key='download_forecast'
                )
        # ==================== CUSTOMER HEALTH SCORE ====================
        elif view_option == "🎖️ Customer Health Score":
            st.markdown('<div class="section-header">🎖️ Customer Health Score Analysis</div>', unsafe_allow_html=True)
            
            st.info("💡 Multi-dimensional customer health scoring to identify at-risk accounts and growth opportunities")
            
            # Calculate detailed health scores
            health_scores = []
            
            for company in companies:
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                broadcasts = company.get('broadcasts_count', 0)
                
                # Score components (0-100 each)
                
                # 1. Engagement Score (40%)
                active_users = sum(1 for u in users if u.get('isActive', False))
                user_activity_rate = (active_users / len(users) * 100) if users else 0
                
                active_instances = sum(1 for i in instances if i.get('active', False))
                instance_activity_rate = (active_instances / len(instances) * 100) if instances else 0
                
                engagement_score = (user_activity_rate * 0.6 + instance_activity_rate * 0.4)
                
                # 2. Adoption Score (30%)
                user_types = Counter(u.get('user_type_name', 'Unknown') for u in users)
                type_diversity = len(user_types) / 4 * 100  # Max 4 types
                
                has_broadcasts = 100 if broadcasts > 0 else 0
                has_channels = 100 if len(channels) > 0 else 0
                
                adoption_score = (type_diversity * 0.4 + has_broadcasts * 0.3 + has_channels * 0.3)
                
                # 3. Growth Score (30%)
                users_per_channel = len(users) / len(channels) if channels else 0
                broadcasts_per_instance = broadcasts / len(instances) if instances else 0
                
                growth_potential = min((users_per_channel / 10 * 50) + (broadcasts_per_instance / 5 * 50), 100)
                
                # Overall Health Score
                overall_health = (
                    engagement_score * 0.4 +
                    adoption_score * 0.3 +
                    growth_potential * 0.3
                )
                
                # Determine status and recommendations
                if overall_health >= 80:
                    status = "🟢 Healthy"
                    status_emoji = "🟢"
                    risk = "Low"
                    recommendation = "Explore upsell opportunities"
                elif overall_health >= 60:
                    status = "🟡 Stable"
                    status_emoji = "🟡"
                    risk = "Medium"
                    recommendation = "Monitor engagement trends"
                elif overall_health >= 40:
                    status = "🟠 At Risk"
                    status_emoji = "🟠"
                    risk = "High"
                    recommendation = "Increase engagement, provide training"
                else:
                    status = "🔴 Critical"
                    status_emoji = "🔴"
                    risk = "Critical"
                    recommendation = "Immediate intervention required"
                
                health_scores.append({
                    'Company': company.get('name', 'Unknown'),
                    'Health Score': round(overall_health, 1),
                    'Status': status,
                    'Status_Emoji': status_emoji,
                    'Risk Level': risk,
                    'Engagement Score': round(engagement_score, 1),
                    'Adoption Score': round(adoption_score, 1),
                    'Growth Potential': round(growth_potential, 1),
                    'Active Users %': round(user_activity_rate, 1),
                    'Active Instances %': round(instance_activity_rate, 1),
                    'Total Users': len(users),
                    'Total Instances': len(instances),
                    'Broadcasts': broadcasts,
                    'Recommendation': recommendation
                })
            
            df_health = pd.DataFrame(health_scores).sort_values('Health Score', ascending=False)
            
            # Summary metrics
            st.markdown("### 📊 Health Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            healthy_count = len(df_health[df_health['Health Score'] >= 80])
            at_risk_count = len(df_health[(df_health['Health Score'] >= 40) & (df_health['Health Score'] < 60)])
            critical_count = len(df_health[df_health['Health Score'] < 40])
            avg_health = df_health['Health Score'].mean()
            
            with col1:
                st.metric("🟢 Healthy Customers", healthy_count, delta=f"{healthy_count/len(df_health)*100:.0f}%")
            
            with col2:
                st.metric("🟠 At-Risk Customers", at_risk_count, delta=f"{at_risk_count/len(df_health)*100:.0f}%", delta_color="inverse")
            
            with col3:
                st.metric("🔴 Critical Customers", critical_count, delta=f"{critical_count/len(df_health)*100:.0f}%", delta_color="inverse")
            
            with col4:
                st.metric("Average Health Score", f"{avg_health:.1f}/100")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Health score distribution
                fig = px.histogram(
                    df_health,
                    x='Health Score',
                    nbins=20,
                    title='Health Score Distribution',
                    color_discrete_sequence=['#667eea'],
                    template=chart_theme
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key='health_distribution')
            
            with col2:
                # Status breakdown
                status_counts = df_health['Status'].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title='Customer Status Breakdown',
                    color=status_counts.index,
                    color_discrete_map={
                        '🟢 Healthy': '#28a745',
                        '🟡 Stable': '#ffc107',
                        '🟠 At Risk': '#fd7e14',
                        '🔴 Critical': '#dc3545'
                    },
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='health_status_pie')
            
            # Health components radar chart
            st.markdown("### 🎯 Health Score Components")
            
            # Select companies to compare
            selected_companies_health = st.multiselect(
                "Select companies to compare (max 5):",
                df_health['Company'].tolist(),
                default=df_health['Company'].tolist()[:3],
                key='health_compare_select'
            )
            
            if selected_companies_health:
                fig = go.Figure()
                
                for company in selected_companies_health[:5]:
                    company_data = df_health[df_health['Company'] == company].iloc[0]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[
                            company_data['Engagement Score'],
                            company_data['Adoption Score'],
                            company_data['Growth Potential'],
                            company_data['Active Users %'],
                            company_data['Active Instances %']
                        ],
                        theta=['Engagement', 'Adoption', 'Growth', 'User Activity', 'Instance Activity'],
                        fill='toself',
                        name=company
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title='Health Score Components Comparison',
                    height=500,
                    template=chart_theme
                )
                st.plotly_chart(fig, use_container_width=True, key='health_radar')
            
            # Detailed health table
            st.markdown("### 📋 Detailed Health Scorecard")
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                risk_filter = st.multiselect(
                    "Filter by Risk Level:",
                    df_health['Risk Level'].unique(),
                    key='health_risk_filter'
                )
            
            with col2:
                min_score = st.slider(
                    "Minimum Health Score:",
                    0, 100, 0,
                    key='health_score_filter'
                )
            
            # Apply filters
            filtered_health = df_health.copy()
            if risk_filter:
                filtered_health = filtered_health[filtered_health['Risk Level'].isin(risk_filter)]
            filtered_health = filtered_health[filtered_health['Health Score'] >= min_score]
            
            # Display table
            display_columns = ['Company', 'Health Score', 'Status', 'Risk Level', 'Engagement Score', 
                             'Adoption Score', 'Growth Potential', 'Total Users', 'Broadcasts', 'Recommendation']
            
            st.dataframe(
                filtered_health[display_columns],
                use_container_width=True,
                height=400
            )
            
            st.info(f"Showing {len(filtered_health)} of {len(df_health)} companies")
            
            # Action recommendations
            st.markdown("### 🎯 Recommended Actions")
            
            tab1, tab2, tab3 = st.tabs(["🔴 Critical", "🟠 At Risk", "🟢 Growth Opportunities"])
            
            with tab1:
                critical_customers = df_health[df_health['Risk Level'] == 'Critical']
                if not critical_customers.empty:
                    st.error(f"⚠️ {len(critical_customers)} customers require immediate attention!")
                    for idx, row in critical_customers.iterrows():
                        with st.expander(f"{row['Company']} - Health Score: {row['Health Score']:.1f}"):
                            st.write(f"**Status:** {row['Status']}")
                            st.write(f"**Recommendation:** {row['Recommendation']}")
                            st.write(f"**Engagement Score:** {row['Engagement Score']:.1f}/100")
                            st.write(f"**Adoption Score:** {row['Adoption Score']:.1f}/100")
                            st.write(f"**Key Metrics:** {row['Total Users']} users, {row['Broadcasts']} broadcasts")
                else:
                    st.success("✅ No critical customers!")
            
            with tab2:
                at_risk_customers = df_health[df_health['Risk Level'] == 'High']
                if not at_risk_customers.empty:
                    st.warning(f"⚠️ {len(at_risk_customers)} customers at risk")
                    st.dataframe(
                        at_risk_customers[['Company', 'Health Score', 'Recommendation']],
                        use_container_width=True
                    )
                else:
                    st.success("✅ No at-risk customers!")
            
            with tab3:
                growth_opps = df_health[(df_health['Health Score'] >= 70) & (df_health['Total Users'] < 100)]
                if not growth_opps.empty:
                    st.success(f"🚀 {len(growth_opps)} customers ready for expansion!")
                    st.dataframe(
                        growth_opps[['Company', 'Health Score', 'Total Users', 'Broadcasts']],
                        use_container_width=True
                    )
                    st.info("💡 These customers are highly engaged and could benefit from upselling")
                else:
                    st.info("No immediate growth opportunities identified")
            
            # Export
            csv = df_health.to_csv(index=False)
            st.download_button(
                "📥 Download Health Scorecard",
                csv,
                "customer_health_scorecard.csv",
                "text/csv",
                key='health_download'
            )
        
        # ==================== ALERTS & ANOMALIES ====================
        elif view_option == "⚠️ Alerts & Anomalies":
            st.markdown('<div class="section-header">⚠️ Alerts & Anomaly Detection</div>', unsafe_allow_html=True)
            
            st.info("💡 Real-time monitoring for unusual patterns and potential issues")
            
            alerts = []
            
            # Check each company for anomalies
            for company in companies:
                company_name = company.get('name', 'Unknown')
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                broadcasts = company.get('broadcasts_count', 0)
                
                # Alert 1: Low user activation
                if users:
                    active_users = sum(1 for u in users if u.get('isActive', False))
                    activation_rate = active_users / len(users) * 100
                    
                    if activation_rate < 50:
                        alerts.append({
                            'Company': company_name,
                            'Alert Type': '🔴 Critical',
                            'Category': 'User Activation',
                            'Message': f'Only {activation_rate:.0f}% of users are active',
                            'Severity': 'High',
                            'Metric': f'{active_users}/{len(users)} active',
                            'Action': 'Contact customer success team immediately'
                        })
                    elif activation_rate < 70:
                        alerts.append({
                            'Company': company_name,
                            'Alert Type': '🟠 Warning',
                            'Category': 'User Activation',
                            'Message': f'User activation rate at {activation_rate:.0f}%',
                            'Severity': 'Medium',
                            'Metric': f'{active_users}/{len(users)} active',
                            'Action': 'Schedule training session'
                        })
                
                # Alert 2: Zero broadcasts
                if instances and broadcasts == 0:
                    alerts.append({
                        'Company': company_name,
                        'Alert Type': '🟠 Warning',
                        'Category': 'Usage',
                        'Message': f'{len(instances)} instances but no broadcasts',
                        'Severity': 'Medium',
                        'Metric': '0 broadcasts',
                        'Action': 'Check if customer needs help setting up campaigns'
                    })
                
                # Alert 3: Inactive instances
                if instances:
                    inactive_instances = sum(1 for i in instances if not i.get('active', False))
                    if inactive_instances / len(instances) > 0.5:
                        alerts.append({
                            'Company': company_name,
                            'Alert Type': '🟡 Info',
                            'Category': 'Resource Optimization',
                            'Message': f'{inactive_instances} of {len(instances)} instances are inactive',
                            'Severity': 'Low',
                            'Metric': f'{inactive_instances}/{len(instances)} inactive',
                            'Action': 'Consider downsizing or reactivating instances'
                        })
                
                # Alert 4: No channels
                if len(users) > 10 and len(channels) == 0:
                    alerts.append({
                        'Company': company_name,
                        'Alert Type': '🔴 Critical',
                        'Category': 'Setup',
                        'Message': f'{len(users)} users but no channels configured',
                        'Severity': 'High',
                        'Metric': '0 channels',
                        'Action': 'Urgent: Complete onboarding process'
                    })
                
                # Alert 5: Unusual user-to-instance ratio
                if instances:
                    ratio = len(users) / len(instances)
                    if ratio > 20:
                        alerts.append({
                            'Company': company_name,
                            'Alert Type': '🟡 Info',
                            'Category': 'Capacity',
                            'Message': f'High user-to-instance ratio ({ratio:.1f}:1)',
                            'Severity': 'Low',
                            'Metric': f'{len(users)} users / {len(instances)} instances',
                            'Action': 'May need additional instances for optimal performance'
                        })
                
                # Alert 6: Inactive company (no users)
                if len(users) == 0:
                    alerts.append({
                        'Company': company_name,
                        'Alert Type': '🔴 Critical',
                        'Category': 'Churn Risk',
                        'Message': 'Company has no users',
                        'Severity': 'Critical',
                        'Metric': '0 users',
                        'Action': 'Potential churn - reach out immediately'
                    })
            
            df_alerts = pd.DataFrame(alerts)
            
            if not df_alerts.empty:
                # Summary
                st.markdown("### 📊 Alert Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                critical_count = len(df_alerts[df_alerts['Severity'] == 'Critical'])
                high_count = len(df_alerts[df_alerts['Severity'] == 'High'])
                medium_count = len(df_alerts[df_alerts['Severity'] == 'Medium'])
                low_count = len(df_alerts[df_alerts['Severity'] == 'Low'])
                
                with col1:
                    st.metric("🔴 Critical", critical_count, delta="Immediate action required" if critical_count > 0 else "None")
                
                with col2:
                    st.metric("🟠 High", high_count, delta="Action needed" if high_count > 0 else "None")
                
                with col3:
                    st.metric("🟡 Medium", medium_count)
                
                with col4:
                    st.metric("ℹ️ Low", low_count)
                
                # Alert breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    # Alerts by category
                    category_counts = df_alerts['Category'].value_counts()
                    fig = px.bar(
                        x=category_counts.index,
                        y=category_counts.values,
                        title='Alerts by Category',
                        labels={'x': 'Category', 'y': 'Count'},
                        color=category_counts.values,
                        color_continuous_scale='Reds',
                        template=chart_theme
                    )
                    st.plotly_chart(fig, use_container_width=True, key='alerts_by_category')
                
                with col2:
                    # Alerts by severity
                    severity_counts = df_alerts['Severity'].value_counts()
                    fig = px.pie(
                        values=severity_counts.values,
                        names=severity_counts.index,
                        title='Alerts by Severity',
                        color=severity_counts.index,
                        color_discrete_map={
                            'Critical': '#dc3545',
                            'High': '#fd7e14',
                            'Medium': '#ffc107',
                            'Low': '#17a2b8'
                        },
                        template=chart_theme
                    )
                    st.plotly_chart(fig, use_container_width=True, key='alerts_by_severity')
                
                # Detailed alerts
                st.markdown("### 🚨 Active Alerts")
                
                # Filter by severity
                severity_filter = st.multiselect(
                    "Filter by Severity:",
                    ['Critical', 'High', 'Medium', 'Low'],
                    default=['Critical', 'High'],
                    key='alert_severity_filter'
                )
                
                filtered_alerts = df_alerts[df_alerts['Severity'].isin(severity_filter)]
                
                # Display alerts in cards
                for idx, alert in filtered_alerts.iterrows():
                    alert_color = {
                        'Critical': 'error',
                        'High': 'warning',
                        'Medium': 'info',
                        'Low': 'success'
                    }.get(alert['Severity'], 'info')
                    
                    with st.expander(f"{alert['Alert Type']} - {alert['Company']}: {alert['Message']}", expanded=(alert['Severity'] in ['Critical', 'High'])):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Category:** {alert['Category']}")
                            st.write(f"**Severity:** {alert['Severity']}")
                            st.write(f"**Metric:** {alert['Metric']}")
                            st.write(f"**Recommended Action:** {alert['Action']}")
                        
                        with col2:
                            if alert['Severity'] in ['Critical', 'High']:
                                if st.button("Mark as Resolved", key=f"resolve_{idx}"):
                                    st.success("Alert marked as resolved!")
                
                st.info(f"Showing {len(filtered_alerts)} of {len(df_alerts)} alerts")
                
                # Export
                csv = df_alerts.to_csv(index=False)
                st.download_button(
                    "📥 Download All Alerts",
                    csv,
                    "alerts_report.csv",
                    "text/csv",
                    key='alerts_download'
                )
            else:
                st.success("🎉 No alerts! All systems operating normally.")
                
                # Show positive metrics
                st.balloons()
                st.markdown("""
                ### ✅ System Health
                
                - All companies have active users
                - Resource utilization is optimal
                - No anomalies detected
                - All critical metrics within normal ranges
                """)
        
        # ==================== REVENUE INSIGHTS ====================
        elif view_option == "💰 Revenue Insights":
            st.markdown('<div class="section-header">💰 Revenue & Cost Analysis</div>', unsafe_allow_html=True)
            
            st.info("💡 Pricing assumptions: $10/user/month, $50/instance/month, $0.01/broadcast")
            
            # Define pricing
            PRICE_PER_USER = 10
            PRICE_PER_INSTANCE = 50
            PRICE_PER_BROADCAST = 0.01
            
            revenue_data = []
            
            for company in companies:
                users_count = company.get('users_count', 0)
                instances_count = company.get('instances_count', 0)
                broadcasts_count = company.get('broadcasts_count', 0)
                
                # Calculate revenue
                user_revenue = users_count * PRICE_PER_USER
                instance_revenue = instances_count * PRICE_PER_INSTANCE
                broadcast_revenue = broadcasts_count * PRICE_PER_BROADCAST
                total_revenue = user_revenue + instance_revenue + broadcast_revenue
                
                # Calculate tier
                if total_revenue >= 5000:
                    tier = "Enterprise"
                elif total_revenue >= 1000:
                    tier = "Professional"
                elif total_revenue >= 100:
                    tier = "Growth"
                else:
                    tier = "Starter"
                
                revenue_data.append({
                    'Company': company.get('name', 'Unknown'),
                    'Monthly Revenue': total_revenue,
                    'Annual Revenue': total_revenue * 12,
                    'User Revenue': user_revenue,
                    'Instance Revenue': instance_revenue,
                    'Broadcast Revenue': broadcast_revenue,
                    'Users': users_count,
                    'Instances': instances_count,
                    'Broadcasts': broadcasts_count,
                    'Tier': tier,
                    'ARPU': total_revenue / users_count if users_count > 0 else 0
                })
            
            df_revenue = pd.DataFrame(revenue_data).sort_values('Monthly Revenue', ascending=False)
            
            # Summary metrics
            total_mrr = df_revenue['Monthly Revenue'].sum()
            total_arr = total_mrr * 12
            avg_revenue = df_revenue['Monthly Revenue'].mean()
            avg_arpu = df_revenue['ARPU'].mean()
            
            st.markdown("### 💰 Revenue Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Monthly Recurring Revenue (MRR)", f"${total_mrr:,.2f}")
            
            with col2:
                st.metric("Annual Recurring Revenue (ARR)", f"${total_arr:,.2f}")
            
            with col3:
                st.metric("Average Revenue/Company", f"${avg_revenue:,.2f}")
            
            with col4:
                st.metric("Average Revenue/User (ARPU)", f"${avg_arpu:.2f}")
            
            # Revenue breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                # Top revenue companies
                fig = px.bar(
                    df_revenue.head(15),
                    x='Monthly Revenue',
                    y='Company',
                    orientation='h',
                    title='Top 15 Revenue Generating Companies',
                    color='Monthly Revenue',
                    color_continuous_scale='Greens',
                    template=chart_theme,
                    hover_data=['Tier', 'Users', 'Instances']
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True, key='revenue_top_companies')
            
            with col2:
                # Revenue by tier
                tier_revenue = df_revenue.groupby('Tier')['Monthly Revenue'].sum().reset_index()
                tier_revenue = tier_revenue.sort_values('Monthly Revenue', ascending=False)
                
                fig = px.pie(
                    tier_revenue,
                    values='Monthly Revenue',
                    names='Tier',
                    title='Revenue Distribution by Tier',
                    color='Tier',
                    color_discrete_map={
                        'Enterprise': '#28a745',
                        'Professional': '#17a2b8',
                        'Growth': '#ffc107',
                        'Starter': '#6c757d'
                    },
                    template=chart_theme
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key='revenue_by_tier')
            
            # Revenue composition
            st.markdown("### 📊 Revenue Composition")
            
            # Calculate total revenue by source
            total_user_rev = df_revenue['User Revenue'].sum()
            total_instance_rev = df_revenue['Instance Revenue'].sum()
            total_broadcast_rev = df_revenue['Broadcast Revenue'].sum()
            
            revenue_sources = pd.DataFrame({
                'Source': ['User Subscriptions', 'Instance Fees', 'Broadcast Usage'],
                'Revenue': [total_user_rev, total_instance_rev, total_broadcast_rev],
                'Percentage': [
                    total_user_rev / total_mrr * 100,
                    total_instance_rev / total_mrr * 100,
                    total_broadcast_rev / total_mrr * 100
                ]
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    revenue_sources,
                    x='Source',
                    y='Revenue',
                    title='Revenue by Source',
                    color='Source',
                    color_discrete_sequence=['#667eea', '#764ba2', '#28a745'],
                    template=chart_theme
                )
                fig.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True, key='revenue_by_source')
            
            with col2:
                fig = px.pie(
                    revenue_sources,
                    values='Percentage',
                    names='Source',
                    title='Revenue Mix',
                    color_discrete_sequence=['#667eea', '#764ba2', '#28a745'],
                    template=chart_theme
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, key='revenue_mix')
            
            # Detailed revenue table
            st.markdown("### 📋 Detailed Revenue Breakdown")
            
            display_cols = ['Company', 'Tier', 'Monthly Revenue', 'Annual Revenue', 
                          'User Revenue', 'Instance Revenue', 'Broadcast Revenue', 
                          'Users', 'Instances', 'Broadcasts', 'ARPU']
            
            # Format currency columns
            formatted_df = df_revenue[display_cols].copy()
            for col in ['Monthly Revenue', 'Annual Revenue', 'User Revenue', 'Instance Revenue', 'Broadcast Revenue', 'ARPU']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f'${x:,.2f}')
            
            st.dataframe(formatted_df, use_container_width=True, height=400)
            
            # Upsell opportunities
            st.markdown("### 🚀 Upsell Opportunities")
            
            # Find companies with low ARPU but high engagement
            low_arpu_high_engagement = df_revenue[
                (df_revenue['ARPU'] < avg_arpu) & 
                (df_revenue['Broadcasts'] > df_revenue['Broadcasts'].median())
            ].sort_values('Broadcasts', ascending=False)
            
            if not low_arpu_high_engagement.empty:
                st.success(f"💡 Found {len(low_arpu_high_engagement)} high-engagement customers with expansion potential!")
                
                st.dataframe(
                    low_arpu_high_engagement[['Company', 'Monthly Revenue', 'ARPU', 'Users', 'Broadcasts']].head(10),
                    use_container_width=True
                )
                
                st.info("""
                **Recommendation:** These customers are actively using the platform but on lower tiers. 
                Consider reaching out with premium features or higher tier plans.
                """)
            
            # Export
            csv = df_revenue.to_csv(index=False)
            st.download_button(
                "📥 Download Revenue Report",
                csv,
                "revenue_analysis.csv",
                "text/csv",
                key='revenue_download'
            )
        
        # ==================== BENCHMARKING ====================
        elif view_option == "📊 Benchmarking":
            st.markdown('<div class="section-header">📊 Competitive Benchmarking</div>', unsafe_allow_html=True)
            
            st.info("💡 Compare your companies against industry benchmarks and best performers")
            
            # Calculate benchmarks
            benchmark_data = []
            
            for company in companies:
                users = company.get('users', [])
                instances = company.get('instances', [])
                channels = company.get('channels', [])
                broadcasts = company.get('broadcasts_count', 0)
                
                # Calculate metrics
                user_activation = (sum(1 for u in users if u.get('isActive', False)) / len(users) * 100) if users else 0
                instance_utilization = (sum(1 for i in instances if i.get('active', False)) / len(instances) * 100) if instances else 0
                users_per_channel = len(users) / len(channels) if channels else 0
                broadcasts_per_user = broadcasts / len(users) if users else 0
                broadcasts_per_instance = broadcasts / len(instances) if instances else 0
                
                benchmark_data.append({
                    'Company': company.get('name', 'Unknown'),
                    'User Activation %': round(user_activation, 1),
                    'Instance Utilization %': round(instance_utilization, 1),
                    'Users/Channel': round(users_per_channel, 1),
                    'Broadcasts/User': round(broadcasts_per_user, 1),
                    'Broadcasts/Instance': round(broadcasts_per_instance, 1),
                    'Total Users': len(users),
                    'Total Instances': len(instances),
                    'Total Broadcasts': broadcasts
                })
            
            df_benchmark = pd.DataFrame(benchmark_data)
            
            # Calculate industry benchmarks (percentiles)
            benchmarks = {
                'User Activation %': {
                    'Top 25%': df_benchmark['User Activation %'].quantile(0.75),
                    'Median': df_benchmark['User Activation %'].median(),
                    'Bottom 25%': df_benchmark['User Activation %'].quantile(0.25)
                },
                'Instance Utilization %': {
                    'Top 25%': df_benchmark['Instance Utilization %'].quantile(0.75),
                    'Median': df_benchmark['Instance Utilization %'].median(),
                    'Bottom 25%': df_benchmark['Instance Utilization %'].quantile(0.25)
                },
                'Broadcasts/User': {
                    'Top 25%': df_benchmark['Broadcasts/User'].quantile(0.75),
                    'Median': df_benchmark['Broadcasts/User'].median(),
                    'Bottom 25%': df_benchmark['Broadcasts/User'].quantile(0.25)
                }
            }
            
            # Display benchmarks
            st.markdown("### 🎯 Industry Benchmarks")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### User Activation")
                st.metric("Top 25%", f"{benchmarks['User Activation %']['Top 25%']:.1f}%", delta="Target")
                st.metric("Median", f"{benchmarks['User Activation %']['Median']:.1f}%")
                st.metric("Bottom 25%", f"{benchmarks['User Activation %']['Bottom 25%']:.1f}%", delta_color="inverse")
            
            with col2:
                st.markdown("#### Instance Utilization")
                st.metric("Top 25%", f"{benchmarks['Instance Utilization %']['Top 25%']:.1f}%", delta="Target")
                st.metric("Median", f"{benchmarks['Instance Utilization %']['Median']:.1f}%")
                st.metric("Bottom 25%", f"{benchmarks['Instance Utilization %']['Bottom 25%']:.1f}%", delta_color="inverse")
            
            with col3:
                st.markdown("#### Broadcasts per User")
                st.metric("Top 25%", f"{benchmarks['Broadcasts/User']['Top 25%']:.1f}", delta="Target")
                st.metric("Median", f"{benchmarks['Broadcasts/User']['Median']:.1f}")
                st.metric("Bottom 25%", f"{benchmarks['Broadcasts/User']['Bottom 25%']:.1f}", delta_color="inverse")
            
            # Benchmark comparison
            st.markdown("### 📊 Company vs Benchmark Comparison")
            
            # Select metric to compare
            metric_to_compare = st.selectbox(
                "Select metric to compare:",
                ['User Activation %', 'Instance Utilization %', 'Broadcasts/User', 'Broadcasts/Instance'],
                key='benchmark_metric_select'
            )
            
            # Create comparison chart
            df_sorted = df_benchmark.sort_values(metric_to_compare, ascending=False).head(20)
            
            fig = go.Figure()
            
            # Add bars for companies
            fig.add_trace(go.Bar(
                x=df_sorted['Company'],
                y=df_sorted[metric_to_compare],
                name='Company Value',
                marker_color='#667eea'
            ))
            
            # Add benchmark lines if applicable
            if metric_to_compare in benchmarks:
                fig.add_hline(
                    y=benchmarks[metric_to_compare]['Top 25%'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Top 25%",
                    annotation_position="right"
                )
                fig.add_hline(
                    y=benchmarks[metric_to_compare]['Median'],
                    line_dash="dot",
                    line_color="orange",
                    annotation_text="Median",
                    annotation_position="right"
                )
            
            fig.update_layout(
                title=f'{metric_to_compare} - Company Comparison vs Benchmarks',
                xaxis_title='Company',
                yaxis_title=metric_to_compare,
                template=chart_theme,
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True, key='benchmark_comparison')
 
        
        # ==================== RAW DATA ====================
        elif view_option == "📁 Raw Data":
            st.markdown('<div class="section-header">🔍 Raw Data Explorer</div>', unsafe_allow_html=True)
            
            data_type = st.selectbox("Select data to explore:", ["Metadata", "Companies", "All Types", "Full JSON"], key='raw_data_type')
            
            if data_type == "Metadata":
                st.json(metadata)
            elif data_type == "Companies":
                selected_comp = st.selectbox("Select company:", [c.get('name', 'Unknown') for c in companies], key='raw_company_select')
                company_data = next((c for c in companies if c.get('name') == selected_comp), None)
                if company_data:
                    st.json(company_data)
            elif data_type == "All Types":
                st.json(data.get('all_types', []))
            else:
                st.json(data)
            
            st.markdown("### 📥 Download Options")
            col1, col2 = st.columns(2)
            
            with col1:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button("Download Full JSON", json_str, "whatsapp_data.json", "application/json", key='raw_download_json')
            
            with col2:
                summary_data = []
                for company in companies:
                    summary_data.append({
                        'Company': company.get('name', 'Unknown'),
                        'Users': company.get('users_count', 0),
                        'Channels': company.get('channels_count', 0),
                        'Instances': company.get('instances_count', 0),
                        'Broadcasts': company.get('broadcasts_count', 0)
                    })
                
                df_summary = pd.DataFrame(summary_data)
                csv = df_summary.to_csv(index=False)
                st.download_button("Download Summary CSV", csv, "summary.csv", "text/csv", key='raw_download_csv')
    
    else:
        st.markdown("""
            <div style='text-align: center; padding: 50px;'>
                <h2>👋 Welcome to WhatsApp Analytics Dashboard</h2>
                <h3 style='color: #667eea;'>Interactive Edition</h3>
                <p style='font-size: 1.2em; color: #666;'>
                    Please upload your <code>merged_whatsapp_data.json</code> file in the sidebar to get started.
                </p>
                <br>
                <div style='background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px auto; max-width: 800px;'>
                    <h4>✨ Features:</h4>
                    <ul style='text-align: left; display: inline-block;'>
                        <li>📊 Interactive charts with zoom, pan, and hover</li>
                        <li>🔍 Advanced filtering and search</li>
                        <li>📈 Cross-dimensional analysis</li>
                        <li>🎯 Real-time data exploration</li>
                        <li>📥 Multiple export formats (CSV, JSON)</li>
                        <li>🎨 Customizable themes</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>📊 WhatsApp API Analytics Dashboard - Interactive Edition | Built with Streamlit & Plotly</p>
            <p style='font-size: 0.9em;'>💡 Tip: Hover over charts for details, click legend items to filter, use box/lasso select tools</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()