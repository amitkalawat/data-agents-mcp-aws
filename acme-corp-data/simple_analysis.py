import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

def load_csv(filename):
    """Load CSV file and return list of dictionaries"""
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

# Load all datasets
print("Loading datasets...")
users = load_csv('user_details/user_details.csv')
streaming = load_csv('streaming_analytics/streaming_analytics.csv')
content = load_csv('streaming_analytics/content_library.csv')
campaigns = load_csv('ad_campaign_data/campaigns.csv')
performance = load_csv('ad_campaign_data/campaign_performance.csv')
attribution = load_csv('ad_campaign_data/attribution_data.csv')

print(f"✓ Loaded {len(users)} users")
print(f"✓ Loaded {len(streaming)} streaming sessions")
print(f"✓ Loaded {len(content)} content items")
print(f"✓ Loaded {len(campaigns)} campaigns")
print(f"✓ Loaded {len(performance)} performance records")
print(f"✓ Loaded {len(attribution)} attribution records")

# 1. User Demographics Analysis
print_section("USER DEMOGRAPHICS ANALYSIS")

# Active users
active_users = sum(1 for u in users if u['is_active'] == 'True')
print(f"Active users: {active_users} ({active_users/len(users)*100:.1f}%)")

# Subscription plan distribution
plan_counts = Counter(u['subscription_plan'] for u in users)
print("\nSubscription Plan Distribution:")
for plan, count in sorted(plan_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {plan}: {count} ({count/len(users)*100:.1f}%)")

# Age statistics
ages = [int(u['age']) for u in users]
avg_age = sum(ages) / len(ages)
print(f"\nAge Statistics:")
print(f"  Average age: {avg_age:.1f}")
print(f"  Min age: {min(ages)}")
print(f"  Max age: {max(ages)}")

# Country distribution
country_counts = Counter(u['country'] for u in users)
print("\nTop 5 Countries:")
for country, count in country_counts.most_common(5):
    print(f"  {country}: {count} users")

# 2. Streaming Behavior Analysis
print_section("STREAMING BEHAVIOR ANALYSIS")

# Average completion rate
completion_rates = [float(s['completion_rate']) for s in streaming]
avg_completion = sum(completion_rates) / len(completion_rates)
print(f"Average completion rate: {avg_completion:.1f}%")

# Watch duration
watch_durations = [float(s['watch_duration_minutes']) for s in streaming]
avg_duration = sum(watch_durations) / len(watch_durations)
print(f"Average watch duration: {avg_duration:.1f} minutes")

# Content type distribution
content_type_counts = Counter(s['content_type'] for s in streaming)
print("\nContent Type Distribution:")
for content_type, count in content_type_counts.items():
    print(f"  {content_type}: {count} views")

# Most watched titles
title_counts = Counter(s['title'] for s in streaming)
print("\nTop 10 Most Watched Titles:")
for title, count in title_counts.most_common(10):
    print(f"  {title}: {count} views")

# 3. Cross-Dataset Analysis: Premium Users Watching Sci-Fi
print_section("CROSS-DATASET ANALYSIS: PREMIUM USERS & SCI-FI")

# Create user lookup
user_lookup = {u['user_id']: u for u in users}

# Find premium/premium plus users watching sci-fi
premium_scifi_sessions = []
for session in streaming:
    if session['genre'] == 'Sci-Fi' and session['user_id'] in user_lookup:
        user = user_lookup[session['user_id']]
        if user['subscription_plan'] in ['Premium', 'Premium Plus']:
            premium_scifi_sessions.append({
                'session': session,
                'user': user
            })

unique_users = set(s['user']['user_id'] for s in premium_scifi_sessions)
print(f"Premium/Premium Plus users watching Sci-Fi:")
print(f"  Total sessions: {len(premium_scifi_sessions)}")
print(f"  Unique users: {len(unique_users)}")

if premium_scifi_sessions:
    avg_completion = sum(float(s['session']['completion_rate']) for s in premium_scifi_sessions) / len(premium_scifi_sessions)
    print(f"  Average completion rate: {avg_completion:.1f}%")
    
    # Average lifetime value
    total_ltv = sum(float(user_lookup[uid]['lifetime_value']) for uid in unique_users)
    avg_ltv = total_ltv / len(unique_users)
    print(f"  Average lifetime value: ${avg_ltv:.2f}")

# 4. Campaign Performance Analysis
print_section("CAMPAIGN PERFORMANCE ANALYSIS")

# Total spend by platform
platform_spend = defaultdict(float)
for perf in performance:
    platform_spend[perf['platform']] += float(perf['spend'])

print("Total Spend by Platform:")
for platform, spend in sorted(platform_spend.items(), key=lambda x: x[1], reverse=True):
    print(f"  {platform}: ${spend:,.2f}")

# Campaign type distribution
campaign_type_counts = Counter(c['campaign_type'] for c in campaigns)
print("\nCampaign Type Distribution:")
for ctype, count in campaign_type_counts.items():
    print(f"  {ctype}: {count}")

# 5. User Attribution Analysis
print_section("USER ATTRIBUTION ANALYSIS")

# Conversion metrics
total_touchpoints = len(attribution)
conversions = sum(1 for a in attribution if a['converted'] == 'True')
conversion_rate = conversions / total_touchpoints * 100

print(f"Attribution Metrics:")
print(f"  Total touchpoints: {total_touchpoints}")
print(f"  Conversions: {conversions}")
print(f"  Conversion rate: {conversion_rate:.2f}%")

# Touchpoint types
touchpoint_counts = Counter(a['touchpoint_type'] for a in attribution)
print("\nTouchpoint Type Distribution:")
for ttype, count in touchpoint_counts.items():
    print(f"  {ttype}: {count}")

# 6. Advanced Analysis: User Value Segmentation
print_section("USER VALUE SEGMENTATION")

# Calculate metrics per user
user_metrics = defaultdict(lambda: {
    'sessions': 0,
    'total_minutes': 0,
    'campaigns_touched': set(),
    'converted': False,
    'ratings_given': 0
})

# Aggregate streaming data
for session in streaming:
    user_id = session['user_id']
    user_metrics[user_id]['sessions'] += 1
    user_metrics[user_id]['total_minutes'] += float(session['watch_duration_minutes'])
    if session['rating_given'] and session['rating_given'] != '':
        user_metrics[user_id]['ratings_given'] += 1

# Aggregate attribution data
for attr in attribution:
    user_id = attr['user_id']
    user_metrics[user_id]['campaigns_touched'].add(attr['campaign_id'])
    if attr['converted'] == 'True':
        user_metrics[user_id]['converted'] = True

# Find top engaged users
engaged_users = []
for user_id, metrics in user_metrics.items():
    if user_id in user_lookup:
        user = user_lookup[user_id]
        engagement_score = (
            metrics['sessions'] * 10 +
            metrics['total_minutes'] * 0.1 +
            metrics['ratings_given'] * 20 +
            len(metrics['campaigns_touched']) * 5
        )
        engaged_users.append({
            'user_id': user_id,
            'subscription_plan': user['subscription_plan'],
            'lifetime_value': float(user['lifetime_value']),
            'sessions': metrics['sessions'],
            'total_minutes': metrics['total_minutes'],
            'converted': metrics['converted'],
            'engagement_score': engagement_score
        })

# Sort by engagement score
engaged_users.sort(key=lambda x: x['engagement_score'], reverse=True)

print("Top 10 Most Engaged Users:")
print(f"{'User ID':<12} {'Plan':<15} {'LTV':<10} {'Sessions':<10} {'Minutes':<10} {'Score':<10}")
print("-" * 77)
for user in engaged_users[:10]:
    print(f"{user['user_id']:<12} {user['subscription_plan']:<15} ${user['lifetime_value']:<9.2f} "
          f"{user['sessions']:<10} {user['total_minutes']:<10.0f} {user['engagement_score']:<10.1f}")

# Summary statistics
print_section("SUMMARY STATISTICS")

total_revenue = sum(float(u['lifetime_value']) for u in users)
avg_revenue = total_revenue / len(users)
total_spend = sum(float(p['spend']) for p in performance)

print(f"Revenue Metrics:")
print(f"  Total user lifetime value: ${total_revenue:,.2f}")
print(f"  Average user lifetime value: ${avg_revenue:.2f}")
print(f"  Total ad spend: ${total_spend:,.2f}")
print(f"  ROI: {((total_revenue - total_spend) / total_spend * 100):.1f}%")

print("\nEngagement Metrics:")
print(f"  Total streaming sessions: {len(streaming):,}")
print(f"  Average sessions per user: {len(streaming) / len(users):.1f}")
print(f"  Total watch time: {sum(watch_durations):,.0f} minutes")
print(f"  Average watch time per user: {sum(watch_durations) / len(users):.1f} minutes")

print("\n✓ Analysis complete!")