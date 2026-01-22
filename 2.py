import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10  

def load_merged_data(filepath):
    """Load the merged JSON data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_date(date_obj):
    """Extract date from MongoDB date format"""
    if not date_obj:
        return None
    if isinstance(date_obj, dict) and '$date' in date_obj:
        try:
            return datetime.fromisoformat(date_obj['$date'].replace('Z', '+00:00'))
        except:
            return None
    return None

def create_company_overview_chart(data, output_dir):
    """Create comprehensive company overview visualization"""
    companies = data.get('companies', [])

    company_names = [] 
    users_counts = []
    channels_counts = []
    instances_counts = []
    broadcasts_counts = []
    
    for company in companies:
        name = company.get('name', 'Unknown')
        if len(name) > 15:
            name = name[:12] + '...'
        company_names.append(name)
        users_counts.append(company.get('users_count', 0))
        channels_counts.append(company.get('channels_count', 0))
        instances_counts.append(company.get('instances_count', 0))
        broadcasts_counts.append(company.get('broadcasts_count', 0))
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Company Overview Dashboard', fontsize=20, fontweight='bold', y=0.995)
    
    # 1. Users per Company
    axes[0, 0].bar(company_names, users_counts, color='#667eea', alpha=0.8)
    axes[0, 0].set_title('Users per Company', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Company')
    axes[0, 0].set_ylabel('Number of Users')
    axes[0, 0].tick_params(axis='x', rotation=45)
    for i, v in enumerate(users_counts):
        axes[0, 0].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 2. Instances per Company
    axes[0, 1].bar(company_names, instances_counts, color='#764ba2', alpha=0.8)
    axes[0, 1].set_title('Instances per Company', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Company')
    axes[0, 1].set_ylabel('Number of Instances')
    axes[0, 1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(instances_counts):
        axes[0, 1].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 3. Channels per Company
    axes[1, 0].bar(company_names, channels_counts, color='#28a745', alpha=0.8)
    axes[1, 0].set_title('Channels per Company', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Company')
    axes[1, 0].set_ylabel('Number of Channels')
    axes[1, 0].tick_params(axis='x', rotation=45)
    for i, v in enumerate(channels_counts):
        axes[1, 0].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 4. Broadcasts per Company
    axes[1, 1].bar(company_names, broadcasts_counts, color='#ffc107', alpha=0.8)
    axes[1, 1].set_title('Broadcasts per Company', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Company')
    axes[1, 1].set_ylabel('Number of Broadcasts')
    axes[1, 1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(broadcasts_counts):
        axes[1, 1].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_company_overview.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 01_company_overview.png")
    plt.close()

def create_user_type_analysis(data, output_dir):
    """Analyze user types across all companies"""
    all_user_types = Counter()
    company_user_types = defaultdict(Counter)
    
    for company in data.get('companies', []):
        company_name = company.get('name', 'Unknown')
        for user in company.get('users', []):
            user_type = user.get('user_type_name', 'Unknown')
            all_user_types[user_type] += 1
            company_user_types[company_name][user_type] += 1
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('User Type Analysis', fontsize=18, fontweight='bold')
    
    # 1. Overall user type distribution (Pie chart)
    colors = ['#667eea', '#764ba2', '#28a745', '#ffc107']
    wedges, texts, autotexts = ax1.pie(all_user_types.values(), 
                                        labels=all_user_types.keys(),
                                        autopct='%1.1f%%',
                                        colors=colors,
                                        startangle=90,
                                        textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax1.set_title('Overall User Type Distribution', fontsize=14, fontweight='bold')
    
    # 2. User types by company (Stacked bar)
    companies = list(company_user_types.keys())
    user_types = ['Agent', 'Admin', 'Supervisor', 'AI']
    
    data_matrix = []
    for user_type in user_types:
        data_matrix.append([company_user_types[comp][user_type] for comp in companies])
    
    x = np.arange(len(companies))
    width = 0.6
    
    bottom = np.zeros(len(companies))
    for i, (user_type, values) in enumerate(zip(user_types, data_matrix)):
        ax2.bar(x, values, width, label=user_type, bottom=bottom, color=colors[i], alpha=0.8)
        bottom += values
    
    ax2.set_title('User Types by Company', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Company')
    ax2.set_ylabel('Number of Users')
    ax2.set_xticks(x)
    ax2.set_xticklabels([c[:12] + '...' if len(c) > 15 else c for c in companies], rotation=45, ha='right')
    ax2.legend(title='User Type')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_user_type_analysis.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 02_user_type_analysis.png")
    plt.close()

def create_instance_type_analysis(data, output_dir):
    """Analyze instance types and their status"""
    instance_types = Counter()
    instance_status = Counter()
    type_status_matrix = defaultdict(Counter)
    
    for company in data.get('companies', []):
        for instance in company.get('instances', []):
            type_details = instance.get('type_details') or {}
            type_name = type_details.get('name', 'Unknown')
            status = instance.get('status', 'Unknown')
            is_active = instance.get('active', False)
            
            instance_types[type_name] += 1
            instance_status[status] += 1
            type_status_matrix[type_name]['Active' if is_active else 'Inactive'] += 1
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Instance Analysis', fontsize=18, fontweight='bold')
    
    # 1. Instance types distribution
    types = list(instance_types.keys())
    counts = list(instance_types.values())
    colors_palette = sns.color_palette("husl", len(types))
    
    ax1.barh(types, counts, color=colors_palette, alpha=0.8)
    ax1.set_title('Instances by Type', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Count')
    for i, v in enumerate(counts):
        ax1.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    
    # 2. Instance status distribution
    statuses = list(instance_status.keys())
    status_counts = list(instance_status.values())
    colors_status = ['#28a745', '#ffc107', '#dc3545', '#6c757d'][:len(statuses)]
    
    ax2.pie(status_counts, labels=statuses, autopct='%1.1f%%', 
            colors=colors_status, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('Instance Status Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_instance_analysis.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 03_instance_analysis.png")
    plt.close()

def create_activity_heatmap(data, output_dir):
    """Create activity heatmap showing user and instance activity by company"""
    companies = data.get('companies', [])
    
    company_names = []
    active_users_pct = []
    active_instances_pct = []
    active_channels_pct = []
    
    for company in companies:
        name = company.get('name', 'Unknown')
        if len(name) > 15:
            name = name[:12] + '...'
        company_names.append(name)
        
        # Calculate active percentages
        users = company.get('users', [])
        if users:
            active_u = sum(1 for u in users if u.get('user_status', u.get('isActive', False)))
            active_users_pct.append((active_u / len(users)) * 100)
        else:
            active_users_pct.append(0)
        
        instances = company.get('instances', [])
        if instances:
            active_i = sum(1 for i in instances if i.get('active', False))
            active_instances_pct.append((active_i / len(instances)) * 100)
        else:
            active_instances_pct.append(0)
        
        channels = company.get('channels', [])
        if channels:
            active_c = sum(1 for c in channels if c.get('isActive', False))
            active_channels_pct.append((active_c / len(channels)) * 100)
        else:
            active_channels_pct.append(0)
    
    # Create heatmap data
    heatmap_data = np.array([active_users_pct, active_instances_pct, active_channels_pct])
    
    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # Set ticks and labels
    ax.set_yticks(np.arange(3))
    ax.set_yticklabels(['Active Users %', 'Active Instances %', 'Active Channels %'])
    ax.set_xticks(np.arange(len(company_names)))
    ax.set_xticklabels(company_names, rotation=45, ha='right')
    
    # Add text annotations
    for i in range(3):
        for j in range(len(company_names)):
            text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}%',
                          ha="center", va="center", color="black", fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Activity Percentage', rotation=270, labelpad=20)
    
    ax.set_title('Activity Heatmap by Company', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_activity_heatmap.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 04_activity_heatmap.png")
    plt.close()

def create_broadcast_analysis(data, output_dir):
    """Analyze broadcast campaigns"""
    broadcast_status = Counter()
    company_broadcasts = defaultdict(int)
    
    for company in data.get('companies', []):
        company_name = company.get('name', 'Unknown')
        broadcasts = company.get('broadcasts', [])
        company_broadcasts[company_name] = len(broadcasts)
        
        for bc in broadcasts:
            status = bc.get('status', 'Unknown')
            broadcast_status[status] += 1
    
    if not broadcast_status:
        print("⚠️ No broadcast data available, skipping broadcast analysis chart")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Broadcast Campaign Analysis', fontsize=18, fontweight='bold')
    
    # 1. Broadcast status
    statuses = list(broadcast_status.keys())
    counts = list(broadcast_status.values())
    colors = sns.color_palette("Set2", len(statuses))
    
    ax1.pie(counts, labels=statuses, autopct='%1.1f%%', colors=colors, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Broadcast Status Distribution', fontsize=14, fontweight='bold')
    
    # 2. Broadcasts by company
    companies = list(company_broadcasts.keys())
    broadcast_counts = list(company_broadcasts.values())
    
    ax2.bar(companies, broadcast_counts, color='#667eea', alpha=0.8)
    ax2.set_title('Broadcasts per Company', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Company')
    ax2.set_ylabel('Number of Broadcasts')
    ax2.tick_params(axis='x', rotation=45)
    for i, v in enumerate(broadcast_counts):
        ax2.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_broadcast_analysis.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 05_broadcast_analysis.png")
    plt.close()

def create_speed_messages_analysis(data, output_dir):
    """Analyze speed messages distribution"""
    company_speed_msgs = defaultdict(int)
    channel_speed_msgs = []
    
    for company in data.get('companies', []):
        company_name = company.get('name', 'Unknown')
        total_speed_msgs = company.get('speedMessages_count', 0)
        company_speed_msgs[company_name] = total_speed_msgs
        
        for channel in company.get('channels', []):
            channel_speed_msgs.append({
                'company': company_name,
                'channel': channel.get('name', 'Unknown'),
                'count': channel.get('speedMessages_count', 0)
            })
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Speed Messages Analysis', fontsize=18, fontweight='bold')
    
    # 1. Speed messages by company
    companies = list(company_speed_msgs.keys())
    counts = list(company_speed_msgs.values())
    
    ax1.bar(companies, counts, color='#28a745', alpha=0.8)
    ax1.set_title('Speed Messages per Company', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Company')
    ax1.set_ylabel('Number of Speed Messages')
    ax1.tick_params(axis='x', rotation=45)
    for i, v in enumerate(counts):
        ax1.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 2. Top 10 channels by speed messages
    sorted_channels = sorted(channel_speed_msgs, key=lambda x: x['count'], reverse=True)[:10]
    
    if sorted_channels:
        channel_labels = [f"{c['company'][:8]}: {c['channel'][:15]}" for c in sorted_channels]
        channel_counts = [c['count'] for c in sorted_channels]
        
        ax2.barh(channel_labels, channel_counts, color='#ffc107', alpha=0.8)
        ax2.set_title('Top 10 Channels by Speed Messages', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Number of Speed Messages')
        for i, v in enumerate(channel_counts):
            ax2.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'No channel data available', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_speed_messages_analysis.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 06_speed_messages_analysis.png")
    plt.close()

def create_resource_utilization_chart(data, output_dir):
    """Show resource utilization and efficiency"""
    companies = data.get('companies', [])
    
    company_names = []
    users_per_channel = []
    instances_utilization = []
    broadcasts_per_instance = []
    
    for company in companies:
        name = company.get('name', 'Unknown')
        if len(name) > 15:
            name = name[:12] + '...'
        company_names.append(name)
        
        # Users per channel ratio
        users = company.get('users_count', 0)
        channels = company.get('channels_count', 1)  # Avoid division by zero
        users_per_channel.append(users / channels if channels > 0 else 0)
        
        # Instance utilization (active %)
        instances = company.get('instances', [])
        if instances:
            active = sum(1 for i in instances if i.get('active', False))
            instances_utilization.append((active / len(instances)) * 100)
        else:
            instances_utilization.append(0)
        
        # Broadcasts per instance
        broadcasts = company.get('broadcasts_count', 0)
        instance_count = company.get('instances_count', 1)
        broadcasts_per_instance.append(broadcasts / instance_count if instance_count > 0 else 0)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Resource Utilization Metrics', fontsize=18, fontweight='bold')
    
    # 1. Users per Channel
    axes[0].bar(company_names, users_per_channel, color='#667eea', alpha=0.8)
    axes[0].set_title('Users per Channel Ratio', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Company')
    axes[0].set_ylabel('Users per Channel')
    axes[0].tick_params(axis='x', rotation=45)
    
    # 2. Instance Utilization
    axes[1].bar(company_names, instances_utilization, color='#28a745', alpha=0.8)
    axes[1].set_title('Instance Utilization (%)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Company')
    axes[1].set_ylabel('Active Instances %')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% threshold')
    axes[1].legend()
    
    # 3. Broadcasts per Instance
    axes[2].bar(company_names, broadcasts_per_instance, color='#ffc107', alpha=0.8)
    axes[2].set_title('Broadcasts per Instance', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Company')
    axes[2].set_ylabel('Avg Broadcasts per Instance')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_resource_utilization.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 07_resource_utilization.png")
    plt.close()

def create_executive_summary_dashboard(data, output_dir):
    """Create a single-page executive summary dashboard"""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Main title
    fig.suptitle('Executive Summary Dashboard', fontsize=24, fontweight='bold', y=0.98)
    
    metadata = data.get('metadata', {})
    companies = data.get('companies', [])
    
    # 1. Key Metrics (Top left - larger)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.axis('off')
    
    metrics_text = f"""
    📊 PLATFORM OVERVIEW
    
    Total Companies: {metadata.get('total_companies', 0)}
    Total Users: {metadata.get('total_users', 0)}
    Total Channels: {metadata.get('total_channels', 0)}
    Total Instances: {metadata.get('total_instances', 0)}
    Total Broadcasts: {metadata.get('total_broadcasts', 0)}
    Total Speed Messages: {metadata.get('total_speedMessages', 0)}
    """
    ax1.text(0.1, 0.5, metrics_text, fontsize=14, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='#e8f4f8', alpha=0.8))
    
    # 2. User Type Distribution (Top right)
    ax2 = fig.add_subplot(gs[0, 2])
    all_user_types = Counter()
    for company in companies:
        for user in company.get('users', []):
            user_type = user.get('user_type_name', 'Unknown')
            all_user_types[user_type] += 1
    
    if all_user_types:
        colors = ['#667eea', '#764ba2', '#28a745', '#ffc107']
        ax2.pie(all_user_types.values(), labels=all_user_types.keys(), autopct='%1.0f%%',
                colors=colors, textprops={'fontsize': 10})
        ax2.set_title('User Types', fontsize=12, fontweight='bold')
    
    # 3. Company Comparison (Middle row)
    ax3 = fig.add_subplot(gs[1, :])
    company_names = [c.get('name', 'Unknown')[:12] for c in companies]
    users_counts = [c.get('users_count', 0) for c in companies]
    instances_counts = [c.get('instances_count', 0) for c in companies]
    
    x = np.arange(len(company_names))
    width = 0.35
    
    ax3.bar(x - width/2, users_counts, width, label='Users', color='#667eea', alpha=0.8)
    ax3.bar(x + width/2, instances_counts, width, label='Instances', color='#764ba2', alpha=0.8)
    ax3.set_xlabel('Company', fontweight='bold')
    ax3.set_ylabel('Count', fontweight='bold')
    ax3.set_title('Users vs Instances by Company', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(company_names, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Instance Types (Bottom left)
    ax4 = fig.add_subplot(gs[2, 0])
    instance_types = Counter()
    for company in companies:
        for instance in company.get('instances', []):
            type_details = instance.get('type_details') or {}
            type_name = type_details.get('name', 'Unknown')
            instance_types[type_name] += 1
    
    if instance_types:
        types = list(instance_types.keys())[:5]  # Top 5
        counts = [instance_types[t] for t in types]
        ax4.barh(types, counts, color=sns.color_palette("husl", len(types)), alpha=0.8)
        ax4.set_title('Top Instance Types', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Count')
    
    # 5. Activity Status (Bottom middle)
    ax5 = fig.add_subplot(gs[2, 1])
    total_users = 0
    active_users = 0
    total_instances = 0
    active_instances = 0
    
    for company in companies:
        for user in company.get('users', []):
            total_users += 1
            if user.get('user_status', user.get('isActive', False)):
                active_users += 1
        for instance in company.get('instances', []):
            total_instances += 1
            if instance.get('active', False):
                active_instances += 1
    
    categories = ['Users', 'Instances']
    active = [active_users, active_instances]
    inactive = [total_users - active_users, total_instances - active_instances]
    
    x_cat = np.arange(len(categories))
    ax5.bar(x_cat, active, label='Active', color='#28a745', alpha=0.8)
    ax5.bar(x_cat, inactive, bottom=active, label='Inactive', color='#dc3545', alpha=0.8)
    ax5.set_title('Active vs Inactive', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_cat)
    ax5.set_xticklabels(categories)
    ax5.legend()
    
    # 6. Top Performers (Bottom right)
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    # Find top companies by total activity
    company_scores = []
    for company in companies:
        score = (company.get('users_count', 0) + 
                company.get('instances_count', 0) + 
                company.get('broadcasts_count', 0))
        company_scores.append((company.get('name', 'Unknown'), score))
    
    company_scores.sort(key=lambda x: x[1], reverse=True)
    
    top_text = "🏆 TOP PERFORMERS\n\n"
    for i, (name, score) in enumerate(company_scores[:5], 1):
        top_text += f"{i}. {name[:20]}\n   Score: {score}\n\n"
    
    ax6.text(0.1, 0.9, top_text, fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='#fff3cd', alpha=0.8))
    
    plt.savefig(os.path.join(output_dir, '00_executive_summary.png'), dpi=300, bbox_inches='tight')
    print("✅ Created: 00_executive_summary.png")
    plt.close()

def main():
    filepath = input("Enter path to merged_whatsapp_data.json: ").strip()
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        return
    
    output_dir = input("Enter output directory for charts (default: ./analytics): ").strip() or './analytics'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n📊 Loading data and generating visualizations...")
    print("="*80)
    
    data = load_merged_data(filepath)
    
    # Generate all visualizations
    print("\n🎨 Creating visualizations...")
    create_executive_summary_dashboard(data, output_dir)
    create_company_overview_chart(data, output_dir)
    create_user_type_analysis(data, output_dir)
    create_instance_type_analysis(data, output_dir)
    create_activity_heatmap(data, output_dir)
    create_broadcast_analysis(data, output_dir)
    create_speed_messages_analysis(data, output_dir)
    create_resource_utilization_chart(data, output_dir)
    
    print("\n" + "="*80)
    print(f"✅ All visualizations created successfully!")
    print(f"📁 Output directory: {output_dir}/")
    print("="*80)
    print("\n📊 Generated Charts:")
    print("  00_executive_summary.png - One-page overview dashboard")
    print("  01_company_overview.png - Users, instances, channels, broadcasts by company")
    print("  02_user_type_analysis.png - User type distribution")
    print("  03_instance_analysis.png - Instance types and status")
    print("  04_activity_heatmap.png - Activity levels across companies")
    print("  05_broadcast_analysis.png - Broadcast campaign analysis")
    print("  06_speed_messages_analysis.png - Speed messages distribution")
    print("  07_resource_utilization.png - Resource efficiency metrics")
    print("\n💡 Use these charts in presentations, reports, or dashboards!")
    print("="*80)

if __name__ == "__main__":
    main()