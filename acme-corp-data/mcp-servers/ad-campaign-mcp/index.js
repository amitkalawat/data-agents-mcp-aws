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

// Data cache for ad campaigns
class AdCampaignDataCache {
  constructor() {
    this.campaigns = [];
    this.performance = [];
    this.attribution = [];
    this.loaded = false;
  }

  async loadData() {
    if (this.loaded) return;

    try {
      // Load campaigns
      const campaignsPath = path.join(__dirname, '../../ad_campaign_data/campaigns.csv');
      const campaignsData = await fs.readFile(campaignsPath, 'utf8');
      
      this.campaigns = parse(campaignsData, {
        columns: true,
        skip_empty_lines: true
      });

      // Load campaign performance
      const performancePath = path.join(__dirname, '../../ad_campaign_data/campaign_performance.csv');
      const performanceData = await fs.readFile(performancePath, 'utf8');
      
      this.performance = parse(performanceData, {
        columns: true,
        skip_empty_lines: true
      });

      // Load attribution data
      const attributionPath = path.join(__dirname, '../../ad_campaign_data/attribution_data.csv');
      const attributionData = await fs.readFile(attributionPath, 'utf8');
      
      this.attribution = parse(attributionData, {
        columns: true,
        skip_empty_lines: true
      });

      this.loaded = true;
      console.error(`Loaded ${this.campaigns.length} campaigns, ${this.performance.length} performance records, ${this.attribution.length} attribution records`);
    } catch (error) {
      console.error('Failed to load ad campaign data:', error);
      throw error;
    }
  }

  getCampaigns(filters = {}) {
    let filtered = [...this.campaigns];

    if (filters.status) {
      filtered = filtered.filter(c => c.status === filters.status);
    }
    if (filters.platform) {
      filtered = filtered.filter(c => c.platform === filters.platform);
    }
    if (filters.budget_min) {
      filtered = filtered.filter(c => parseFloat(c.budget) >= filters.budget_min);
    }
    if (filters.budget_max) {
      filtered = filtered.filter(c => parseFloat(c.budget) <= filters.budget_max);
    }

    return filtered;
  }

  getCampaignById(campaignId) {
    return this.campaigns.find(c => c.campaign_id === campaignId);
  }

  getCampaignPerformance(campaignId, dateRange = null) {
    let perfData = this.performance.filter(p => p.campaign_id === campaignId);

    if (dateRange) {
      if (dateRange.from) {
        perfData = perfData.filter(p => new Date(p.date) >= new Date(dateRange.from));
      }
      if (dateRange.to) {
        perfData = perfData.filter(p => new Date(p.date) <= new Date(dateRange.to));
      }
    }

    // Aggregate performance metrics
    const metrics = {
      campaign_id: campaignId,
      total_impressions: 0,
      total_clicks: 0,
      total_conversions: 0,
      total_spend: 0,
      ctr: 0,
      conversion_rate: 0,
      cpc: 0,
      cpa: 0,
      roas: 0,
      daily_performance: []
    };

    perfData.forEach(day => {
      metrics.total_impressions += parseInt(day.impressions || 0);
      metrics.total_clicks += parseInt(day.clicks || 0);
      metrics.total_conversions += parseInt(day.conversions || 0);
      metrics.total_spend += parseFloat(day.spend || 0);

      metrics.daily_performance.push({
        date: day.date,
        impressions: parseInt(day.impressions || 0),
        clicks: parseInt(day.clicks || 0),
        conversions: parseInt(day.conversions || 0),
        spend: parseFloat(day.spend || 0),
        ctr: parseFloat(day.ctr || 0),
        conversion_rate: parseFloat(day.conversion_rate || 0)
      });
    });

    // Calculate aggregate metrics
    if (metrics.total_impressions > 0) {
      metrics.ctr = (metrics.total_clicks / metrics.total_impressions * 100).toFixed(2);
    }
    if (metrics.total_clicks > 0) {
      metrics.conversion_rate = (metrics.total_conversions / metrics.total_clicks * 100).toFixed(2);
      metrics.cpc = (metrics.total_spend / metrics.total_clicks).toFixed(2);
    }
    if (metrics.total_conversions > 0) {
      metrics.cpa = (metrics.total_spend / metrics.total_conversions).toFixed(2);
    }

    metrics.total_spend = metrics.total_spend.toFixed(2);

    return metrics;
  }

  getAttributionAnalysis(campaignId = null) {
    let attrData = [...this.attribution];

    if (campaignId) {
      attrData = attrData.filter(a => a.campaign_id === campaignId);
    }

    // Analyze attribution paths
    const pathAnalysis = {
      total_conversions: attrData.length,
      by_channel: {},
      by_path_length: {},
      first_touch: {},
      last_touch: {},
      multi_touch: {}
    };

    attrData.forEach(attr => {
      const path = attr.touchpoint_path.split(' -> ');
      const pathLength = path.length;

      // Path length analysis
      pathAnalysis.by_path_length[pathLength] = 
        (pathAnalysis.by_path_length[pathLength] || 0) + 1;

      // Channel analysis
      path.forEach(channel => {
        pathAnalysis.by_channel[channel] = 
          (pathAnalysis.by_channel[channel] || 0) + 1;
      });

      // Attribution models
      const firstTouch = path[0];
      const lastTouch = path[path.length - 1];

      pathAnalysis.first_touch[firstTouch] = 
        (pathAnalysis.first_touch[firstTouch] || 0) + 1;
      
      pathAnalysis.last_touch[lastTouch] = 
        (pathAnalysis.last_touch[lastTouch] || 0) + 1;

      // Multi-touch (equal credit)
      path.forEach(channel => {
        pathAnalysis.multi_touch[channel] = 
          (pathAnalysis.multi_touch[channel] || 0) + (1 / pathLength);
      });
    });

    // Round multi-touch values
    Object.keys(pathAnalysis.multi_touch).forEach(key => {
      pathAnalysis.multi_touch[key] = Math.round(pathAnalysis.multi_touch[key]);
    });

    return pathAnalysis;
  }

  getCampaignComparison() {
    const comparison = [];

    this.campaigns.forEach(campaign => {
      const performance = this.getCampaignPerformance(campaign.campaign_id);
      
      comparison.push({
        campaign_id: campaign.campaign_id,
        campaign_name: campaign.campaign_name,
        platform: campaign.platform,
        status: campaign.status,
        budget: parseFloat(campaign.budget),
        spent: parseFloat(performance.total_spend),
        budget_utilization: (parseFloat(performance.total_spend) / parseFloat(campaign.budget) * 100).toFixed(2) + '%',
        impressions: performance.total_impressions,
        clicks: performance.total_clicks,
        conversions: performance.total_conversions,
        ctr: performance.ctr,
        conversion_rate: performance.conversion_rate,
        cpa: parseFloat(performance.cpa),
        roi: campaign.target_audience // This would normally be calculated
      });
    });

    // Sort by conversions
    comparison.sort((a, b) => b.conversions - a.conversions);

    return comparison;
  }

  getOptimizationRecommendations(campaignId) {
    const campaign = this.getCampaignById(campaignId);
    const performance = this.getCampaignPerformance(campaignId);
    const attribution = this.getAttributionAnalysis(campaignId);

    if (!campaign) {
      return { error: 'Campaign not found' };
    }

    const recommendations = [];

    // CTR optimization
    if (parseFloat(performance.ctr) < 2) {
      recommendations.push({
        type: 'ctr_optimization',
        priority: 'high',
        recommendation: 'CTR is below industry average (2%). Consider improving ad creatives or targeting.',
        current_value: performance.ctr + '%',
        target_value: '2-3%'
      });
    }

    // Budget utilization
    const utilization = (parseFloat(performance.total_spend) / parseFloat(campaign.budget) * 100);
    if (utilization < 70 && campaign.status === 'Active') {
      recommendations.push({
        type: 'budget_utilization',
        priority: 'medium',
        recommendation: 'Budget utilization is low. Consider expanding targeting or increasing bids.',
        current_value: utilization.toFixed(2) + '%',
        target_value: '80-90%'
      });
    }

    // CPA optimization
    if (parseFloat(performance.cpa) > 50) {
      recommendations.push({
        type: 'cpa_optimization',
        priority: 'high',
        recommendation: 'CPA is high. Consider refining targeting or improving landing page conversion.',
        current_value: '$' + performance.cpa,
        target_value: '<$50'
      });
    }

    // Attribution insights
    const pathLengths = Object.keys(attribution.by_path_length);
    const avgPathLength = pathLengths.reduce((sum, len) => 
      sum + (parseInt(len) * attribution.by_path_length[len]), 0) / attribution.total_conversions;

    if (avgPathLength > 3) {
      recommendations.push({
        type: 'conversion_path',
        priority: 'medium',
        recommendation: 'Conversion paths are long. Consider remarketing to shorten the journey.',
        current_value: avgPathLength.toFixed(1) + ' touchpoints',
        target_value: '2-3 touchpoints'
      });
    }

    return {
      campaign_id: campaignId,
      campaign_name: campaign.campaign_name,
      recommendations,
      performance_summary: {
        ctr: performance.ctr + '%',
        conversion_rate: performance.conversion_rate + '%',
        cpa: '$' + performance.cpa,
        budget_utilization: utilization.toFixed(2) + '%'
      }
    };
  }
}

// Initialize data cache
const dataCache = new AdCampaignDataCache();

// MCP Server setup
const server = new Server(
  {
    name: 'acme-ad-campaign-mcp',
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
        name: 'get_campaigns',
        description: 'Get list of ad campaigns with optional filters',
        inputSchema: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              description: 'Filter by campaign status',
              enum: ['Active', 'Paused', 'Completed']
            },
            platform: {
              type: 'string',
              description: 'Filter by advertising platform',
              enum: ['Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'Twitter']
            },
            budget_min: {
              type: 'number',
              description: 'Minimum budget filter'
            },
            budget_max: {
              type: 'number',
              description: 'Maximum budget filter'
            }
          },
        },
      },
      {
        name: 'get_campaign_performance',
        description: 'Get detailed performance metrics for a specific campaign',
        inputSchema: {
          type: 'object',
          properties: {
            campaign_id: {
              type: 'string',
              description: 'The campaign ID',
            },
            date_from: {
              type: 'string',
              description: 'Start date for metrics (ISO format)'
            },
            date_to: {
              type: 'string',
              description: 'End date for metrics (ISO format)'
            }
          },
          required: ['campaign_id'],
        },
      },
      {
        name: 'get_attribution_analysis',
        description: 'Get attribution analysis showing conversion paths',
        inputSchema: {
          type: 'object',
          properties: {
            campaign_id: {
              type: 'string',
              description: 'Optional: filter by campaign ID'
            }
          },
        },
      },
      {
        name: 'compare_campaigns',
        description: 'Get comparison of all campaigns performance',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_optimization_recommendations',
        description: 'Get AI-powered optimization recommendations for a campaign',
        inputSchema: {
          type: 'object',
          properties: {
            campaign_id: {
              type: 'string',
              description: 'The campaign ID',
            },
          },
          required: ['campaign_id'],
        },
      },
      {
        name: 'get_campaign_roi',
        description: 'Calculate ROI and profitability metrics for campaigns',
        inputSchema: {
          type: 'object',
          properties: {
            campaign_id: {
              type: 'string',
              description: 'Optional: specific campaign ID'
            }
          },
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
    case 'get_campaigns': {
      const campaigns = dataCache.getCampaigns(args);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              total_campaigns: campaigns.length,
              campaigns
            }, null, 2),
          },
        ],
      };
    }

    case 'get_campaign_performance': {
      const { campaign_id, date_from, date_to } = args;
      const dateRange = (date_from || date_to) ? { from: date_from, to: date_to } : null;
      const performance = dataCache.getCampaignPerformance(campaign_id, dateRange);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ campaign_performance: performance }, null, 2),
          },
        ],
      };
    }

    case 'get_attribution_analysis': {
      const { campaign_id } = args;
      const analysis = dataCache.getAttributionAnalysis(campaign_id);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ 
              attribution_analysis: analysis,
              campaign_filter: campaign_id || 'all_campaigns'
            }, null, 2),
          },
        ],
      };
    }

    case 'compare_campaigns': {
      const comparison = dataCache.getCampaignComparison();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ 
              campaign_comparison: comparison,
              total_campaigns: comparison.length
            }, null, 2),
          },
        ],
      };
    }

    case 'get_optimization_recommendations': {
      const { campaign_id } = args;
      const recommendations = dataCache.getOptimizationRecommendations(campaign_id);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ optimization_recommendations: recommendations }, null, 2),
          },
        ],
      };
    }

    case 'get_campaign_roi': {
      const { campaign_id } = args;
      
      // Calculate ROI for specific campaign or all campaigns
      const campaigns = campaign_id ? 
        [dataCache.getCampaignById(campaign_id)].filter(Boolean) : 
        dataCache.campaigns;

      const roiAnalysis = campaigns.map(campaign => {
        const performance = dataCache.getCampaignPerformance(campaign.campaign_id);
        const revenue = performance.total_conversions * 100; // Assume $100 per conversion
        const roi = ((revenue - parseFloat(performance.total_spend)) / parseFloat(performance.total_spend) * 100).toFixed(2);

        return {
          campaign_id: campaign.campaign_id,
          campaign_name: campaign.campaign_name,
          total_spend: '$' + performance.total_spend,
          total_revenue: '$' + revenue.toFixed(2),
          profit: '$' + (revenue - parseFloat(performance.total_spend)).toFixed(2),
          roi: roi + '%',
          is_profitable: parseFloat(roi) > 0
        };
      });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ 
              roi_analysis: roiAnalysis,
              summary: {
                total_campaigns: roiAnalysis.length,
                profitable_campaigns: roiAnalysis.filter(c => c.is_profitable).length,
                avg_roi: (roiAnalysis.reduce((sum, c) => sum + parseFloat(c.roi), 0) / roiAnalysis.length).toFixed(2) + '%'
              }
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
  console.error('Acme Ad Campaign MCP Server running');
}

main().catch(console.error);