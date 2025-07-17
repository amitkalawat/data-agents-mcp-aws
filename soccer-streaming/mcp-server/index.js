import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { Kafka } from 'kafkajs';
import dotenv from 'dotenv';
import { EventEmitter } from 'events';

dotenv.config();

// Event cache and aggregator
class SoccerDataCache extends EventEmitter {
  constructor() {
    super();
    this.matches = new Map(); // matchId -> match data
    this.recentEvents = []; // Last 100 events
    this.userStats = new Map(); // userId -> interaction stats
    this.maxEvents = 100;
  }

  addMatchEvent(event) {
    const matchId = event.match_id;
    if (!this.matches.has(matchId)) {
      this.matches.set(matchId, {
        id: matchId,
        events: [],
        userInteractions: [],
        stats: {
          goals: { home: 0, away: 0 },
          cards: { yellow: 0, red: 0 },
          activeUsers: new Set()
        }
      });
    }

    const match = this.matches.get(matchId);
    match.events.push(event);
    
    // Update stats based on event type
    if (event.event_type === 'goal') {
      if (event.team_id === match.homeTeam) {
        match.stats.goals.home++;
      } else {
        match.stats.goals.away++;
      }
    } else if (event.event_type === 'yellow_card') {
      match.stats.cards.yellow++;
    } else if (event.event_type === 'red_card') {
      match.stats.cards.red++;
    }

    // Keep recent events
    this.recentEvents.unshift(event);
    if (this.recentEvents.length > this.maxEvents) {
      this.recentEvents.pop();
    }

    this.emit('matchEvent', event);
  }

  addUserInteraction(interaction) {
    const matchId = interaction.match_id;
    const userId = interaction.user_id;

    // Update match data
    if (this.matches.has(matchId)) {
      const match = this.matches.get(matchId);
      match.userInteractions.push(interaction);
      match.stats.activeUsers.add(userId);
    }

    // Update user stats
    if (!this.userStats.has(userId)) {
      this.userStats.set(userId, {
        totalInteractions: 0,
        actionTypes: {}
      });
    }

    const userStat = this.userStats.get(userId);
    userStat.totalInteractions++;
    userStat.actionTypes[interaction.action_type] = 
      (userStat.actionTypes[interaction.action_type] || 0) + 1;

    this.emit('userInteraction', interaction);
  }

  getMatchSummary(matchId) {
    const match = this.matches.get(matchId);
    if (!match) return null;

    return {
      matchId,
      totalEvents: match.events.length,
      goals: match.stats.goals,
      cards: match.stats.cards,
      activeUsers: match.stats.activeUsers.size,
      lastEvent: match.events[match.events.length - 1] || null
    };
  }

  getRecentEvents(limit = 10) {
    return this.recentEvents.slice(0, limit);
  }

  getUserEngagement() {
    const totalUsers = this.userStats.size;
    const totalInteractions = Array.from(this.userStats.values())
      .reduce((sum, stat) => sum + stat.totalInteractions, 0);
    
    const actionBreakdown = {};
    for (const stat of this.userStats.values()) {
      for (const [action, count] of Object.entries(stat.actionTypes)) {
        actionBreakdown[action] = (actionBreakdown[action] || 0) + count;
      }
    }

    return {
      totalUsers,
      totalInteractions,
      avgInteractionsPerUser: totalUsers > 0 ? totalInteractions / totalUsers : 0,
      actionBreakdown
    };
  }
}

// Initialize cache
const dataCache = new SoccerDataCache();

// Kafka consumer setup
async function setupKafkaConsumer() {
  const kafka = new Kafka({
    clientId: 'soccer-mcp-server',
    brokers: [process.env.MSK_BOOTSTRAP_SERVERS || 'localhost:9092'],
    ssl: process.env.MSK_SECURITY_PROTOCOL === 'SSL' ? {
      rejectUnauthorized: false
    } : false
  });

  const consumer = kafka.consumer({ groupId: 'mcp-server-group' });

  try {
    await consumer.connect();
    await consumer.subscribe({ 
      topics: [
        'soccer-match-events',
        'soccer-user-interactions',
        'soccer-match-stream'
      ], 
      fromBeginning: false 
    });

    await consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        try {
          const data = JSON.parse(message.value.toString());
          
          if (data.match_event) {
            dataCache.addMatchEvent(data.match_event);
          }
          
          if (data.user_interaction) {
            dataCache.addUserInteraction(data.user_interaction);
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      },
    });

    console.error('Kafka consumer connected and running');
  } catch (error) {
    console.error('Failed to setup Kafka consumer:', error);
    // Continue without real-time data
  }
}

// MCP Server setup
const server = new Server(
  {
    name: 'soccer-streaming-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_live_matches',
        description: 'Get list of currently live soccer matches with basic stats',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_match_details',
        description: 'Get detailed information about a specific match including events and stats',
        inputSchema: {
          type: 'object',
          properties: {
            match_id: {
              type: 'string',
              description: 'The ID of the match',
            },
          },
          required: ['match_id'],
        },
      },
      {
        name: 'get_recent_events',
        description: 'Get recent match events across all matches',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Maximum number of events to return (default: 10)',
              default: 10,
            },
            event_type: {
              type: 'string',
              description: 'Filter by event type (e.g., goal, card, substitution)',
            },
          },
        },
      },
      {
        name: 'get_user_engagement',
        description: 'Get user engagement statistics and interaction patterns',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'subscribe_to_match',
        description: 'Subscribe to real-time updates for a specific match',
        inputSchema: {
          type: 'object',
          properties: {
            match_id: {
              type: 'string',
              description: 'The ID of the match to subscribe to',
            },
          },
          required: ['match_id'],
        },
      },
      {
        name: 'predict_match_outcome',
        description: 'Get AI predictions for match outcome based on current data',
        inputSchema: {
          type: 'object',
          properties: {
            match_id: {
              type: 'string',
              description: 'The ID of the match',
            },
          },
          required: ['match_id'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'get_live_matches': {
      const matches = Array.from(dataCache.matches.values()).map(match => ({
        matchId: match.id,
        status: match.events.some(e => e.event_type === 'match_end') ? 'finished' : 'live',
        currentMinute: match.events.length > 0 ? 
          match.events[match.events.length - 1].minute : 0,
        score: match.stats.goals,
        activeUsers: match.stats.activeUsers.size
      }));

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ matches }, null, 2),
          },
        ],
      };
    }

    case 'get_match_details': {
      const { match_id } = args;
      const match = dataCache.matches.get(match_id);
      
      if (!match) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: 'Match not found' }),
            },
          ],
        };
      }

      const summary = dataCache.getMatchSummary(match_id);
      const recentEvents = match.events.slice(-10).reverse();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              summary,
              recentEvents,
              totalInteractions: match.userInteractions.length
            }, null, 2),
          },
        ],
      };
    }

    case 'get_recent_events': {
      const { limit = 10, event_type } = args;
      let events = dataCache.getRecentEvents(limit);
      
      if (event_type) {
        events = events.filter(e => e.event_type === event_type);
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ events }, null, 2),
          },
        ],
      };
    }

    case 'get_user_engagement': {
      const engagement = dataCache.getUserEngagement();
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ engagement }, null, 2),
          },
        ],
      };
    }

    case 'subscribe_to_match': {
      const { match_id } = args;
      
      // Create a subscription that will send updates
      const updates = [];
      const eventHandler = (event) => {
        if (event.match_id === match_id) {
          updates.push({
            timestamp: new Date().toISOString(),
            event
          });
        }
      };

      dataCache.on('matchEvent', eventHandler);
      
      // Return subscription info
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              subscribed: true,
              match_id,
              message: 'Subscribed to match updates. Events will be collected.',
            }, null, 2),
          },
        ],
      };
    }

    case 'predict_match_outcome': {
      const { match_id } = args;
      const match = dataCache.matches.get(match_id);
      
      if (!match) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: 'Match not found' }),
            },
          ],
        };
      }

      // Simple prediction based on current stats
      const { goals, cards } = match.stats;
      const homeAdvantage = goals.home - goals.away;
      const momentum = match.events.slice(-5)
        .filter(e => e.event_type === 'goal')
        .reduce((acc, e) => {
          return e.team_id === 'home' ? acc + 1 : acc - 1;
        }, 0);

      let prediction = {
        matchId: match_id,
        currentScore: goals,
        predictedWinner: homeAdvantage > 0 ? 'home' : homeAdvantage < 0 ? 'away' : 'draw',
        confidence: Math.min(0.5 + Math.abs(homeAdvantage) * 0.15, 0.9),
        factors: {
          scoreDifference: homeAdvantage,
          recentMomentum: momentum,
          disciplineIssues: cards
        }
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ prediction }, null, 2),
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start the server
async function main() {
  // Setup Kafka consumer
  setupKafkaConsumer().catch(console.error);

  // Start MCP server
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Soccer Streaming MCP Server running');
}

main().catch(console.error);