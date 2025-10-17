import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  ShoppingCart, 
  Monitor, 
  MapPin, 
  Heart, 
  CreditCard,
  GraduationCap,
  Building,
  Utensils,
  Factory,
  CheckCircle,
  Clock,
  Users,
  Zap,
  Settings,
  Download,
  Eye
} from 'lucide-react';
import MobileMatrixOptimizer from '../components/MobileMatrixOptimizer';
import TerminalWindow from '../components/TerminalWindow';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const IndustryTemplates = () => {
  const [templatesData, setTemplatesData] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [deploymentConfig, setDeploymentConfig] = useState(null);

  useEffect(() => {
    fetchTemplatesData();
  }, []);

  const fetchTemplatesData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      const response = await fetch(`${backendUrl}/api/templates/industries`);
      if (response.ok) {
        const result = await response.json();
        setTemplatesData(result.data || {});
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching templates data:', error);
      setLoading(false);
    }
  };

  const handleTemplateSelect = async (industry) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      const response = await fetch(`${backendUrl}/api/templates/industries/${industry}`);
      if (response.ok) {
        const result = await response.json();
        setSelectedTemplate({industry, ...result.data});
      }
    } catch (error) {
      console.error('Error fetching template details:', error);
    }
  };

  const handleDeployTemplate = async (industry, customizations = {}) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      const response = await fetch(`${backendUrl}/api/templates/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry, customizations })
      });

      if (response.ok) {
        const result = await response.json();
        setDeploymentConfig(result.data);
      }
    } catch (error) {
      console.error('Error deploying template:', error);
    }
  };

  const getIndustryIcon = (industry) => {
    switch (industry) {
      case 'ecommerce': return <ShoppingCart className="w-6 h-6" />;
      case 'saas': return <Monitor className="w-6 h-6" />;
      case 'local_service': return <MapPin className="w-6 h-6" />;
      case 'healthcare': return <Heart className="w-6 h-6" />;
      case 'fintech': return <CreditCard className="w-6 h-6" />;
      case 'education': return <GraduationCap className="w-6 h-6" />;
      case 'real_estate': return <Building className="w-6 h-6" />;
      case 'restaurant': return <Utensils className="w-6 h-6" />;
      case 'manufacturing': return <Factory className="w-6 h-6" />;
      default: return <Layers className="w-6 h-6" />;
    }
  };

  const getIndustryColor = (industry) => {
    const colors = {
      ecommerce: 'bg-blue-400/20 text-blue-400 border-blue-400/40',
      saas: 'bg-green-400/20 text-green-400 border-green-400/40',
      local_service: 'bg-yellow-400/20 text-yellow-400 border-yellow-400/40',
      healthcare: 'bg-red-400/20 text-red-400 border-red-400/40',
      fintech: 'bg-purple-400/20 text-purple-400 border-purple-400/40',
      education: 'bg-indigo-400/20 text-indigo-400 border-indigo-400/40',
      real_estate: 'bg-orange-400/20 text-orange-400 border-orange-400/40',
      restaurant: 'bg-pink-400/20 text-pink-400 border-pink-400/40',
      manufacturing: 'bg-gray-400/20 text-gray-400 border-gray-400/40'
    };
    return colors[industry] || 'bg-matrix-green/20 text-matrix-green border-matrix-green/40';
  };

  const formatIndustryName = (industry) => {
    return industry.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-2 border-matrix-green border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-matrix-green/80">Loading Industry Templates...</p>
        </div>
      </MobileMatrixOptimizer>
    );
  }

  const templates = templatesData.templates || {};
  const industries = templatesData.industries || [];

  return (
    <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green relative overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 z-0 bg-matrix-gradient-dark" />
      
      {/* Header */}
      <div className="relative z-10 pt-24 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="bg-gradient-to-r from-matrix-green/20 to-matrix-cyan/20 text-matrix-green border-matrix-green/40 font-body animate-scaleIn mb-4">
              🏭 Industry Blueprints
            </Badge>
            
            <h1 className="text-4xl lg:text-6xl font-bold font-heading leading-tight animate-fadeInUp">
              <span className="matrix-text-bright animate-glow">
                TEMPLATE_DEPLOYMENT
              </span>
            </h1>
            
            <p className="text-xl text-matrix-green/80 font-body mt-4 animate-fadeInUp" style={{animationDelay: '0.2s'}}>
              Pre-configured AI agent setups for rapid deployment across industries
            </p>
          </div>

          {/* Template Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Available Templates</CardTitle>
                <Layers className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{templatesData.total_templates || 0}</div>
                <p className="text-xs text-matrix-green/60">Industry blueprints</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Setup Time</CardTitle>
                <Clock className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">30min</div>
                <p className="text-xs text-matrix-green/60">Average deployment</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Success Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">98%</div>
                <p className="text-xs text-matrix-green/60">Deployment success</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">ROI Improvement</CardTitle>
                <Zap className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">300%</div>
                <p className="text-xs text-matrix-green/60">Average ROI boost</p>
              </CardContent>
            </Card>
          </div>

          {/* Industry Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {Object.entries(templates).map(([industryKey, template]) => (
              <Card key={industryKey} className="modern-card hover-glow cursor-pointer" onClick={() => handleTemplateSelect(industryKey)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-matrix-green/10 rounded-lg">
                        {getIndustryIcon(industryKey)}
                      </div>
                      <div>
                        <CardTitle className="text-matrix-green font-heading">
                          {template.name || formatIndustryName(industryKey)}
                        </CardTitle>
                        <CardDescription className="text-matrix-green/60 text-sm">
                          {template.description || "Industry-specific AI automation"}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge className={`${getIndustryColor(industryKey)} font-mono text-xs`}>
                      {formatIndustryName(industryKey)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Template Features */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="text-center">
                        <div className="text-lg font-bold text-matrix-bright-cyan">
                          {Object.keys(template.agents || {}).length}
                        </div>
                        <div className="text-xs text-matrix-green/60">AI Agents</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-matrix-bright-cyan">
                          {(template.integrations || []).length}
                        </div>
                        <div className="text-xs text-matrix-green/60">Integrations</div>
                      </div>
                    </div>

                    {/* Key Features */}
                    {template.focus_areas && (
                      <div>
                        <h4 className="text-sm font-semibold text-matrix-green mb-2">Focus Areas</h4>
                        <div className="flex flex-wrap gap-1">
                          {template.focus_areas.slice(0, 3).map((area, index) => (
                            <Badge key={index} variant="outline" className="text-xs font-mono border-matrix-green/40 text-matrix-green/80">
                              {area.replace(/_/g, ' ')}
                            </Badge>
                          ))}
                          {template.focus_areas.length > 3 && (
                            <Badge variant="outline" className="text-xs font-mono border-matrix-green/40 text-matrix-green/80">
                              +{template.focus_areas.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex space-x-2 pt-2">
                      <Button 
                        size="sm" 
                        className="flex-1 btn-matrix hover-lift font-heading"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeployTemplate(industryKey);
                        }}
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Deploy
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="border-matrix-green text-matrix-green hover:bg-matrix-green/10"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTemplateSelect(industryKey);
                        }}
                      >
                        <Eye className="w-3 h-3 mr-1" />
                        Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Template Details Modal */}
          {selectedTemplate && (
            <div className="mb-8">
              <TerminalWindow title={`${selectedTemplate.name?.toUpperCase()}_BLUEPRINT.json`}>
                <div className="space-y-2 text-sm font-mono max-h-64 overflow-y-auto">
                  <div className="text-matrix-green animate-glow">
                    {`{`}
                  </div>
                  <div className="text-matrix-cyan ml-2">
                    "template": "{selectedTemplate.name}",
                  </div>
                  <div className="text-matrix-cyan ml-2">
                    "industry": "{selectedTemplate.industry}",
                  </div>
                  <div className="text-matrix-green ml-2">
                    "agents": {`{`}
                  </div>
                  {Object.keys(selectedTemplate.agents || {}).map((agentType, index) => (
                    <div key={agentType} className="text-matrix-green/80 ml-4">
                      "{agentType}": "configured"{index < Object.keys(selectedTemplate.agents || {}).length - 1 ? ',' : ''}
                    </div>
                  ))}
                  <div className="text-matrix-green ml-2">
                    {`}`},
                  </div>
                  <div className="text-matrix-green ml-2">
                    "integrations": [
                  </div>
                  {(selectedTemplate.integrations || []).map((integration, index) => (
                    <div key={integration} className="text-matrix-green/80 ml-4">
                      "{integration}"{index < (selectedTemplate.integrations || []).length - 1 ? ',' : ''}
                    </div>
                  ))}
                  <div className="text-matrix-green ml-2">
                    ],
                  </div>
                  <div className="text-matrix-cyan ml-2">
                    "estimated_setup": "30-45 minutes"
                  </div>
                  <div className="text-matrix-green">
                    {`}`}
                  </div>
                </div>
              </TerminalWindow>
              
              <div className="flex justify-end space-x-4 mt-4">
                <Button 
                  variant="outline"
                  className="border-matrix-green text-matrix-green hover:bg-matrix-green/10"
                  onClick={() => setSelectedTemplate(null)}
                >
                  Close
                </Button>
                <Button 
                  className="btn-matrix hover-lift font-heading"
                  onClick={() => handleDeployTemplate(selectedTemplate.industry)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Deploy Template
                </Button>
              </div>
            </div>
          )}

          {/* Deployment Configuration */}
          {deploymentConfig && (
            <div className="mb-8">
              <Card className="modern-card hover-glow">
                <CardHeader>
                  <CardTitle className="text-matrix-green font-heading flex items-center">
                    <Settings className="w-5 h-5 mr-2" />
                    Deployment Configuration
                  </CardTitle>
                  <CardDescription className="text-matrix-green/60">
                    Review and customize your template deployment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Deployment Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                        <Users className="w-6 h-6 text-matrix-green mx-auto mb-2" />
                        <div className="text-lg font-bold text-matrix-bright-cyan">
                          {deploymentConfig.agents_to_deploy?.length || 0}
                        </div>
                        <div className="text-xs text-matrix-green/60">Agents to Deploy</div>
                      </div>
                      <div className="text-center p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                        <Zap className="w-6 h-6 text-matrix-green mx-auto mb-2" />
                        <div className="text-lg font-bold text-matrix-bright-cyan">
                          {deploymentConfig.integrations_to_setup?.length || 0}
                        </div>
                        <div className="text-xs text-matrix-green/60">Integrations</div>
                      </div>
                      <div className="text-center p-4 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                        <Clock className="w-6 h-6 text-matrix-green mx-auto mb-2" />
                        <div className="text-lg font-bold text-matrix-bright-cyan">
                          {deploymentConfig.estimated_setup_time}
                        </div>
                        <div className="text-xs text-matrix-green/60">Setup Time</div>
                      </div>
                    </div>

                    {/* Agents Configuration */}
                    <div>
                      <h3 className="text-lg font-semibold text-matrix-green mb-4">AI Agents Configuration</h3>
                      <div className="space-y-3">
                        {(deploymentConfig.agents_to_deploy || []).map((agent, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-matrix-green/5 rounded-lg border border-matrix-green/20">
                            <div className="flex items-center space-x-3">
                              <Badge className={`${getIndustryColor('default')} font-mono`}>
                                {agent.agent_type?.replace('_', ' ').toUpperCase()}
                              </Badge>
                              <div>
                                <div className="text-matrix-green font-medium">{agent.agent_type?.replace('_', ' ')}</div>
                                <div className="text-xs text-matrix-green/60">{agent.workflows?.length || 0} workflows configured</div>
                              </div>
                            </div>
                            <Badge variant="outline" className={`font-mono ${agent.priority === 'high' ? 'border-red-400 text-red-400' : 'border-matrix-green text-matrix-green'}`}>
                              {agent.priority} priority
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Deploy Button */}
                    <div className="flex justify-center pt-4">
                      <Button className="btn-matrix hover-lift font-heading px-8 py-3">
                        <Download className="w-5 h-5 mr-2" />
                        Execute Deployment
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Custom Template Creation */}
          <Card className="modern-card hover-glow">
            <CardHeader>
              <CardTitle className="text-matrix-green font-heading">Create Custom Template</CardTitle>
              <CardDescription className="text-matrix-green/60">
                Build your own industry-specific template for unique business requirements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-matrix-green/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Settings className="w-8 h-8 text-matrix-green" />
                </div>
                <p className="text-matrix-green/70 mb-4">
                  Need a custom solution? Create your own template with specific agent configurations and integrations.
                </p>
                <Button className="btn-matrix hover-lift font-heading">
                  <Layers className="w-4 h-4 mr-2" />
                  Build Custom Template
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MobileMatrixOptimizer>
  );
};

export default IndustryTemplates;