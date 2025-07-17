import csv
import json
import random
from datetime import datetime, timedelta

random.seed(42)

def generate_ad_campaigns(num_campaigns=100, num_performance_records=10000):
    
    campaign_types = ['Display', 'Video', 'Search', 'Social Media', 'Email', 'Native']
    objectives = ['Brand Awareness', 'User Acquisition', 'Retention', 'Re-engagement', 'Upsell']
    platforms = ['Google Ads', 'Facebook', 'Instagram', 'YouTube', 'TikTok', 'Twitter', 'LinkedIn', 'Programmatic']
    
    with open('../user_details/user_details.json', 'r') as f:
        users = json.load(f)
    
    with open('../streaming_analytics/content_library.json', 'r') as f:
        content_library = json.load(f)
    
    campaigns = []
    campaign_id_counter = 1
    
    for i in range(num_campaigns):
        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
        duration = random.randint(7, 90)
        end_date = start_date + timedelta(days=duration)
        
        campaign_type = random.choice(campaign_types)
        objective = random.choice(objectives)
        
        if objective == 'Brand Awareness':
            budget = random.uniform(50000, 200000)
        elif objective == 'User Acquisition':
            budget = random.uniform(100000, 500000)
        else:
            budget = random.uniform(20000, 100000)
            
        promoted_content = random.choice(content_library + [None, None, None])
        
        campaigns.append({
            'campaign_id': f"CMP{str(campaign_id_counter).zfill(6)}",
            'campaign_name': f"{objective} - {campaign_type} Campaign {i+1}",
            'campaign_type': campaign_type,
            'objective': objective,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'budget': round(budget, 2),
            'target_audience': random.choice(['18-24', '25-34', '35-44', '45-54', '55+', 'All Ages']),
            'target_countries': random.choice(['USA', 'USA,Canada', 'Global', 'Europe', 'LATAM']),
            'promoted_content_id': promoted_content['content_id'] if promoted_content else None,
            'promoted_content_title': promoted_content['title'] if promoted_content else None
        })
        
        campaign_id_counter += 1
    
    performance_data = []
    performance_id_counter = 1
    
    for _ in range(num_performance_records):
        campaign = random.choice(campaigns)
        
        date = datetime.strptime(campaign['start_date'], '%Y-%m-%d') + timedelta(days=random.randint(0, 30))
        
        platform = random.choice(platforms)
        
        if campaign['campaign_type'] == 'Video':
            impressions = random.randint(10000, 1000000)
            clicks = int(impressions * random.uniform(0.01, 0.05))
            views = int(impressions * random.uniform(0.3, 0.8))
        else:
            impressions = random.randint(5000, 500000)
            clicks = int(impressions * random.uniform(0.005, 0.03))
            views = 0
            
        cost_per_click = random.uniform(0.5, 5.0)
        spend = round(clicks * cost_per_click, 2)
        
        conversions = int(clicks * random.uniform(0.01, 0.1))
        
        if campaign['objective'] == 'User Acquisition':
            signups = conversions
            subscriptions = int(signups * random.uniform(0.3, 0.7))
        else:
            signups = int(conversions * random.uniform(0.1, 0.3))
            subscriptions = int(signups * random.uniform(0.5, 0.9))
            
        performance_data.append({
            'performance_id': f"PERF{str(performance_id_counter).zfill(10)}",
            'campaign_id': campaign['campaign_id'],
            'date': date.strftime('%Y-%m-%d'),
            'platform': platform,
            'impressions': impressions,
            'clicks': clicks,
            'click_through_rate': round((clicks / impressions) * 100, 2),
            'views': views,
            'view_rate': round((views / impressions) * 100, 2) if views > 0 else 0,
            'spend': spend,
            'cost_per_click': round(cost_per_click, 2),
            'cost_per_thousand_impressions': round((spend / impressions) * 1000, 2),
            'conversions': conversions,
            'conversion_rate': round((conversions / clicks) * 100, 2) if clicks > 0 else 0,
            'signups': signups,
            'subscriptions': subscriptions,
            'revenue_generated': round(subscriptions * random.uniform(8.99, 22.99), 2)
        })
        
        performance_id_counter += 1
    
    attribution_data = []
    attribution_id_counter = 1
    
    active_users = [u for u in users if u['is_active']]
    for _ in range(5000):
        user = random.choice(active_users)
        campaign = random.choice(campaigns)
        
        touchpoint_date = datetime.strptime(campaign['start_date'], '%Y-%m-%d') + timedelta(days=random.randint(0, 30))
        
        attribution_data.append({
            'attribution_id': f"ATTR{str(attribution_id_counter).zfill(8)}",
            'user_id': user['user_id'],
            'campaign_id': campaign['campaign_id'],
            'touchpoint_date': touchpoint_date.strftime('%Y-%m-%d'),
            'touchpoint_type': random.choice(['Impression', 'Click', 'View']),
            'platform': random.choice(platforms),
            'device': user['primary_device'],
            'attribution_model': random.choice(['Last Touch', 'First Touch', 'Linear', 'Time Decay']),
            'attribution_weight': round(random.uniform(0.1, 1.0), 2),
            'converted': random.choices([True, False], weights=[0.15, 0.85])[0],
            'conversion_value': round(random.uniform(8.99, 22.99), 2) if random.random() < 0.15 else 0
        })
        
        attribution_id_counter += 1
    
    return campaigns, performance_data, attribution_data

def write_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def write_json(data, filename):
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)

if __name__ == "__main__":
    print("Generating ad campaign datasets...")
    campaigns, performance_data, attribution_data = generate_ad_campaigns(100, 10000)
    
    write_csv(campaigns, 'campaigns.csv')
    write_json(campaigns, 'campaigns.json')
    
    write_csv(performance_data, 'campaign_performance.csv')
    write_json(performance_data, 'campaign_performance.json')
    
    write_csv(attribution_data, 'attribution_data.csv')
    write_json(attribution_data, 'attribution_data.json')
    
    print(f"Generated {len(campaigns)} campaigns")
    print(f"Generated {len(performance_data)} performance records")
    print(f"Generated {len(attribution_data)} attribution records")
    
    print("\nCampaign Type Distribution:")
    type_counts = {}
    for campaign in campaigns:
        campaign_type = campaign['campaign_type']
        type_counts[campaign_type] = type_counts.get(campaign_type, 0) + 1
    for campaign_type, count in sorted(type_counts.items()):
        print(f"  {campaign_type}: {count}")
    
    print("\nTotal Spend by Platform:")
    platform_spend = {}
    for record in performance_data:
        platform = record['platform']
        platform_spend[platform] = platform_spend.get(platform, 0) + record['spend']
    for platform, spend in sorted(platform_spend.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {platform}: ${spend:,.2f}")