# Acme Corp Synthetic Datasets

This repository contains synthetic datasets for Acme Corp, a media streaming company similar to Netflix. The datasets are designed for AI-driven analytics and natural language querying.

## Dataset Overview

### 1. User Details Dataset
**Location**: `user_details/`
- **user_details.csv/json**: 10,000 subscriber records

**Schema**:
- `user_id`: Unique identifier (format: USR00000001)
- `email`: User email address
- `age`: User age (18-80)
- `gender`: Male/Female/Other/Prefer not to say
- `country`: User's country
- `city`: User's city
- `subscription_plan`: Basic/Standard/Premium/Premium Plus
- `monthly_price`: Monthly subscription price
- `signup_date`: Date of account creation
- `is_active`: Whether subscription is currently active
- `last_payment_date`: Most recent payment date (null if inactive)
- `primary_device`: Main viewing device
- `num_profiles`: Number of profiles on account
- `payment_method`: Credit Card/PayPal/Bank Transfer/Gift Card
- `lifetime_value`: Total revenue from user
- `referral_source`: How user discovered the service
- `language_preference`: User's preferred language

### 2. Streaming Analytics Dataset
**Location**: `streaming_analytics/`
- **streaming_analytics.csv/json**: 50,000 viewing session records
- **content_library.csv/json**: 20 content items (movies/TV shows)

**Streaming Analytics Schema**:
- `session_id`: Unique session identifier (format: SES0000000001)
- `user_id`: Links to user_details.user_id
- `content_id`: Links to content_library.content_id
- `title`: Content title
- `content_type`: Movie/TV Show/Documentary
- `genre`: Primary genre
- `view_date`: Date of viewing
- `view_time`: Time of viewing
- `device_type`: Device used for viewing
- `watch_duration_minutes`: Minutes watched
- `completion_rate`: Percentage of content watched
- `rating_given`: User rating (1-5, null if not rated)
- `paused_count`: Number of times paused
- `rewind_count`: Number of times rewound
- `country`: Viewing country
- `bandwidth_mbps`: Connection speed
- `video_quality`: 4K/HD/SD
- `subtitle_language`: Subtitle preference

**Content Library Schema**:
- `content_id`: Unique content identifier (format: CNT000001)
- `title`: Content title
- `type`: Movie/TV Show/Documentary
- `genres`: List of genres
- `release_year`: Year of release
- `rating`: Average user rating
- `runtime`: Runtime in minutes (movies)
- `episodes`: Number of episodes (TV shows)

### 3. Ad Campaign Data
**Location**: `ad_campaign_data/`
- **campaigns.csv/json**: 100 ad campaigns
- **campaign_performance.csv/json**: 10,000 daily performance records
- **attribution_data.csv/json**: 5,000 user attribution records

**Campaigns Schema**:
- `campaign_id`: Unique campaign identifier (format: CMP000001)
- `campaign_name`: Descriptive campaign name
- `campaign_type`: Display/Video/Search/Social Media/Email/Native
- `objective`: Brand Awareness/User Acquisition/Retention/Re-engagement/Upsell
- `start_date`: Campaign start date
- `end_date`: Campaign end date
- `budget`: Total campaign budget
- `target_audience`: Age group targeting
- `target_countries`: Geographic targeting
- `promoted_content_id`: Links to content_library.content_id (if applicable)
- `promoted_content_title`: Title of promoted content

**Campaign Performance Schema**:
- `performance_id`: Unique record identifier (format: PERF0000000001)
- `campaign_id`: Links to campaigns.campaign_id
- `date`: Performance date
- `platform`: Advertising platform
- `impressions`: Number of ad impressions
- `clicks`: Number of clicks
- `click_through_rate`: CTR percentage
- `views`: Video views (for video campaigns)
- `view_rate`: View rate percentage
- `spend`: Daily spend amount
- `cost_per_click`: Average CPC
- `cost_per_thousand_impressions`: CPM
- `conversions`: Number of conversions
- `conversion_rate`: Conversion rate percentage
- `signups`: New user signups
- `subscriptions`: New subscriptions
- `revenue_generated`: Revenue from conversions

**Attribution Data Schema**:
- `attribution_id`: Unique attribution identifier (format: ATTR00000001)
- `user_id`: Links to user_details.user_id
- `campaign_id`: Links to campaigns.campaign_id
- `touchpoint_date`: Date of ad interaction
- `touchpoint_type`: Impression/Click/View
- `platform`: Ad platform
- `device`: User's device
- `attribution_model`: Last Touch/First Touch/Linear/Time Decay
- `attribution_weight`: Weight in attribution model
- `converted`: Whether user converted
- `conversion_value`: Value of conversion

## Relationships Between Datasets

1. **User → Streaming**: `user_details.user_id` → `streaming_analytics.user_id`
2. **User → Attribution**: `user_details.user_id` → `attribution_data.user_id`
3. **Content → Streaming**: `content_library.content_id` → `streaming_analytics.content_id`
4. **Content → Campaigns**: `content_library.content_id` → `campaigns.promoted_content_id`
5. **Campaign → Performance**: `campaigns.campaign_id` → `campaign_performance.campaign_id`
6. **Campaign → Attribution**: `campaigns.campaign_id` → `attribution_data.campaign_id`

## Example Queries

These datasets support complex cross-dataset queries such as:

1. "What is the average lifetime value of Premium subscribers who watched sci-fi content?"
2. "Which ad campaigns drove the most conversions for users aged 25-34?"
3. "What is the correlation between viewing completion rates and subscription plan?"
4. "Which content titles are most popular among users acquired through social media campaigns?"
5. "What is the ROI of video campaigns promoting specific content?"

## Data Generation

All datasets were generated using Python scripts with seeded random data to ensure consistency and realistic relationships between entities.