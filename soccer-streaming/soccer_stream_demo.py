import time
import random
import threading
from datetime import datetime
from typing import List

from soccer_match_schema import MatchEvent, UserInteraction, EventType, UserActionType
from soccer_stream_producer import SoccerStreamProducer
from soccer_stream_consumer import AnalyticsConsumer


class SoccerMatchSimulator:
    """Simulates a soccer match with events and user interactions"""
    
    def __init__(self, match_id: str, team1: str, team2: str):
        self.match_id = match_id
        self.team1 = team1
        self.team2 = team2
        self.current_minute = 0
        self.is_running = False
        self.users = [f"user_{i}" for i in range(100)]  # Simulate 100 users
        
    def generate_match_event(self) -> MatchEvent:
        """Generate random match event"""
        # Weighted probability for different events
        event_weights = {
            EventType.GOAL: 0.02,
            EventType.YELLOW_CARD: 0.03,
            EventType.RED_CARD: 0.005,
            EventType.CORNER: 0.08,
            EventType.FOUL: 0.1,
            EventType.OFFSIDE: 0.05,
            EventType.SUBSTITUTION: 0.02,
            EventType.PENALTY: 0.01,
            EventType.VAR_REVIEW: 0.01
        }
        
        # Check if any event occurs this minute
        if random.random() < 0.3:  # 30% chance of event
            event_type = random.choices(
                list(event_weights.keys()), 
                weights=list(event_weights.values())
            )[0]
            
            team_id = random.choice([self.team1, self.team2])
            
            return MatchEvent(
                match_id=self.match_id,
                event_id=f"evt_{self.current_minute}_{random.randint(1000, 9999)}",
                event_type=event_type,
                timestamp=datetime.utcnow(),
                minute=self.current_minute,
                team_id=team_id,
                player_id=f"player_{random.randint(1, 11)}",
                metadata={
                    "stadium": "Emirates Stadium",
                    "attendance": 60000
                }
            )
        return None
    
    def generate_user_interactions(self, match_event: MatchEvent = None) -> List[UserInteraction]:
        """Generate user interactions, more if there's a match event"""
        interactions = []
        
        # More interactions when something happens
        num_interactions = random.randint(5, 20) if match_event else random.randint(0, 5)
        
        for _ in range(num_interactions):
            user_id = random.choice(self.users)
            
            # Different actions based on event
            if match_event and match_event.event_type == EventType.GOAL:
                action_type = random.choice([
                    UserActionType.REACTION,
                    UserActionType.SHARE,
                    UserActionType.COMMENT
                ])
            else:
                action_type = random.choice(list(UserActionType))
            
            interaction = UserInteraction(
                user_id=user_id,
                match_id=self.match_id,
                interaction_id=f"int_{datetime.utcnow().timestamp()}_{random.randint(1000, 9999)}",
                action_type=action_type,
                timestamp=datetime.utcnow(),
                session_id=f"session_{user_id}_{self.match_id}",
                device_type=random.choice(["mobile", "web", "tv_app"]),
                location={"lat": 51.5074, "lon": -0.1278} if random.random() > 0.5 else None,
                metadata={
                    "platform": random.choice(["iOS", "Android", "Web"]),
                    "app_version": "2.3.1"
                }
            )
            interactions.append(interaction)
        
        return interactions


def run_producer_demo(simulator: SoccerMatchSimulator, producer: SoccerStreamProducer, duration: int = 10):
    """Run producer simulation for specified duration"""
    print(f"\n🎮 Starting match simulation: {simulator.team1} vs {simulator.team2}")
    print(f"⏱️  Duration: {duration} seconds (simulating 90 minutes)\n")
    
    simulator.is_running = True
    start_time = time.time()
    
    # Send match start event
    start_event = MatchEvent(
        match_id=simulator.match_id,
        event_id="evt_start",
        event_type=EventType.MATCH_START,
        timestamp=datetime.utcnow(),
        minute=0,
        metadata={"teams": [simulator.team1, simulator.team2]}
    )
    producer.send_match_event(start_event)
    
    while simulator.is_running and (time.time() - start_time) < duration:
        # Simulate match progression (90 minutes in 'duration' seconds)
        simulator.current_minute = int((time.time() - start_time) / duration * 90)
        
        # Generate match event
        match_event = simulator.generate_match_event()
        if match_event:
            producer.send_match_event(match_event)
            print(f"⚽ {match_event.event_type.value} at minute {match_event.minute} - {match_event.team_id}")
        
        # Generate user interactions
        interactions = simulator.generate_user_interactions(match_event)
        for interaction in interactions:
            producer.send_user_interaction(interaction)
        
        if interactions:
            print(f"👥 {len(interactions)} user interactions")
        
        time.sleep(0.5)  # Simulate real-time streaming
    
    # Send match end event
    end_event = MatchEvent(
        match_id=simulator.match_id,
        event_id="evt_end",
        event_type=EventType.MATCH_END,
        timestamp=datetime.utcnow(),
        minute=90,
        metadata={"final_score": {"team1": 2, "team2": 1}}
    )
    producer.send_match_event(end_event)
    producer.flush()
    
    print("\n✅ Match simulation completed!")


def run_consumer_demo(consumer: AnalyticsConsumer, duration: int = 15):
    """Run consumer for specified duration"""
    print("\n📊 Starting consumer analytics...\n")
    
    # Custom handlers
    def handle_goal(event):
        print(f"🎯 GOAL! Team: {event.get('team_id')} at minute {event.get('minute')}")
    
    def handle_user_action(interaction):
        action = interaction.get('action_type')
        if action in ['reaction', 'comment', 'share']:
            print(f"💬 User {interaction.get('user_id')} - {action}")
    
    # Set custom handlers for specific events
    consumer.set_match_event_handler(lambda event: 
        handle_goal(event) if event.get('event_type') == 'goal' 
        else consumer._default_match_event_handler(event)
    )
    consumer.set_user_interaction_handler(handle_user_action)
    
    # Subscribe and consume
    consumer.subscribe()
    
    # Run consumer in thread
    consumer_thread = threading.Thread(
        target=consumer.consume,
        kwargs={'max_messages': 100}
    )
    consumer_thread.start()
    
    # Let it run for duration
    time.sleep(duration)
    
    # Print analytics
    print("\n📈 Analytics Summary:")
    summary = consumer.get_analytics_summary()
    print(f"  Active Users: {summary['active_users_count']}")
    print(f"  Match Events: {summary['events_by_type']}")
    print(f"  User Actions: {summary['user_actions_by_type']}")
    print(f"  Total Events: {summary['timeline_events_count']}")


def main():
    """Main demo function"""
    print("⚽ Soccer Match Streaming Demo with AWS MSK")
    print("=" * 50)
    
    # Note: This demo will fail without actual MSK connection
    # Set MSK_BOOTSTRAP_SERVERS environment variable or update config
    
    try:
        # Initialize components
        simulator = SoccerMatchSimulator(
            match_id="match_2024_001",
            team1="Arsenal",
            team2="Chelsea"
        )
        
        producer = SoccerStreamProducer()
        consumer = AnalyticsConsumer()
        
        # Run producer in separate thread
        producer_thread = threading.Thread(
            target=run_producer_demo,
            args=(simulator, producer, 10)
        )
        producer_thread.start()
        
        # Give producer time to start
        time.sleep(2)
        
        # Run consumer
        run_consumer_demo(consumer, 12)
        
        # Wait for producer to finish
        producer_thread.join()
        
        # Cleanup
        producer.close()
        consumer.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Note: This demo requires AWS MSK connection.")
        print("   Set MSK_BOOTSTRAP_SERVERS environment variable or update msk_config.py")


if __name__ == "__main__":
    main()