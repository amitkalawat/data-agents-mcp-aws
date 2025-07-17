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

// Data cache for streaming analytics
class StreamingDataCache {
  constructor() {
    this.analytics = [];
    this.content = [];
    this.loaded = false;
  }

  async loadData() {
    if (this.loaded) return;

    try {
      // Load streaming analytics
      const analyticsPath = path.join(__dirname, '../../streaming_analytics/streaming_analytics.csv');
      const analyticsData = await fs.readFile(analyticsPath, 'utf8');
      
      this.analytics = parse(analyticsData, {
        columns: true,
        skip_empty_lines: true
      });

      // Load content library
      const contentPath = path.join(__dirname, '../../streaming_analytics/content_library.csv');
      const contentData = await fs.readFile(contentPath, 'utf8');
      
      this.content = parse(contentData, {
        columns: true,
        skip_empty_lines: true
      });

      this.loaded = true;
      console.error(`Loaded ${this.analytics.length} analytics records and ${this.content.length} content items`);
    } catch (error) {
      console.error('Failed to load streaming data:', error);
      throw error;
    }
  }

  getViewingHistory(filters = {}) {
    let filtered = [...this.analytics];

    if (filters.user_id) {
      filtered = filtered.filter(a => a.user_id === filters.user_id);
    }
    if (filters.content_id) {
      filtered = filtered.filter(a => a.content_id === filters.content_id);
    }
    if (filters.date_from) {
      filtered = filtered.filter(a => new Date(a.timestamp) >= new Date(filters.date_from));
    }
    if (filters.date_to) {
      filtered = filtered.filter(a => new Date(a.timestamp) <= new Date(filters.date_to));
    }

    return filtered;
  }

  getContentDetails(contentId) {
    return this.content.find(c => c.content_id === contentId);
  }

  getPopularContent(limit = 10, timeframe = null) {
    let relevantAnalytics = [...this.analytics];

    // Filter by timeframe if specified
    if (timeframe) {
      const cutoffDate = new Date();
      if (timeframe === 'day') {
        cutoffDate.setDate(cutoffDate.getDate() - 1);
      } else if (timeframe === 'week') {
        cutoffDate.setDate(cutoffDate.getDate() - 7);
      } else if (timeframe === 'month') {
        cutoffDate.setMonth(cutoffDate.getMonth() - 1);
      }

      relevantAnalytics = relevantAnalytics.filter(a => 
        new Date(a.timestamp) >= cutoffDate
      );
    }

    // Count views per content
    const viewCounts = {};
    const watchTime = {};

    relevantAnalytics.forEach(record => {
      viewCounts[record.content_id] = (viewCounts[record.content_id] || 0) + 1;
      watchTime[record.content_id] = (watchTime[record.content_id] || 0) + 
        parseFloat(record.watch_duration_minutes || 0);
    });

    // Get content details and sort by views
    const popularContent = Object.entries(viewCounts)
      .map(([contentId, views]) => {
        const content = this.getContentDetails(contentId);
        return {
          content_id: contentId,
          title: content?.title || 'Unknown',
          genre: content?.genre || 'Unknown',
          views,
          total_watch_time: Math.round(watchTime[contentId]),
          avg_watch_time: Math.round(watchTime[contentId] / views)
        };
      })
      .sort((a, b) => b.views - a.views)
      .slice(0, limit);

    return popularContent;
  }

  getUserMetrics(userId) {
    const userViews = this.analytics.filter(a => a.user_id === userId);

    if (userViews.length === 0) {
      return { error: 'User not found or no viewing history' };
    }

    const metrics = {
      user_id: userId,
      total_views: userViews.length,
      total_watch_time: 0,
      favorite_genres: {},
      viewing_by_hour: new Array(24).fill(0),
      content_completion_rate: 0,
      unique_content_watched: new Set(),
      viewing_streak: 0
    };

    let completedViews = 0;

    userViews.forEach(view => {
      // Watch time
      metrics.total_watch_time += parseFloat(view.watch_duration_minutes || 0);

      // Unique content
      metrics.unique_content_watched.add(view.content_id);

      // Completion rate
      if (parseFloat(view.completion_rate) >= 0.9) {
        completedViews++;
      }

      // Viewing by hour
      const hour = new Date(view.timestamp).getHours();
      metrics.viewing_by_hour[hour]++;

      // Genre preferences
      const content = this.getContentDetails(view.content_id);
      if (content && content.genre) {
        metrics.favorite_genres[content.genre] = 
          (metrics.favorite_genres[content.genre] || 0) + 1;
      }
    });

    metrics.unique_content_watched = metrics.unique_content_watched.size;
    metrics.completion_rate = (completedViews / userViews.length * 100).toFixed(2) + '%';
    metrics.total_watch_time = Math.round(metrics.total_watch_time);
    metrics.avg_watch_time_per_view = Math.round(metrics.total_watch_time / userViews.length);

    // Sort genres by preference
    metrics.favorite_genres = Object.entries(metrics.favorite_genres)
      .sort(([, a], [, b]) => b - a)
      .reduce((acc, [genre, count]) => {
        acc[genre] = count;
        return acc;
      }, {});

    return metrics;
  }

  getContentRecommendations(userId, limit = 5) {
    const userMetrics = this.getUserMetrics(userId);
    
    if (userMetrics.error) {
      return { error: userMetrics.error };
    }

    const watchedContent = new Set(
      this.analytics
        .filter(a => a.user_id === userId)
        .map(a => a.content_id)
    );

    // Get user's favorite genres
    const favoriteGenres = Object.keys(userMetrics.favorite_genres);

    // Find unwatched content in favorite genres
    const recommendations = this.content
      .filter(content => {
        return !watchedContent.has(content.content_id) &&
               favoriteGenres.includes(content.genre);
      })
      .map(content => {
        // Score based on genre preference and ratings
        const genreScore = userMetrics.favorite_genres[content.genre] || 0;
        const ratingScore = parseFloat(content.rating || 0);
        const totalScore = genreScore * 0.7 + ratingScore * 0.3;

        return {
          ...content,
          recommendation_score: totalScore.toFixed(2),
          reason: `Based on your interest in ${content.genre} content`
        };
      })
      .sort((a, b) => b.recommendation_score - a.recommendation_score)
      .slice(0, limit);

    return {
      user_id: userId,
      recommendations
    };
  }

  getEngagementAnalytics() {
    const totalViews = this.analytics.length;
    const uniqueUsers = new Set(this.analytics.map(a => a.user_id)).size;
    const uniqueContent = new Set(this.analytics.map(a => a.content_id)).size;

    // Calculate engagement metrics
    let totalWatchTime = 0;
    let highEngagementViews = 0;
    const deviceUsage = {};
    const genrePerformance = {};

    this.analytics.forEach(view => {
      totalWatchTime += parseFloat(view.watch_duration_minutes || 0);
      
      if (parseFloat(view.completion_rate) >= 0.8) {
        highEngagementViews++;
      }

      // Device usage
      deviceUsage[view.device_type] = (deviceUsage[view.device_type] || 0) + 1;
    });

    // Genre performance
    this.content.forEach(content => {
      const views = this.analytics.filter(a => a.content_id === content.content_id);
      if (views.length > 0) {
        const avgCompletion = views.reduce((sum, v) => 
          sum + parseFloat(v.completion_rate || 0), 0) / views.length;
        
        if (!genrePerformance[content.genre]) {
          genrePerformance[content.genre] = {
            views: 0,
            avg_completion: 0,
            total_watch_time: 0
          };
        }

        genrePerformance[content.genre].views += views.length;
        genrePerformance[content.genre].avg_completion = avgCompletion;
        genrePerformance[content.genre].total_watch_time += 
          views.reduce((sum, v) => sum + parseFloat(v.watch_duration_minutes || 0), 0);
      }
    });

    return {
      overview: {
        total_views: totalViews,
        unique_users: uniqueUsers,
        unique_content: uniqueContent,
        total_watch_time_hours: Math.round(totalWatchTime / 60),
        avg_watch_time_minutes: Math.round(totalWatchTime / totalViews),
        high_engagement_rate: (highEngagementViews / totalViews * 100).toFixed(2) + '%'
      },
      device_usage: deviceUsage,
      genre_performance: genrePerformance
    };
  }
}

// Initialize data cache
const dataCache = new StreamingDataCache();

// MCP Server setup
const server = new Server(
  {
    name: 'acme-streaming-analytics-mcp',
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
        name: 'get_viewing_history',
        description: 'Get viewing history with optional filters',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: {
              type: 'string',
              description: 'Filter by user ID'
            },
            content_id: {
              type: 'string',
              description: 'Filter by content ID'
            },
            date_from: {
              type: 'string',
              description: 'Start date (ISO format)'
            },
            date_to: {
              type: 'string',
              description: 'End date (ISO format)'
            },
            limit: {
              type: 'number',
              description: 'Maximum records to return',
              default: 100
            }
          },
        },
      },
      {
        name: 'get_popular_content',
        description: 'Get most popular content by views',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Number of items to return',
              default: 10
            },
            timeframe: {
              type: 'string',
              description: 'Timeframe for popularity',
              enum: ['day', 'week', 'month', 'all'],
              default: 'all'
            }
          },
        },
      },
      {
        name: 'get_user_metrics',
        description: 'Get detailed viewing metrics for a specific user',
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
        name: 'get_content_details',
        description: 'Get details about a specific content item',
        inputSchema: {
          type: 'object',
          properties: {
            content_id: {
              type: 'string',
              description: 'The content ID',
            },
          },
          required: ['content_id'],
        },
      },
      {
        name: 'get_content_recommendations',
        description: 'Get personalized content recommendations for a user',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: {
              type: 'string',
              description: 'The user ID',
            },
            limit: {
              type: 'number',
              description: 'Number of recommendations',
              default: 5
            }
          },
          required: ['user_id'],
        },
      },
      {
        name: 'get_engagement_analytics',
        description: 'Get overall platform engagement analytics',
        inputSchema: {
          type: 'object',
          properties: {},
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
    case 'get_viewing_history': {
      const { limit = 100, ...filters } = args;
      const history = dataCache.getViewingHistory(filters);
      const limited = history.slice(0, limit);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              total_matches: history.length,
              returned: limited.length,
              viewing_history: limited
            }, null, 2),
          },
        ],
      };
    }

    case 'get_popular_content': {
      const { limit = 10, timeframe = 'all' } = args;
      const popular = dataCache.getPopularContent(limit, timeframe === 'all' ? null : timeframe);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              timeframe,
              popular_content: popular
            }, null, 2),
          },
        ],
      };
    }

    case 'get_user_metrics': {
      const { user_id } = args;
      const metrics = dataCache.getUserMetrics(user_id);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ user_metrics: metrics }, null, 2),
          },
        ],
      };
    }

    case 'get_content_details': {
      const { content_id } = args;
      const content = dataCache.getContentDetails(content_id);

      if (!content) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: 'Content not found' }),
            },
          ],
        };
      }

      // Add viewing statistics
      const views = dataCache.analytics.filter(a => a.content_id === content_id);
      const avgCompletion = views.length > 0 ?
        views.reduce((sum, v) => sum + parseFloat(v.completion_rate || 0), 0) / views.length : 0;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              content_details: content,
              statistics: {
                total_views: views.length,
                avg_completion_rate: (avgCompletion * 100).toFixed(2) + '%',
                unique_viewers: new Set(views.map(v => v.user_id)).size
              }
            }, null, 2),
          },
        ],
      };
    }

    case 'get_content_recommendations': {
      const { user_id, limit = 5 } = args;
      const recommendations = dataCache.getContentRecommendations(user_id, limit);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ recommendations }, null, 2),
          },
        ],
      };
    }

    case 'get_engagement_analytics': {
      const analytics = dataCache.getEngagementAnalytics();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ engagement_analytics: analytics }, null, 2),
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
  console.error('Acme Streaming Analytics MCP Server running');
}

main().catch(console.error);