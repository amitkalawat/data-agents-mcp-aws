# Example MCP Server Queries for AI Agents

Here are example queries an AI agent can make using the soccer streaming MCP server:

## 1. Match Overview Queries

### Get all live matches
```
"Show me all currently live soccer matches"
```
The agent will use: `get_live_matches()`

### Get specific match details
```
"What's happening in match_001?"
"Give me details about the Arsenal vs Chelsea match"
```
The agent will use: `get_match_details(match_id="match_001")`

## 2. Event Analysis

### Recent goals
```
"Show me the last 5 goals scored across all matches"
```
The agent will use: `get_recent_events(limit=5, event_type="goal")`

### Card analysis
```
"Which matches have had red cards today?"
```
The agent will use: `get_recent_events(event_type="red_card")`

## 3. User Engagement

### Overall engagement
```
"How engaged are users with today's matches?"
"What's the user activity breakdown?"
```
The agent will use: `get_user_engagement()`

### Popular actions
```
"What are users doing most during matches?"
```
The agent will analyze the actionBreakdown from `get_user_engagement()`

## 4. Predictions and Analysis

### Match predictions
```
"Who's likely to win the Arsenal match?"
"Predict the outcome of match_001"
```
The agent will use: `predict_match_outcome(match_id="match_001")`

### Combined analysis
```
"Give me a full report on the Manchester United match including score, recent events, and prediction"
```
The agent will combine:
- `get_match_details(match_id="match_002")`
- `predict_match_outcome(match_id="match_002")`

## 5. Real-time Monitoring

### Event subscriptions
```
"Alert me about any goals in the Liverpool match"
"Monitor match_003 for major events"
```
The agent will use: `subscribe_to_match(match_id="match_003")`

## 6. Complex Queries

### Multi-match analysis
```
"Which match has the most user engagement right now?"
```
The agent will:
1. Call `get_live_matches()` to get all matches
2. Call `get_match_details()` for each match
3. Compare activeUsers counts

### Trend analysis
```
"Are there more goals in the second half of matches?"
```
The agent will:
1. Use `get_recent_events(limit=100)`
2. Analyze the minute field of goal events
3. Calculate first vs second half distribution

### User behavior patterns
```
"When do users interact most during matches?"
```
The agent will:
1. Get match events with `get_recent_events()`
2. Get user engagement with `get_user_engagement()`
3. Correlate interaction spikes with match events

## Example Conversation Flow

**User**: "What's the most exciting match happening right now?"

**AI Agent** would:
1. Call `get_live_matches()` to see all active matches
2. For each match, call `get_match_details()` to get event counts
3. Identify the match with most goals/events
4. Call `get_user_engagement()` to confirm which has highest activity
5. Provide a summary with the most exciting match

**User**: "Keep me updated on that match"

**AI Agent** would:
1. Call `subscribe_to_match(match_id="...")` for the identified match
2. Monitor for significant events
3. Report major happenings as they occur