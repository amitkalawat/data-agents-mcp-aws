import csv
import json
import random
from datetime import datetime, timedelta

random.seed(42)

def generate_content_library():
    genres = ['Action', 'Comedy', 'Drama', 'Thriller', 'Romance', 'Documentary', 'Horror', 'Sci-Fi', 'Animation', 'Crime']
    content_types = ['Movie', 'TV Show']
    
    titles = [
        {'title': 'The Last Frontier', 'type': 'Movie', 'genres': ['Action', 'Sci-Fi'], 'release_year': 2023, 'rating': 8.5, 'runtime': 142, 'episodes': None},
        {'title': 'Comedy Central', 'type': 'TV Show', 'genres': ['Comedy'], 'release_year': 2022, 'rating': 7.8, 'runtime': None, 'episodes': 24},
        {'title': 'Dark Waters', 'type': 'Movie', 'genres': ['Thriller', 'Drama'], 'release_year': 2023, 'rating': 8.2, 'runtime': 118, 'episodes': None},
        {'title': 'Family Ties', 'type': 'TV Show', 'genres': ['Drama', 'Romance'], 'release_year': 2021, 'rating': 8.0, 'runtime': None, 'episodes': 36},
        {'title': 'The Algorithm', 'type': 'Movie', 'genres': ['Sci-Fi', 'Thriller'], 'release_year': 2024, 'rating': 7.9, 'runtime': 125, 'episodes': None},
        {'title': 'Breaking Boundaries', 'type': 'Documentary', 'genres': ['Documentary'], 'release_year': 2023, 'rating': 8.7, 'runtime': 95, 'episodes': None},
        {'title': 'Midnight Terror', 'type': 'Movie', 'genres': ['Horror'], 'release_year': 2023, 'rating': 7.2, 'runtime': 98, 'episodes': None},
        {'title': 'Detective Chronicles', 'type': 'TV Show', 'genres': ['Crime', 'Thriller'], 'release_year': 2022, 'rating': 8.4, 'runtime': None, 'episodes': 48},
        {'title': 'Space Academy', 'type': 'TV Show', 'genres': ['Sci-Fi', 'Action'], 'release_year': 2023, 'rating': 8.1, 'runtime': None, 'episodes': 30},
        {'title': 'Love in Paris', 'type': 'Movie', 'genres': ['Romance', 'Comedy'], 'release_year': 2024, 'rating': 7.5, 'runtime': 105, 'episodes': None},
        {'title': 'The Heist', 'type': 'Movie', 'genres': ['Action', 'Crime'], 'release_year': 2023, 'rating': 8.3, 'runtime': 132, 'episodes': None},
        {'title': 'Nature\'s Wonders', 'type': 'Documentary', 'genres': ['Documentary'], 'release_year': 2024, 'rating': 9.0, 'runtime': 88, 'episodes': None},
        {'title': 'Animated Adventures', 'type': 'TV Show', 'genres': ['Animation', 'Comedy'], 'release_year': 2022, 'rating': 8.2, 'runtime': None, 'episodes': 52},
        {'title': 'City Lights', 'type': 'Movie', 'genres': ['Drama', 'Romance'], 'release_year': 2023, 'rating': 7.7, 'runtime': 115, 'episodes': None},
        {'title': 'Future Wars', 'type': 'Movie', 'genres': ['Action', 'Sci-Fi'], 'release_year': 2024, 'rating': 8.0, 'runtime': 148, 'episodes': None},
        {'title': 'Comedy Night Live', 'type': 'TV Show', 'genres': ['Comedy'], 'release_year': 2023, 'rating': 7.6, 'runtime': None, 'episodes': 18},
        {'title': 'The Mansion', 'type': 'Movie', 'genres': ['Horror', 'Thriller'], 'release_year': 2023, 'rating': 7.3, 'runtime': 102, 'episodes': None},
        {'title': 'Medical Emergency', 'type': 'TV Show', 'genres': ['Drama'], 'release_year': 2022, 'rating': 8.5, 'runtime': None, 'episodes': 42},
        {'title': 'Robot Revolution', 'type': 'Movie', 'genres': ['Sci-Fi', 'Action'], 'release_year': 2024, 'rating': 7.8, 'runtime': 136, 'episodes': None},
        {'title': 'Historical Secrets', 'type': 'Documentary', 'genres': ['Documentary'], 'release_year': 2023, 'rating': 8.6, 'runtime': 92, 'episodes': None}
    ]
    
    for i, title in enumerate(titles):
        title['content_id'] = f"CNT{str(i+1).zfill(6)}"
    
    return titles

def generate_streaming_analytics(num_records=50000):
    content_library = generate_content_library()
    
    with open('../user_details/user_details.json', 'r') as f:
        users = json.load(f)
    
    user_ids = [u['user_id'] for u in users if u['is_active']]
    
    streaming_data = []
    session_id_counter = 1
    
    for _ in range(num_records):
        user_id = random.choice(user_ids)
        content = random.choice(content_library)
        
        user_data = next(u for u in users if u['user_id'] == user_id)
        device = user_data['primary_device']
        
        view_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        if content['type'] == 'Movie' or content['type'] == 'Documentary':
            runtime = content['runtime'] if content['runtime'] else 90
            watch_duration = random.gauss(runtime * 0.85, runtime * 0.15)
            watch_duration = max(10, min(runtime, watch_duration))
            completion_rate = min(100, (watch_duration / runtime) * 100)
        else:
            episode_duration = 45
            watch_duration = random.gauss(episode_duration * 0.9, episode_duration * 0.1)
            watch_duration = max(5, min(episode_duration, watch_duration))
            completion_rate = min(100, (watch_duration / episode_duration) * 100)
            
        streaming_data.append({
            'session_id': f"SES{str(session_id_counter).zfill(10)}",
            'user_id': user_id,
            'content_id': content['content_id'],
            'title': content['title'],
            'content_type': content['type'],
            'genre': content['genres'][0],
            'view_date': view_date.strftime('%Y-%m-%d'),
            'view_time': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
            'device_type': device,
            'watch_duration_minutes': round(watch_duration, 2),
            'completion_rate': round(completion_rate, 2),
            'rating_given': random.choice([None, None, None, 3, 4, 4, 5, 5, 5]) if completion_rate > 80 else None,
            'paused_count': random.randint(0, 5) if completion_rate < 90 else 0,
            'rewind_count': random.randint(0, 3),
            'country': user_data['country'],
            'bandwidth_mbps': round(random.uniform(5, 100), 2),
            'video_quality': random.choices(['4K', 'HD', 'SD'], weights=[0.25, 0.60, 0.15])[0],
            'subtitle_language': random.choices(['None', 'English', 'Spanish', 'French'], weights=[0.60, 0.25, 0.10, 0.05])[0]
        })
        
        session_id_counter += 1
    
    return streaming_data, content_library

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
    print("Generating streaming analytics dataset...")
    streaming_data, content_library = generate_streaming_analytics(50000)
    
    write_csv(streaming_data, 'streaming_analytics.csv')
    write_json(streaming_data, 'streaming_analytics.json')
    
    write_csv(content_library, 'content_library.csv')
    write_json(content_library, 'content_library.json')
    
    print(f"Generated {len(streaming_data)} streaming records")
    print(f"Generated {len(content_library)} content items")
    
    print("\nTop 5 Most Watched Titles:")
    title_counts = {}
    for record in streaming_data:
        title = record['title']
        title_counts[title] = title_counts.get(title, 0) + 1
    for title, count in sorted(title_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {title}: {count} views")
    
    print("\nAverage Completion Rate by Content Type:")
    type_rates = {}
    type_counts = {}
    for record in streaming_data:
        content_type = record['content_type']
        if content_type not in type_rates:
            type_rates[content_type] = 0
            type_counts[content_type] = 0
        type_rates[content_type] += record['completion_rate']
        type_counts[content_type] += 1
    
    for content_type in type_rates:
        avg_rate = type_rates[content_type] / type_counts[content_type]
        print(f"  {content_type}: {avg_rate:.1f}%")