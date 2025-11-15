import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Download, 
  Star, 
  Search, 
  Grid3X3, 
  List,
  Zap,
  Shield,
  Users,
  TrendingUp,
  Plus,
  Settings
} from 'lucide-react';
import MobileMatrixOptimizer from '../components/MobileMatrixOptimizer';
import TerminalWindow from '../components/TerminalWindow';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const PluginMarketplace = () => {
  const [marketplaceData, setMarketplaceData] = useState({});
  const [availablePlugins, setAvailablePlugins] = useState({});
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMarketplaceData();
  }, []);

  const fetchMarketplaceData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      
      // Fetch marketplace plugins
      const marketplaceResponse = await fetch(`${backendUrl}/api/plugins/marketplace`);
      if (marketplaceResponse.ok) {
        const marketplaceResult = await marketplaceResponse.json();
        setMarketplaceData(marketplaceResult.data || {});
      }

      // Fetch available/installed plugins
      const availableResponse = await fetch(`${backendUrl}/api/plugins/available`);
      if (availableResponse.ok) {
        const availableResult = await availableResponse.json();
        setAvailablePlugins(availableResult.data || {});
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching marketplace data:', error);
      setLoading(false);
    }
  };

  const handleInstallPlugin = async (pluginId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
      const response = await fetch(`${backendUrl}/api/plugins/${pluginId}/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (response.ok) {
        fetchMarketplaceData(); // Refresh data
      }
    } catch (error) {
      console.error('Error installing plugin:', error);
    }
  };

  const handleCreatePlugin = () => {
    // Navigate to plugin creation interface
    console.log('Creating new plugin...');
  };

  const filteredPlugins = (marketplaceData.featured_plugins || []).filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plugin.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || plugin.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'integration': return <Zap className="w-4 h-4" />;
      case 'automation': return <Settings className="w-4 h-4" />;
      case 'security': return <Shield className="w-4 h-4" />;
      default: return <Package className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'integration': return 'bg-blue-400/20 text-blue-400 border-blue-400/40';
      case 'automation': return 'bg-green-400/20 text-green-400 border-green-400/40';
      case 'security': return 'bg-red-400/20 text-red-400 border-red-400/40';
      default: return 'bg-matrix-green/20 text-matrix-green border-matrix-green/40';
    }
  };

  if (loading) {
    return (
      <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-2 border-matrix-green border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-matrix-green/80">Loading Plugin Marketplace...</p>
        </div>
      </MobileMatrixOptimizer>
    );
  }

  const categories = marketplaceData.categories || {};

  return (
    <MobileMatrixOptimizer className="min-h-screen bg-black text-matrix-green relative overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 z-0 bg-matrix-gradient-dark" />
      
      {/* Header */}
      <div className="relative z-10 pt-24 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="bg-gradient-to-r from-matrix-green/20 to-matrix-cyan/20 text-matrix-green border-matrix-green/40 font-body animate-scaleIn mb-4">
              🧩 Plugin Marketplace
            </Badge>
            
            <h1 className="text-4xl lg:text-6xl font-bold font-heading leading-tight animate-fadeInUp">
              <span className="matrix-text-bright animate-glow">
                EXTEND_PLATFORM
              </span>
            </h1>
            
            <p className="text-xl text-matrix-green/80 font-body mt-4 animate-fadeInUp" style={{animationDelay: '0.2s'}}>
              Discover and install plugins to enhance your AI agent capabilities
            </p>
          </div>

          {/* Marketplace Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Available Plugins</CardTitle>
                <Package className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{marketplaceData.total_available || 47}</div>
                <p className="text-xs text-matrix-green/60">Ready to install</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Installed</CardTitle>
                <Download className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{availablePlugins.loaded_plugins || 0}</div>
                <p className="text-xs text-matrix-green/60">Active plugins</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Categories</CardTitle>
                <Grid3X3 className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{Object.keys(categories).length || 7}</div>
                <p className="text-xs text-matrix-green/60">Plugin categories</p>
              </CardContent>
            </Card>

            <Card className="modern-card hover-lift">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-matrix-green">Featured</CardTitle>
                <Trending className="h-4 w-4 text-matrix-cyan" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-matrix-bright-cyan">{(marketplaceData.featured_plugins || []).length}</div>
                <p className="text-xs text-matrix-green/60">Top picks</p>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col lg:flex-row gap-4 mb-8">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-matrix-green/60" />
              <input
                type="text"
                placeholder="Search plugins..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-matrix-black/50 border border-matrix-green/20 rounded-lg text-matrix-green placeholder-matrix-green/60 focus:border-matrix-green/60 focus:outline-none font-mono"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 bg-matrix-black/50 border border-matrix-green/20 rounded-lg text-matrix-green focus:border-matrix-green/60 focus:outline-none font-mono"
              >
                <option value="all">All Categories</option>
                {Object.entries(categories).map(([key, description]) => (
                  <option key={key} value={key}>{key.replace('_', ' ').toUpperCase()}</option>
                ))}
              </select>

              <div className="flex border border-matrix-green/20 rounded-lg overflow-hidden">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-3 ${viewMode === 'grid' ? 'bg-matrix-green/20 text-matrix-green' : 'text-matrix-green/60 hover:text-matrix-green'}`}
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-3 ${viewMode === 'list' ? 'bg-matrix-green/20 text-matrix-green' : 'text-matrix-green/60 hover:text-matrix-green'}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              <Button
                onClick={handleCreatePlugin}
                className="btn-matrix hover-lift font-heading"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Plugin
              </Button>
            </div>
          </div>

          {/* Plugin Grid/List */}
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8' : 'space-y-4 mb-8'}>
            {filteredPlugins.map((plugin, index) => (
              <Card key={plugin.id} className="modern-card hover-glow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      {getCategoryIcon(plugin.category)}
                      <div className="flex-1">
                        <CardTitle className="text-matrix-green font-heading">{plugin.name}</CardTitle>
                        <CardDescription className="text-matrix-green/60 text-sm">
                          {plugin.description}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge className={`${getCategoryColor(plugin.category)} font-mono text-xs`}>
                      {plugin.category.replace('_', ' ')}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Plugin Stats */}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Star className="w-3 h-3 text-yellow-400 fill-current" />
                          <span className="text-matrix-green/80">{plugin.rating}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Download className="w-3 h-3 text-matrix-green/60" />
                          <span className="text-matrix-green/80">{plugin.downloads.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Users className="w-3 h-3 text-matrix-green/60" />
                          <span className="text-matrix-green/80">Active</span>
                        </div>
                      </div>
                      <div className="text-matrix-bright-cyan font-mono font-bold">
                        {plugin.price}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        className="flex-1 btn-matrix hover-lift font-heading"
                        onClick={() => handleInstallPlugin(plugin.id)}
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Install
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="border-matrix-green text-matrix-green hover:bg-matrix-green/10"
                      >
                        Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Plugin Development Section */}
          <TerminalWindow title="PLUGIN_DEVELOPMENT_KIT.md" className="mb-8">
            <div className="space-y-2 text-sm font-mono">
              <div className="text-matrix-green animate-glow">
                # Plugin Development Kit (PDK) v2.0
              </div>
              <div className="text-matrix-cyan">
                &gt; Create custom plugins to extend your AI agent platform
              </div>
              <div className="text-matrix-green/80">
                • Support for custom agent capabilities and integrations
              </div>
              <div className="text-matrix-green/80">
                • Plugin marketplace submission and distribution
              </div>
              <div className="text-matrix-green/80">
                • White-label and reseller plugin licensing available
              </div>
              <div className="text-matrix-bright-cyan">
                &gt; Get started: <span className="underline cursor-pointer">Create Plugin Template</span>
              </div>
            </div>
          </TerminalWindow>

          {/* Categories Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(categories).map(([categoryKey, description]) => (
              <Card key={categoryKey} className="modern-card hover-lift cursor-pointer" onClick={() => setSelectedCategory(categoryKey)}>
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    {getCategoryIcon(categoryKey)}
                    <div>
                      <CardTitle className="text-matrix-green font-heading capitalize">
                        {categoryKey.replace('_', ' ')}
                      </CardTitle>
                      <CardDescription className="text-matrix-green/60">
                        {description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-matrix-green/70">
                    {filteredPlugins.filter(p => p.category === categoryKey).length} plugins available
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </MobileMatrixOptimizer>
  );
};

export default PluginMarketplace;