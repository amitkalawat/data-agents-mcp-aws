import csv
import json
import random
from datetime import datetime, timedelta

random.seed(42)

def generate_user_details(num_users=10000):
    
    subscription_plans = ['Basic', 'Standard', 'Premium', 'Premium Plus']
    plan_prices = {'Basic': 8.99, 'Standard': 13.99, 'Premium': 17.99, 'Premium Plus': 22.99}
    
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Brazil', 'Mexico', 'Japan', 'Australia', 'India']
    country_weights = [0.25, 0.08, 0.10, 0.08, 0.06, 0.05, 0.04, 0.08, 0.06, 0.05, 0.03, 0.12]
    
    devices = ['Smart TV', 'Mobile', 'Tablet', 'Web Browser', 'Gaming Console', 'Streaming Device']
    device_weights = [0.30, 0.25, 0.15, 0.15, 0.08, 0.07]
    
    users = []
    
    for i in range(num_users):
        user_id = f"USR{str(i+1).zfill(8)}"
        
        age = int(random.gauss(35, 12))
        age = max(18, min(80, age))
        
        if age < 25:
            plan_probs = [0.40, 0.35, 0.20, 0.05]
        elif age < 35:
            plan_probs = [0.20, 0.30, 0.35, 0.15]
        elif age < 50:
            plan_probs = [0.15, 0.25, 0.35, 0.25]
        else:
            plan_probs = [0.25, 0.35, 0.30, 0.10]
            
        subscription_plan = random.choices(subscription_plans, weights=plan_probs)[0]
        
        signup_date = datetime.now() - timedelta(days=random.randint(1, 1825))
        
        if subscription_plan in ['Premium', 'Premium Plus']:
            churn_prob = 0.05
        elif subscription_plan == 'Standard':
            churn_prob = 0.10
        else:
            churn_prob = 0.15
            
        is_active = random.random() > churn_prob
        
        last_payment_date = datetime.now() - timedelta(days=random.randint(0, 30)) if is_active else None
        
        country = random.choices(countries, weights=country_weights)[0]
        
        primary_device = random.choices(devices, weights=device_weights)[0]
        
        num_profiles = random.randint(1, 5 if subscription_plan in ['Premium', 'Premium Plus'] else 3)
        
        lifetime_value = 0
        if is_active:
            months_active = (datetime.now() - signup_date).days // 30
            lifetime_value = months_active * plan_prices[subscription_plan]
        else:
            random_months = random.randint(1, 24)
            lifetime_value = random_months * plan_prices[subscription_plan]
        
        users.append({
            'user_id': user_id,
            'email': f"user{i+1}@example.com",
            'age': age,
            'gender': random.choices(['Male', 'Female', 'Other', 'Prefer not to say'], weights=[0.48, 0.48, 0.02, 0.02])[0],
            'country': country,
            'city': f"{country}_City_{random.randint(1, 20)}",
            'subscription_plan': subscription_plan,
            'monthly_price': plan_prices[subscription_plan],
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'is_active': is_active,
            'last_payment_date': last_payment_date.strftime('%Y-%m-%d') if last_payment_date else None,
            'primary_device': primary_device,
            'num_profiles': num_profiles,
            'payment_method': random.choices(['Credit Card', 'PayPal', 'Bank Transfer', 'Gift Card'], weights=[0.60, 0.25, 0.10, 0.05])[0],
            'lifetime_value': round(lifetime_value, 2),
            'referral_source': random.choices(['Organic', 'Social Media', 'Email', 'Partner', 'TV Ad'], weights=[0.30, 0.25, 0.20, 0.15, 0.10])[0],
            'language_preference': random.choices(['English', 'Spanish', 'French', 'German', 'Portuguese', 'Japanese'], weights=[0.40, 0.20, 0.10, 0.10, 0.10, 0.10])[0]
        })
    
    return users

def write_csv(users, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = users[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

def write_json(users, filename):
    with open(filename, 'w') as jsonfile:
        json.dump(users, jsonfile, indent=2)

if __name__ == "__main__":
    print("Generating user details dataset...")
    users = generate_user_details(10000)
    
    write_csv(users, 'user_details.csv')
    write_json(users, 'user_details.json')
    
    print(f"Generated {len(users)} user records")
    
    active_users = sum(1 for u in users if u['is_active'])
    print(f"\nActive Users: {active_users} ({active_users/len(users)*100:.1f}%)")
    
    print("\nSubscription Distribution:")
    plan_counts = {}
    for u in users:
        plan = u['subscription_plan']
        plan_counts[plan] = plan_counts.get(plan, 0) + 1
    for plan, count in sorted(plan_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {plan}: {count}")
    
    print("\nTop 5 Countries:")
    country_counts = {}
    for u in users:
        country = u['country']
        country_counts[country] = country_counts.get(country, 0) + 1
    for i, (country, count) in enumerate(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]):
        print(f"  {country}: {count}")