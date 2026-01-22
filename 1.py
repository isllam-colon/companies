import json
import os
from collections import defaultdict, Counter
from datetime import datetime

def load_merged_data(filepath):
    """Load the merged JSON data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_date(date_obj):
    """Extract date from MongoDB date format"""
    if not date_obj:
        return None
    if isinstance(date_obj, dict) and '$date' in date_obj:
        return datetime.fromisoformat(date_obj['$date'].replace('Z', '+00:00'))
    return None

def analyze_companies(data):
    """Comprehensive company analysis"""
    print("\n" + "="*80)
    print("COMPANIES ANALYSIS")
    print("="*80)
    
    companies = data.get('companies', [])
    
    for company in companies:
        print(f"\n📊 Company: {company.get('name', 'Unknown')}")
        print("-" * 80)
        
        # Basic stats
        print(f"  Total Users: {company.get('users_count', 0)}")
        print(f"  Total Channels: {company.get('channels_count', 0)}")
        print(f"  Total Instances: {company.get('instances_count', 0)}")
        print(f"  Total Broadcasts: {company.get('broadcasts_count', 0)}")
        print(f"  Total Speed Messages: {company.get('speedMessages_count', 0)}")
        print(f"  Active Status: {'✅ Active' if company.get('isActive') else '❌ Inactive'}")
        
        # User type breakdown
        if company.get('users'):
            analyze_users(company['users'])
            
        # Instance analysis
        if company.get('instances'):
            analyze_instances(company['instances'])
        
        # Channel analysis
        if company.get('channels'):
            analyze_channels(company['channels'])
        
        # Broadcast analysis
        if company.get('broadcasts'):
            analyze_broadcasts(company['broadcasts'])

def analyze_users(users):
    """Analyze user distribution and activity"""
    print("\n  👥 USER BREAKDOWN:")
    
    # Count by type
    type_counts = Counter()
    active_count = 0
    inactive_count = 0
    
    for user in users:
        user_type = user.get('user_type_name', 'Unknown')
        type_counts[user_type] += 1
        
        if user.get('user_status', user.get('isActive', False)):
            active_count += 1
        else:
            inactive_count += 1
    
    print(f"    • Agents: {type_counts.get('Agent', 0)}")
    print(f"    • Admins: {type_counts.get('Admin', 0)}")
    print(f"    • Supervisors: {type_counts.get('Supervisor', 0)}")
    print(f"    • AI Users: {type_counts.get('AI', 0)}")
    print(f"    • Active Users: {active_count} ({active_count/len(users)*100:.1f}%)")
    print(f"    • Inactive Users: {inactive_count} ({inactive_count/len(users)*100:.1f}%)")

def analyze_instances(instances):
    """Analyze instance types and status"""
    print("\n  🔌 INSTANCE BREAKDOWN:")
    
    # Count by type
    type_counts = Counter()
    status_counts = Counter()
    active_count = 0
    
    for instance in instances:
        type_details = instance.get('type_details') or {}
        type_name = type_details.get('name', 'Unknown')
        type_counts[type_name] += 1
        
        status = instance.get('status', 'Unknown')
        status_counts[status] += 1
        
        if instance.get('active', False):
            active_count += 1
    
    print(f"    Active Instances: {active_count}/{len(instances)} ({active_count/len(instances)*100:.1f}%)")
    print(f"\n    By Type:")
    for type_name, count in type_counts.most_common():
        print(f"      • {type_name}: {count}")
    
    print(f"\n    By Status:")
    for status, count in status_counts.most_common():
        print(f"      • {status}: {count}")

def analyze_channels(channels):
    """Analyze channel activity"""
    print("\n  📢 CHANNEL BREAKDOWN:")
    
    active_channels = sum(1 for ch in channels if ch.get('isActive', False))
    total_speed_messages = sum(ch.get('speedMessages_count', 0) for ch in channels)
    
    print(f"    Active Channels: {active_channels}/{len(channels)} ({active_channels/len(channels)*100:.1f}%)")
    print(f"    Total Speed Messages across all channels: {total_speed_messages}")
    
    # Top channels by speed messages
    channels_by_msgs = sorted(channels, 
                              key=lambda x: x.get('speedMessages_count', 0), 
                              reverse=True)[:5]
    
    if channels_by_msgs:
        print(f"\n    Top Channels by Speed Messages:")
        for ch in channels_by_msgs:
            print(f"      • {ch.get('name', 'Unknown')}: {ch.get('speedMessages_count', 0)} messages")

def analyze_broadcasts(broadcasts):
    """Analyze broadcast campaigns"""
    print("\n  📣 BROADCAST ANALYSIS:")
    
    status_counts = Counter()
    for bc in broadcasts:
        status = bc.get('status', 'Unknown')
        status_counts[status] += 1
    
    print(f"    Total Broadcasts: {len(broadcasts)}")
    print(f"    By Status:")
    for status, count in status_counts.most_common():
        print(f"      • {status}: {count}")

def generate_summary_report(data):
    """Generate overall summary"""
    print("\n" + "="*80)
    print("OVERALL SUMMARY REPORT")
    print("="*80)
    
    metadata = data.get('metadata', {})
    companies = data.get('companies', [])
    
    print(f"\n📈 PLATFORM TOTALS:")
    print(f"  Total Companies: {metadata.get('total_companies', 0)}")
    print(f"  Total Users: {metadata.get('total_users', 0)}")
    print(f"  Total Channels: {metadata.get('total_channels', 0)}")
    print(f"  Total Instances: {metadata.get('total_instances', 0)}")
    print(f"  Total Broadcasts: {metadata.get('total_broadcasts', 0)}")
    print(f"  Total Speed Messages: {metadata.get('total_speedMessages', 0)}")
    
    # Company comparison
    print(f"\n🏢 COMPANY COMPARISON:")
    print(f"{'Company':<20} {'Users':<8} {'Channels':<10} {'Instances':<10} {'Broadcasts':<12}")
    print("-" * 80)
    
    for company in companies:
        name = (company.get('name', 'Unknown')[:17] + '...') if len(company.get('name', '')) > 20 else company.get('name', 'Unknown')
        print(f"{name:<20} {company.get('users_count', 0):<8} {company.get('channels_count', 0):<10} {company.get('instances_count', 0):<10} {company.get('broadcasts_count', 0):<12}")
    
    # Active vs Inactive summary
    print(f"\n⚡ ACTIVITY SUMMARY:")
    active_companies = sum(1 for c in companies if c.get('isActive', False))
    print(f"  Active Companies: {active_companies}/{len(companies)}")
    
    total_active_users = 0
    total_users = 0
    for company in companies:
        for user in company.get('users', []):
            total_users += 1
            if user.get('user_status', user.get('isActive', False)):
                total_active_users += 1
    
    if total_users > 0:
        print(f"  Active Users Platform-wide: {total_active_users}/{total_users} ({total_active_users/total_users*100:.1f}%)")

def generate_recommendations(data):
    """Generate actionable recommendations"""
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    companies = data.get('companies', [])
    
    for company in companies:
        recommendations = []
        company_name = company.get('name', 'Unknown')
        
        # Check user activity
        users = company.get('users', [])
        if users:
            inactive_users = sum(1 for u in users if not u.get('user_status', u.get('isActive', False)))
            if inactive_users > len(users) * 0.3:  # More than 30% inactive
                recommendations.append(f"⚠️ High inactive user rate ({inactive_users}/{len(users)}). Consider reviewing user accounts.")
        
        # Check instance utilization
        instances = company.get('instances', [])
        if instances:
            active_instances = sum(1 for i in instances if i.get('active', False))
            if active_instances < len(instances) * 0.5:  # Less than 50% active
                recommendations.append(f"⚠️ Low instance utilization ({active_instances}/{len(instances)} active). Review inactive instances.")
        
        # Check channel usage
        channels = company.get('channels', [])
        if channels:
            empty_channels = sum(1 for ch in channels if ch.get('speedMessages_count', 0) == 0)
            if empty_channels > 0:
                recommendations.append(f"📝 {empty_channels} channels have no speed messages. Consider adding templates.")
        
        # Check broadcasts
        broadcasts = company.get('broadcasts', [])
        if len(broadcasts) == 0 and len(instances) > 0:
            recommendations.append(f"📣 No broadcasts configured. Consider creating broadcast campaigns.")
        
        if recommendations:
            print(f"\n🏢 {company_name}:")
            for rec in recommendations:
                print(f"  {rec}")

def export_csv_reports(data, output_dir):
    """Export detailed CSV reports"""
    import csv
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Users report
    with open(os.path.join(output_dir, 'users_report.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'User Name', 'Email', 'Type', 'Phone', 'Active', 'Channel'])
        
        for company in data.get('companies', []):
            company_name = company.get('name', 'Unknown')
            for user in company.get('users', []):
                writer.writerow([
                    company_name,
                    user.get('name', user.get('user_name', 'N/A')),
                    user.get('email', 'N/A'),
                    user.get('user_type_name', 'Unknown'),
                    user.get('phone', 'N/A'),
                    'Yes' if user.get('user_status', user.get('isActive', False)) else 'No',
                    user.get('assigned_channel', {}).get('name', 'N/A') if user.get('assigned_channel') else 'N/A'
                ])
    
    # Instances report
    with open(os.path.join(output_dir, 'instances_report.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'Instance Name', 'Type', 'Phone', 'Status', 'Active', 'Broadcasts'])
        
        for company in data.get('companies', []):
            company_name = company.get('name', 'Unknown')
            for instance in company.get('instances', []):
                type_details = instance.get('type_details') or {}
                writer.writerow([
                    company_name,
                    instance.get('name', instance.get('nickName', 'N/A')),
                    type_details.get('name', 'Unknown'),
                    instance.get('phone', 'N/A'),
                    instance.get('status', 'Unknown'),
                    'Yes' if instance.get('active', False) else 'No',
                    instance.get('broadcasts_count', 0)
                ])
    
    # Channels report
    with open(os.path.join(output_dir, 'channels_report.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'Channel Name', 'Speed Messages', 'Active'])
        
        for company in data.get('companies', []):
            company_name = company.get('name', 'Unknown')
            for channel in company.get('channels', []):
                writer.writerow([
                    company_name,
                    channel.get('name', 'N/A'),
                    channel.get('speedMessages_count', 0),
                    'Yes' if channel.get('isActive', False) else 'No'
                ])
    
    print(f"\n✅ CSV reports exported to: {output_dir}/")
    print(f"  • users_report.csv")
    print(f"  • instances_report.csv")
    print(f"  • channels_report.csv")

def main():
    # Get file path
    filepath = input("Enter path to merged_whatsapp_data.json: ").strip()
    
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return
    
    print("\n📊 Loading and analyzing data...")
    data = load_merged_data(filepath)
    
    # Generate reports
    generate_summary_report(data)
    analyze_companies(data)
    generate_recommendations(data)
    
    # Ask about CSV export
    export_csv = input("\n\nExport detailed CSV reports? (y/n): ").strip().lower()
    if export_csv == 'y':
        output_dir = input("Enter output directory (default: ./reports): ").strip() or './reports'
        export_csv_reports(data, output_dir)
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80)

if __name__ == "__main__":
    main()