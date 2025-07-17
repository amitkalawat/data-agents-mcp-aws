import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { promises as fs } from 'fs';
import { parse } from 'csv-parse/sync';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Data cache
class UserDataCache {
  constructor() {
    this.users = [];
    this.loaded = false;
  }

  async loadData() {
    if (this.loaded) return;

    try {
      // Load user details
      const csvPath = path.join(__dirname, '../../user_details/user_details.csv');
      const csvData = await fs.readFile(csvPath, 'utf8');
      
      this.users = parse(csvData, {
        columns: true,
        skip_empty_lines: true
      });

      this.loaded = true;
      console.error(`Loaded ${this.users.length} users`);
    } catch (error) {
      console.error('Failed to load user data:', error);
      throw error;
    }
  }

  getUsers(filters = {}) {
    let filteredUsers = [...this.users];

    if (filters.age_min) {
      filteredUsers = filteredUsers.filter(u => parseInt(u.age) >= filters.age_min);
    }
    if (filters.age_max) {
      filteredUsers = filteredUsers.filter(u => parseInt(u.age) <= filters.age_max);
    }
    if (filters.gender) {
      filteredUsers = filteredUsers.filter(u => u.gender === filters.gender);
    }
    if (filters.subscription_type) {
      filteredUsers = filteredUsers.filter(u => u.subscription_type === filters.subscription_type);
    }
    if (filters.location) {
      filteredUsers = filteredUsers.filter(u => 
        u.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }

    return filteredUsers;
  }

  getUserById(userId) {
    return this.users.find(u => u.user_id === userId);
  }

  getUserStats() {
    const stats = {
      total_users: this.users.length,
      by_subscription: {},
      by_gender: {},
      by_age_group: {
        '18-25': 0,
        '26-35': 0,
        '36-45': 0,
        '46-55': 0,
        '56+': 0
      },
      avg_age: 0,
      locations: new Set()
    };

    let totalAge = 0;

    this.users.forEach(user => {
      // Subscription stats
      stats.by_subscription[user.subscription_type] = 
        (stats.by_subscription[user.subscription_type] || 0) + 1;

      // Gender stats
      stats.by_gender[user.gender] = 
        (stats.by_gender[user.gender] || 0) + 1;

      // Age stats
      const age = parseInt(user.age);
      totalAge += age;
      
      if (age <= 25) stats.by_age_group['18-25']++;
      else if (age <= 35) stats.by_age_group['26-35']++;
      else if (age <= 45) stats.by_age_group['36-45']++;
      else if (age <= 55) stats.by_age_group['46-55']++;
      else stats.by_age_group['56+']++;

      // Locations
      stats.locations.add(user.location);
    });

    stats.avg_age = Math.round(totalAge / this.users.length);
    stats.unique_locations = stats.locations.size;
    delete stats.locations; // Remove Set from response

    return stats;
  }

  getSegmentation(criteria) {
    const segments = {};

    this.users.forEach(user => {
      let segmentKey = '';

      if (criteria.includes('subscription')) {
        segmentKey += user.subscription_type + '_';
      }
      if (criteria.includes('gender')) {
        segmentKey += user.gender + '_';
      }
      if (criteria.includes('age_group')) {
        const age = parseInt(user.age);
        let ageGroup;
        if (age <= 25) ageGroup = '18-25';
        else if (age <= 35) ageGroup = '26-35';
        else if (age <= 45) ageGroup = '36-45';
        else if (age <= 55) ageGroup = '46-55';
        else ageGroup = '56+';
        segmentKey += ageGroup + '_';
      }

      segmentKey = segmentKey.slice(0, -1); // Remove trailing underscore

      if (!segments[segmentKey]) {
        segments[segmentKey] = {
          count: 0,
          users: []
        };
      }

      segments[segmentKey].count++;
      segments[segmentKey].users.push({
        user_id: user.user_id,
        name: user.name,
        email: user.email
      });
    });

    return segments;
  }
}

// Initialize data cache
const dataCache = new UserDataCache();

// MCP Server setup
const server = new Server(
  {
    name: 'acme-user-details-mcp',
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
        name: 'get_users',
        description: 'Get list of users with optional filters',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Maximum number of users to return',
              default: 100
            },
            age_min: {
              type: 'number',
              description: 'Minimum age filter'
            },
            age_max: {
              type: 'number',
              description: 'Maximum age filter'
            },
            gender: {
              type: 'string',
              description: 'Filter by gender (M/F)',
              enum: ['M', 'F']
            },
            subscription_type: {
              type: 'string',
              description: 'Filter by subscription type',
              enum: ['Free', 'Basic', 'Premium']
            },
            location: {
              type: 'string',
              description: 'Filter by location (partial match)'
            }
          },
        },
      },
      {
        name: 'get_user_by_id',
        description: 'Get detailed information about a specific user',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: {
              type: 'string',
              description: 'The user ID',
            },
          },
          required: ['user_id'],
        },
      },
      {
        name: 'get_user_statistics',
        description: 'Get aggregate statistics about all users',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_user_segments',
        description: 'Get user segmentation based on criteria',
        inputSchema: {
          type: 'object',
          properties: {
            criteria: {
              type: 'array',
              description: 'Segmentation criteria',
              items: {
                type: 'string',
                enum: ['subscription', 'gender', 'age_group']
              },
              default: ['subscription']
            }
          },
        },
      },
      {
        name: 'find_similar_users',
        description: 'Find users similar to a given user',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: {
              type: 'string',
              description: 'The reference user ID',
            },
            similarity_criteria: {
              type: 'array',
              description: 'Criteria for similarity',
              items: {
                type: 'string',
                enum: ['age', 'location', 'subscription', 'gender']
              },
              default: ['age', 'subscription']
            },
            limit: {
              type: 'number',
              description: 'Maximum number of similar users to return',
              default: 10
            }
          },
          required: ['user_id'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Ensure data is loaded
  await dataCache.loadData();

  const { name, arguments: args } = request.params;

  switch (name) {
    case 'get_users': {
      const { limit = 100, ...filters } = args;
      const users = dataCache.getUsers(filters);
      const limitedUsers = users.slice(0, limit);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              total_matches: users.length,
              returned: limitedUsers.length,
              users: limitedUsers
            }, null, 2),
          },
        ],
      };
    }

    case 'get_user_by_id': {
      const { user_id } = args;
      const user = dataCache.getUserById(user_id);

      if (!user) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: 'User not found' }),
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ user }, null, 2),
          },
        ],
      };
    }

    case 'get_user_statistics': {
      const stats = dataCache.getUserStats();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ statistics: stats }, null, 2),
          },
        ],
      };
    }

    case 'get_user_segments': {
      const { criteria = ['subscription'] } = args;
      const segments = dataCache.getSegmentation(criteria);

      // Sort segments by count
      const sortedSegments = Object.entries(segments)
        .sort(([, a], [, b]) => b.count - a.count)
        .reduce((acc, [key, value]) => {
          acc[key] = {
            count: value.count,
            percentage: (value.count / dataCache.users.length * 100).toFixed(2) + '%',
            sample_users: value.users.slice(0, 5)
          };
          return acc;
        }, {});

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ 
              criteria,
              segments: sortedSegments 
            }, null, 2),
          },
        ],
      };
    }

    case 'find_similar_users': {
      const { user_id, similarity_criteria = ['age', 'subscription'], limit = 10 } = args;
      const referenceUser = dataCache.getUserById(user_id);

      if (!referenceUser) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: 'Reference user not found' }),
            },
          ],
        };
      }

      // Find similar users
      const allUsers = dataCache.getUsers();
      const similarUsers = allUsers
        .filter(u => u.user_id !== user_id)
        .map(user => {
          let score = 0;

          if (similarity_criteria.includes('age')) {
            const ageDiff = Math.abs(parseInt(user.age) - parseInt(referenceUser.age));
            score += Math.max(0, 10 - ageDiff); // Max 10 points for age
          }

          if (similarity_criteria.includes('location') && user.location === referenceUser.location) {
            score += 10;
          }

          if (similarity_criteria.includes('subscription') && user.subscription_type === referenceUser.subscription_type) {
            score += 10;
          }

          if (similarity_criteria.includes('gender') && user.gender === referenceUser.gender) {
            score += 5;
          }

          return { ...user, similarity_score: score };
        })
        .sort((a, b) => b.similarity_score - a.similarity_score)
        .slice(0, limit);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              reference_user: {
                user_id: referenceUser.user_id,
                name: referenceUser.name,
                age: referenceUser.age,
                location: referenceUser.location,
                subscription_type: referenceUser.subscription_type
              },
              similarity_criteria,
              similar_users: similarUsers
            }, null, 2),
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
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Acme User Details MCP Server running');
}

main().catch(console.error);