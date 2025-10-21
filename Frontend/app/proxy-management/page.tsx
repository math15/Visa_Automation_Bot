'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Globe, 
  Plus, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Loader2,
  RefreshCw,
  Shield,
  MapPin
} from 'lucide-react';

interface Proxy {
  id: number;
  host: string;
  port: number;
  username?: string;
  password?: string;
  country: string;
  is_active: boolean;
  validation_status: string;
}

interface ProxyFormData {
  host: string;
  port: string;
  username: string;
  password: string;
  country: string;
}

export default function ProxyManagementPage() {
  const [proxies, setProxies] = useState<Proxy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showBulkImport, setShowBulkImport] = useState(false);
  const [bulkProxies, setBulkProxies] = useState('');
  const [formData, setFormData] = useState<ProxyFormData>({
    host: '',
    port: '',
    username: '',
    password: '',
    country: 'DZ'
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  // Load proxies on component mount
  useEffect(() => {
    loadProxies();
  }, []);

  const parseBulkProxies = (text: string) => {
    console.log('🔍 Parsing bulk proxies text:', text);
    const lines = text.split('\n').filter(line => line.trim());
    console.log('📝 Lines after split:', lines);
    const parsedProxies = [];
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      console.log('🔍 Processing line:', trimmedLine);
      
      // Skip empty lines and comments
      if (!trimmedLine || trimmedLine.startsWith('#')) {
        console.log('⏭️ Skipping line (empty or comment):', trimmedLine);
        continue;
      }
      
      // Parse different formats:
      // Format 1: host:port
      // Format 2: host:port:username:password
      // Format 3: username:password@host:port
      // Format 4: host:port@username:password
      
      let host, port, username, password, country = 'DZ'; // Default to Algeria
      
      if (trimmedLine.includes('@')) {
        // Format: username:password@host:port or host:port@username:password
        const [authPart, hostPart] = trimmedLine.split('@');
        console.log('🔍 Auth format detected:', { authPart, hostPart });
        
        // Check if authPart looks like host:port (contains numbers) or username:password
        if (authPart.includes(':') && /:\d+$/.test(authPart)) {
          // host:port@username:password (your format)
          [host, port] = authPart.split(':');
          [username, password] = hostPart.split(':');
          console.log('🔍 Detected host:port@username:password format');
        } else {
          // username:password@host:port
          [username, password] = authPart.split(':');
          [host, port] = hostPart.split(':');
          console.log('🔍 Detected username:password@host:port format');
        }
        
        // Extract country from username if it contains country code (e.g., __cr.es)
        if (username && username.includes('__cr.')) {
          const countryMatch = username.match(/__cr\.(\w+)/);
          if (countryMatch) {
            const countryCode = countryMatch[1].toUpperCase();
            // Map common country codes
            const countryMap: {[key: string]: string} = {
              'ES': 'ES', 'US': 'US', 'GB': 'GB', 'FR': 'FR', 'DE': 'DE',
              'IT': 'IT', 'CA': 'CA', 'AU': 'AU', 'JP': 'JP', 'DZ': 'DZ'
            };
            country = countryMap[countryCode] || 'DZ';
          }
        }
      } else {
        // Format: host:port or host:port:username:password
        const parts = trimmedLine.split(':');
        console.log('🔍 Colon format detected:', parts);
        if (parts.length >= 2) {
          host = parts[0];
          port = parts[1];
          if (parts.length >= 4) {
            username = parts[2];
            password = parts[3];
          }
        }
      }
      
      console.log('🔍 Parsed values:', { host, port, username, password });
      
      if (host && port && /^\d+$/.test(port)) {
        const proxy = {
          host: host.trim(),
          port: parseInt(port.trim()),
          username: username?.trim() || '',
          password: password?.trim() || '',
          country: country || 'DZ' // Use extracted country or default to Algeria
        };
        console.log('✅ Valid proxy found:', proxy);
        parsedProxies.push(proxy);
      } else {
        console.log('❌ Invalid proxy format:', { host, port });
      }
    }
    
    console.log('📋 Final parsed proxies:', parsedProxies);
    return parsedProxies;
  };

  const handleBulkImport = async () => {
    console.log('🔍 Bulk import started');
    console.log('📝 Bulk proxies text:', bulkProxies);
    
    if (!bulkProxies.trim()) {
      setMessage({type: 'error', text: 'Please enter proxy data'});
      return;
    }
    
    try {
      setIsAdding(true);
      setMessage(null);
      
      const parsedProxies = parseBulkProxies(bulkProxies);
      console.log('📋 Parsed proxies:', parsedProxies);
      
      if (parsedProxies.length === 0) {
        setMessage({type: 'error', text: 'No valid proxies found in the text'});
        return;
      }
      
      let successCount = 0;
      let errorCount = 0;
      const errors = [];
      
      console.log(`🚀 Starting to add ${parsedProxies.length} proxies`);
      
      // Add each proxy
      for (const proxy of parsedProxies) {
        console.log(`📤 Adding proxy: ${proxy.host}:${proxy.port}`);
        try {
          const response = await fetch('http://localhost:8000/api/proxies/add', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              host: proxy.host,
              port: proxy.port,
              username: proxy.username || null,
              password: proxy.password || null,
              country: proxy.country
            }),
          });
          
          console.log(`📊 Response for ${proxy.host}:${proxy.port}:`, response.status);
          
          if (response.ok) {
            successCount++;
            console.log(`✅ Success: ${proxy.host}:${proxy.port}`);
          } else {
            const errorData = await response.json();
            console.log(`❌ Error for ${proxy.host}:${proxy.port}:`, errorData);
            errors.push(`${proxy.host}:${proxy.port} - ${errorData.detail}`);
            errorCount++;
          }
        } catch (error) {
          console.log(`🌐 Network error for ${proxy.host}:${proxy.port}:`, error);
          errors.push(`${proxy.host}:${proxy.port} - Network error`);
          errorCount++;
        }
      }
      
      console.log(`📈 Final results: ${successCount} success, ${errorCount} errors`);
      
      if (successCount > 0) {
        setMessage({
          type: 'success', 
          text: `Successfully added ${successCount} proxy(ies). ${errorCount > 0 ? `${errorCount} failed.` : ''}`
        });
        
        // Reset form
        setBulkProxies('');
        setShowBulkImport(false);
        
        // Reload proxies
        await loadProxies();
      } else {
        setMessage({type: 'error', text: `Failed to add all proxies. Errors: ${errors.join(', ')}`});
      }
      
    } catch (error) {
      console.error('💥 Error in bulk import:', error);
      setMessage({type: 'error', text: 'Failed to import proxies'});
    } finally {
      setIsAdding(false);
    }
  };

  const loadProxies = async () => {
    try {
      setIsLoading(true);
      console.log('🔄 Loading proxies from backend...');
      const response = await fetch('http://localhost:8000/api/proxies/');
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`Failed to load proxies: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      console.log('📦 Response data:', data);
      
      // Handle both formats: direct array or wrapped object
      let proxiesArray = [];
      if (Array.isArray(data)) {
        // Direct array format: [{...}, {...}, ...]
        proxiesArray = data;
        console.log('📦 Direct array format detected');
      } else if (data.proxies && Array.isArray(data.proxies)) {
        // Wrapped format: {success: true, proxies: [...]}
        proxiesArray = data.proxies;
        console.log('📦 Wrapped format detected');
      } else {
        console.warn('⚠️ Unknown response format:', data);
        proxiesArray = [];
      }
      
      console.log('📦 Proxies array:', proxiesArray);
      console.log('📦 Proxies length:', proxiesArray.length);
      
      setProxies(proxiesArray);
      
    } catch (error) {
      console.error('💥 Error loading proxies:', error);
      setMessage({type: 'error', text: `Failed to load proxies: ${error.message}`});
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};
    
    if (!formData.host.trim()) {
      newErrors.host = 'Host is required';
    }
    
    if (!formData.port.trim()) {
      newErrors.port = 'Port is required';
    } else if (!/^\d+$/.test(formData.port)) {
      newErrors.port = 'Port must be a number';
    } else {
      const portNum = parseInt(formData.port);
      if (portNum < 1 || portNum > 65535) {
        newErrors.port = 'Port must be between 1 and 65535';
      }
    }
    
    if (!formData.country.trim()) {
      newErrors.country = 'Country is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof ProxyFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleAddProxy = async () => {
    if (!validateForm()) {
      return;
    }
    
    try {
      setIsAdding(true);
      setMessage(null);
      
      const response = await fetch('http://localhost:8000/api/proxies/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          host: formData.host.trim(),
          port: parseInt(formData.port),
          username: formData.username.trim() || null,
          password: formData.password.trim() || null,
          country: formData.country.trim()
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add proxy');
      }
      
      const result = await response.json();
      setMessage({type: 'success', text: result.message});
      
      // Reset form
      setFormData({
        host: '',
        port: '',
        username: '',
        password: '',
        country: 'DZ'
      });
      setShowAddForm(false);
      
      // Reload proxies
      await loadProxies();
      
    } catch (error) {
      console.error('Error adding proxy:', error);
      setMessage({type: 'error', text: error instanceof Error ? error.message : 'Failed to add proxy'});
    } finally {
      setIsAdding(false);
    }
  };

  const getStatusBadge = (proxy: Proxy) => {
    if (!proxy.is_active) {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Inactive</Badge>;
    }
    
    switch (proxy.validation_status) {
      case 'validated':
        return <Badge variant="default" className="bg-green-100 text-green-800">Validated</Badge>;
      case 'failed':
        return <Badge variant="destructive" className="bg-red-100 text-red-800">Failed</Badge>;
      case 'pending':
        return <Badge variant="outline" className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      default:
        return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Unknown</Badge>;
    }
  };

  const getCountryFlag = (country: string) => {
    const flags: {[key: string]: string} = {
      'DZ': '🇩🇿',
      'US': '🇺🇸',
      'GB': '🇬🇧',
      'FR': '🇫🇷',
      'DE': '🇩🇪',
      'ES': '🇪🇸',
      'IT': '🇮🇹',
      'CA': '🇨🇦',
      'AU': '🇦🇺',
      'JP': '🇯🇵'
    };
    return flags[country] || '🌍';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Proxy Management</h1>
          <p className="text-gray-600">
            Manage Algerian proxies for BLS website access. Proxies are automatically used for account creation.
          </p>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success' 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            {message.text}
          </div>
        )}

        {/* Add Proxy Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Add New Proxy
            </CardTitle>
            <CardDescription>
              Add Algerian proxies to enable BLS website access. Proxies are automatically validated.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!showAddForm && !showBulkImport ? (
              <div className="flex gap-2">
                <Button onClick={() => setShowAddForm(true)} className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add Single Proxy
                </Button>
                <Button onClick={() => setShowBulkImport(true)} variant="outline" className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  Bulk Import Proxies
                </Button>
              </div>
            ) : showAddForm ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="host">Host *</Label>
                    <Input
                      id="host"
                      value={formData.host}
                      onChange={(e) => handleInputChange('host', e.target.value)}
                      placeholder="proxy.example.com"
                      className={errors.host ? 'border-red-500' : ''}
                    />
                    {errors.host && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.host}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="port">Port *</Label>
                    <Input
                      id="port"
                      value={formData.port}
                      onChange={(e) => handleInputChange('port', e.target.value)}
                      placeholder="8080"
                      className={errors.port ? 'border-red-500' : ''}
                    />
                    {errors.port && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.port}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="username">Username (Optional)</Label>
                    <Input
                      id="username"
                      value={formData.username}
                      onChange={(e) => handleInputChange('username', e.target.value)}
                      placeholder="proxy_user"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password (Optional)</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      placeholder="proxy_pass"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="country">Country *</Label>
                    <select
                      id="country"
                      value={formData.country}
                      onChange={(e) => handleInputChange('country', e.target.value)}
                      className="w-full px-3 py-2 border border-input bg-background rounded-md"
                    >
                      <option value="DZ">🇩🇿 Algeria (DZ)</option>
                      <option value="US">🇺🇸 United States (US)</option>
                      <option value="GB">🇬🇧 United Kingdom (GB)</option>
                      <option value="FR">🇫🇷 France (FR)</option>
                      <option value="DE">🇩🇪 Germany (DE)</option>
                      <option value="ES">🇪🇸 Spain (ES)</option>
                      <option value="IT">🇮🇹 Italy (IT)</option>
                      <option value="CA">🇨🇦 Canada (CA)</option>
                      <option value="AU">🇦🇺 Australia (AU)</option>
                      <option value="JP">🇯🇵 Japan (JP)</option>
                    </select>
                    {errors.country && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.country}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={handleAddProxy} 
                    disabled={isAdding}
                    className="flex items-center gap-2"
                  >
                    {isAdding ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Plus className="h-4 w-4" />
                    )}
                    {isAdding ? 'Adding...' : 'Add Proxy'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setShowAddForm(false)}
                    disabled={isAdding}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : showBulkImport ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="bulkProxies">Paste Multiple Proxies</Label>
                  <textarea
                    id="bulkProxies"
                    value={bulkProxies}
                    onChange={(e) => setBulkProxies(e.target.value)}
                    placeholder={`# Paste your proxies here, one per line
# Supported formats:
# host:port
# host:port:username:password
# username:password@host:port
# host:port@username:password

proxy1.example.com:8080
proxy2.example.com:3128:user:pass
user:pass@proxy3.example.com:8080
proxy4.example.com:8080@user:pass`}
                    className="w-full px-3 py-2 border border-input bg-background rounded-md min-h-[200px] font-mono text-sm"
                  />
                  <p className="text-xs text-gray-500">
                    Supports multiple formats. Lines starting with # are comments and will be ignored.
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={handleBulkImport} 
                    disabled={isAdding}
                    className="flex items-center gap-2"
                  >
                    {isAdding ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Globe className="h-4 w-4" />
                    )}
                    {isAdding ? 'Importing...' : 'Import Proxies'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setShowBulkImport(false)}
                    disabled={isAdding}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>

        {/* Proxies List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Proxies ({proxies.length})
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={loadProxies}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </CardTitle>
            <CardDescription>
              Manage your proxy list. Algerian proxies (DZ) are automatically used for BLS access.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-500">Loading proxies...</span>
              </div>
            ) : proxies.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Globe className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">No proxies found</p>
                <p className="text-sm">Add your first proxy to get started with BLS automation.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {proxies.map((proxy) => (
                  <div 
                    key={proxy.id} 
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-gray-400" />
                        <span className="text-lg">{getCountryFlag(proxy.country)}</span>
                        <span className="font-medium">{proxy.country}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-gray-400" />
                        <span className="font-mono text-sm">
                          {proxy.host}:{proxy.port}
                        </span>
                        {proxy.username && (
                          <span className="text-xs text-gray-500">
                            ({proxy.username})
                          </span>
                        )}
                      </div>
                      
                      {getStatusBadge(proxy)}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {proxy.is_active ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Proxy Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">🇩🇿 Algerian Proxies (DZ)</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• Required for BLS website access</li>
                  <li>• Automatically selected for account creation</li>
                  <li>• Validated before use</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">🌍 Other Countries</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• Available for future features</li>
                  <li>• Can be used for testing</li>
                  <li>• Not used for BLS automation</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}