import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Target,
  Lightbulb,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Users,
  DollarSign,
  Clock,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import MobileMatrixOptimizer from '../components/MobileMatrixOptimizer';
import TerminalWindow from '../components/TerminalWindow';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const InsightsDashboard = () => {
  const [insights, setInsights] = useState([]);
  const [insightsSummary, setInsightsSummary] = useState({});
  const [performanceData, setPerformanceData] = useState({});
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchInsightsData();
    const interval = setInterval(fetchInsightsData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchInsightsData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      // Fetch insights summary
      const summaryResponse = await fetch(`${backendUrl}/api/insights/summary?days=7`);
      if (summaryResponse.ok) {
        const summaryResult = await summaryResponse.json();
        setInsightsSummary(summaryResult.data || {});
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching insights data:', error);
      setLoading(false);
    }
  };

  const runPerformanceAnalysis = async () => {
    setAnalyzing(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      // Mock performance data - in production this would come from actual metrics
      const mockPerformanceData = {
        success_rate: 0.92,
        average_response_time: 2.3,
        cpu_utilization: 0.65,
        memory_utilization: 0.58,
        total_requests: 15420,
        error_rate: 0.03,
        active_users: 234,
        revenue_today: 18500
      };

      const response = await fetch(`${backendUrl}/api/insights/analyze-performance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockPerformanceData)
      });

      if (response.ok) {
        const result = await response.json();
        setInsights(result.data?.insights || []);
        setPerformanceData(mockPerformanceData);
      }
    } catch (error) {
      console.error('Error running performance analysis:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const runAnomalyDetection = async () => {
    setAnalyzing(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      // Mock business data for anomaly detection
      const mockBusinessData = {
        revenue: {
          daily_revenue: [12000, 15000, 18000, 22000, 8000], // Last value is anomaly
          average_order_value: 85,
          conversion_rate: 0.034
        },
        customers: {
          new_signups: 45,
          churn_rate: 0.02,
          satisfaction_score: 4.2
        },
        operations: {
          server_uptime: 0.998,
          processing_time: 1.2,
          queue_length: 23
        }
      };

      const response = await fetch(`${backendUrl}/api/insights/detect-anomalies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockBusinessData)
      });

      if (response.ok) {
        const result = await response.json();
        const newInsights = result.data?.insights || [];
        setInsights(prevInsights => [...prevInsights, ...newInsights]);
      }
    } catch (error) {
      console.error('Error running anomaly detection:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-400/20 text-red-400 border-red-400/40';
      case 'high': return 'bg-orange-400/20 text-orange-400 border-orange-400/40';
      case 'medium': return 'bg-yellow-400/20 text-yellow-400 border-yellow-400/40';
      case 'low': return 'bg-green-400/20 text-green-400 border-green-400/40';
      default: return 'bg-matrix-green/20 text-matrix-green border-matrix-green/40';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      case 'high': return <TrendingUp className="w-4 h-4" />;
      case 'medium': return <Target className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Lightbulb className="w-4 h-4" />;
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'performance_optimization': return <TrendingUp className="w-5 h-5" />;
      case 'anomaly_detection': return <AlertTriangle className="w-5 h-5" />;
      case 'business_recommendation': return <Lightbulb className="w-5 h-5" />;
      case 'agent_improvement': return <Brain className="w-5 h-5" />;
      case 'cost_optimization': return <DollarSign className="w-5 h-5" />;
      default: return <BarChart3 className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-2 border-matrix-green border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-matrix-green/80">Loading Smart Insights...</p>
        </div>
      </MobileMatrixOptimizer>
    );
  }

  return (
    <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green relative overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 z-0 bg-matrix-gradient-dark" />
      
      {/* Header */}
      <div className="relative z-10 pt-24 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="bg-gradient-to-r from-matrix-green/20 to-matrix-cyan/20 text-matrix-green border-matrix-green/40 font-body animate-scaleIn mb-4">
              🧠 AI-Powered Intelligence
            </Badge>
            
            <h1 className="text-4xl lg:text-6xl font-bold font-heading leading-tight animate-fadeInUp">
              <span className="matrix-text-bright animate-glow">
                SMART_INSIGHTS
              </span>
            </h1>
            
            <p className="text-xl text-matrix-green/80 font-body mt-4 animate-fadeInUp" style={{animationDelay: '0.2s'}}>
              AI-powered analytics, anomaly detection, and optimization recommendations
            </p>
          </div>

          {/* Insights Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Total Insights</CardTitle>
                <Brain className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{insightsSummary.total_insights || 0}</div>
                <p className="text-xs text-matrix-green/60">Last 7 days</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Critical Alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-400">{(insightsSummary.critical_alerts || []).length}</div>
                <p className="text-xs text-matrix-green/60">Require attention</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Optimizations</CardTitle>
                <TrendingUp className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">
                  {insightsSummary.by_type?.performance_optimization || 0}
                </div>
                <p className="text-xs text-matrix-green/60">Available improvements</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Anomalies</CardTitle>
                <Activity className="h-4 w-4 text-orange-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-400">
                  {insightsSummary.by_type?.anomaly_detection || 0}
                </div>
                <p className="text-xs text-matrix-green/60">Detected patterns</p>
              </CardContent>
            </Card>
          </div>

          {/* Analysis Controls */}
          <div className="flex flex-wrap gap-4 mb-8">
            <Button 
              onClick={runPerformanceAnalysis}
              disabled={analyzing}
              className="btn-matrix hover-lift font-heading"
            >
              {analyzing ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <BarChart3 className="w-4 h-4 mr-2" />}
              Analyze Performance
            </Button>
            
            <Button 
              onClick={runAnomalyDetection}
              disabled={analyzing}
              className="btn-matrix hover-lift font-heading"
            >
              {analyzing ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Activity className="w-4 h-4 mr-2" />}
              Detect Anomalies
            </Button>
            
            <Button 
              variant="outline"
              className="border-matrix-green text-matrix-green hover:bg-matrix-green/10"
              onClick={fetchInsightsData}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Data
            </Button>
          </div>

          {/* Current Performance Metrics */}
          {Object.keys(performanceData).length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-matrix-green mb-4">Current Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-matrix-green/70">Success Rate</p>
                      <p className="text-xl font-bold text-matrix-bright-cyan">
                        {(performanceData.success_rate * 100).toFixed(1)}%
                      </p>
                    </div>
                    <CheckCircle className="w-6 h-6 text-green-400" />
                  </div>
                </div>

                <div className="p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-matrix-green/70">Response Time</p>
                      <p className="text-xl font-bold text-matrix-bright-cyan">
                        {performanceData.average_response_time}s
                      </p>
                    </div>
                    <Clock className="w-6 h-6 text-blue-400" />
                  </div>
                </div>

                <div className="p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-matrix-green/70">CPU Usage</p>
                      <p className="text-xl font-bold text-matrix-bright-cyan">
                        {(performanceData.cpu_utilization * 100).toFixed(0)}%
                      </p>
                    </div>
                    <Activity className="w-6 h-6 text-yellow-400" />
                  </div>
                </div>

                <div className="p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-matrix-green/70">Active Users</p>
                      <p className="text-xl font-bold text-matrix-bright-cyan">
                        {performanceData.active_users}
                      </p>
                    </div>
                    <Users className="w-6 h-6 text-matrix-cyan" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Insights List */}
          {insights.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-matrix-green mb-4">Generated Insights</h3>
              <div className="space-y-4">
                {insights.map((insight, index) => (
                  <Card key={index} className="modern-card hover-glow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-matrix-green/10 rounded-lg">
                            {getTypeIcon(insight.type)}
                          </div>
                          <div className="flex-1">
                            <CardTitle className="text-matrix-green font-heading">{insight.title}</CardTitle>
                            <CardDescription className="text-matrix-green/60">
                              {insight.description}
                            </CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getSeverityColor(insight.severity)} font-mono text-xs`}>
                            {getSeverityIcon(insight.severity)}
                            <span className="ml-1">{(insight.severity || 'unknown').toUpperCase()}</span>
                          </Badge>
                          <Badge variant="outline" className="text-matrix-cyan border-matrix-cyan/40 font-mono text-xs">
                            {Math.round(insight.confidence * 100)}% confidence
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {/* Impact Estimate */}
                        <div className="flex items-center justify-between p-3 bg-matrix-green/5 rounded-lg">
                          <span className="text-sm text-matrix-green/70">Estimated Impact:</span>
                          <span className="text-sm font-semibold text-matrix-bright-cyan">{insight.impact}</span>
                        </div>

                        {/* Recommendations */}
                        <div>
                          <h4 className="text-sm font-semibold text-matrix-green mb-2">Recommendations</h4>
                          <ul className="space-y-2">
                            {insight.recommendations.map((rec, recIndex) => (
                              <li key={recIndex} className="flex items-start space-x-2 text-sm text-matrix-green/80">
                                <ArrowRight className="w-3 h-3 mt-1 flex-shrink-0 text-matrix-cyan" />
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex space-x-2 pt-2">
                          <Button size="sm" className="btn-matrix hover-lift font-heading">
                            <Zap className="w-3 h-3 mr-1" />
                            Implement
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="border-matrix-green text-matrix-green hover:bg-matrix-green/10"
                          >
                            Learn More
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* AI Analysis Terminal */}
          <TerminalWindow title="AI_INSIGHTS_ANALYZER.log" className="mb-8">
            <div className="space-y-2 text-sm font-mono max-h-64 overflow-y-auto">
              {analyzing && (
                <>
                  <div className="text-matrix-green animate-glow">
                    &gt; Initializing AI analysis engine...
                  </div>
                  <div className="text-matrix-cyan animate-glow" style={{animationDelay: '0.5s'}}>
                    &gt; Processing performance metrics and business data...
                  </div>
                  <div className="text-matrix-green animate-glow" style={{animationDelay: '1s'}}>
                    &gt; Running anomaly detection algorithms...
                  </div>
                  <div className="text-matrix-cyan animate-glow" style={{animationDelay: '1.5s'}}>
                    &gt; Generating optimization recommendations...
                  </div>
                </>
              )}
              {insights.length > 0 && (
                <>
                  <div className="text-matrix-bright-cyan">
                    ✅ Analysis Complete: {insights.length} insights generated
                  </div>
                  <div className="text-matrix-green/80">
                    📊 Performance metrics analyzed across {Object.keys(performanceData).length} data points
                  </div>
                  <div className="text-matrix-green/80">
                    🎯 {insights.filter(i => i.severity === 'high' || i.severity === 'critical').length} high-priority recommendations identified
                  </div>
                </>
              )}
              {!analyzing && insights.length === 0 && (
                <div className="text-matrix-green/60">
                  💡 Click "Analyze Performance" or "Detect Anomalies" to generate AI insights
                </div>
              )}
            </div>
          </TerminalWindow>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="modern-card hover-lift cursor-pointer">
              <CardHeader>
                <CardTitle className="text-matrix-green flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  Agent Performance Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-matrix-green/70 text-sm">Deep analysis of individual agent performance and improvement suggestions</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift cursor-pointer">
              <CardHeader>
                <CardTitle className="text-matrix-green flex items-center">
                  <PieChart className="w-5 h-5 mr-2" />
                  Business Intelligence
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-matrix-green/70 text-sm">Comprehensive business metrics analysis and growth opportunities</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift cursor-pointer">
              <CardHeader>
                <CardTitle className="text-matrix-green flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Optimization Engine
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-matrix-green/70 text-sm">AI-powered recommendations for cost reduction and performance optimization</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </MobileMatrixOptimizer>
  );
};

export default InsightsDashboard;