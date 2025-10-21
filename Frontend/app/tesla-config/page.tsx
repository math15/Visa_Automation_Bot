'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Edit, Trash2, Settings, Globe, Shield, Key } from 'lucide-react';

interface TeslaConfig {
  id: number;
  name: string;
  description?: string;
  api_key?: string;
  base_url?: string;
  is_active: boolean;
  bls_website_url: string;
  proxy_enabled: boolean;
  captcha_service_url: string;
  aws_waf_bypass_enabled: boolean;
  max_retry_attempts: number;
  request_timeout: number;
  user_agent: string;
  created_at: string;
  updated_at: string;
}

export default function TeslaConfigPage() {
  const [configs, setConfigs] = useState<TeslaConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState<TeslaConfig | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<TeslaConfig>>({
    name: '',
    description: '',
    api_key: '',
    base_url: '',
    is_active: true,
    bls_website_url: 'https://algeria.blsspainglobal.com',
    proxy_enabled: true,
    captcha_service_url: 'https://api.nocaptcha.io',
    aws_waf_bypass_enabled: true,
    max_retry_attempts: 3,
    request_timeout: 30,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });

  const API_BASE = 'http://localhost:8000/api';

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await fetch(`${API_BASE}/tesla-configs/`);
      const data = await response.json();
      setConfigs(Array.isArray(data) ? data : [data]);
    } catch (error) {
      console.error('Failed to fetch configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingConfig) {
        // Update existing config
        await fetch(`${API_BASE}/tesla-configs/${editingConfig.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      } else {
        // Create new config
        await fetch(`${API_BASE}/tesla-configs/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      }
      await fetchConfigs();
      setShowForm(false);
      setEditingConfig(null);
      setFormData({
        name: '',
        description: '',
        api_key: '',
        base_url: '',
        is_active: true,
        bls_website_url: 'https://algeria.blsspainglobal.com',
        proxy_enabled: true,
        captcha_service_url: 'https://api.nocaptcha.io',
        aws_waf_bypass_enabled: true,
        max_retry_attempts: 3,
        request_timeout: 30,
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      });
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  };

  const handleEdit = (config: TeslaConfig) => {
    setEditingConfig(config);
    setFormData(config);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this configuration?')) {
      try {
        await fetch(`${API_BASE}/tesla-configs/${id}`, { method: 'DELETE' });
        await fetchConfigs();
      } catch (error) {
        console.error('Failed to delete config:', error);
      }
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingConfig(null);
    setFormData({
      name: '',
      description: '',
      api_key: '',
      base_url: '',
      is_active: true,
      bls_website_url: 'https://algeria.blsspainglobal.com',
      proxy_enabled: true,
      captcha_service_url: 'https://api.nocaptcha.io',
      aws_waf_bypass_enabled: true,
      max_retry_attempts: 3,
      request_timeout: 30,
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading Tesla configurations...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tesla Configuration Management</h1>
          <p className="text-muted-foreground">
            Manage Tesla automation configurations with AWS WAF bypass capabilities
          </p>
        </div>
        <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Configuration
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingConfig ? 'Edit Configuration' : 'Add New Configuration'}</CardTitle>
            <CardDescription>
              Configure Tesla automation settings including AWS WAF bypass and proxy settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Configuration Name *</Label>
                  <Input
                    id="name"
                    value={formData.name || ''}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Production Config"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="api_key">API Key</Label>
                  <Input
                    id="api_key"
                    value={formData.api_key || ''}
                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                    placeholder="Your API key"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Configuration description..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bls_website_url">BLS Website URL</Label>
                  <Input
                    id="bls_website_url"
                    value={formData.bls_website_url || ''}
                    onChange={(e) => setFormData({ ...formData, bls_website_url: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="captcha_service_url">Captcha Service URL</Label>
                  <Input
                    id="captcha_service_url"
                    value={formData.captcha_service_url || ''}
                    onChange={(e) => setFormData({ ...formData, captcha_service_url: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="max_retry_attempts">Max Retry Attempts</Label>
                  <Input
                    id="max_retry_attempts"
                    type="number"
                    value={formData.max_retry_attempts || 3}
                    onChange={(e) => setFormData({ ...formData, max_retry_attempts: parseInt(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="request_timeout">Request Timeout (seconds)</Label>
                  <Input
                    id="request_timeout"
                    type="number"
                    value={formData.request_timeout || 30}
                    onChange={(e) => setFormData({ ...formData, request_timeout: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_active"
                    checked={formData.is_active || false}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                  />
                  <Label htmlFor="is_active">Active Configuration</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="proxy_enabled"
                    checked={formData.proxy_enabled || false}
                    onCheckedChange={(checked) => setFormData({ ...formData, proxy_enabled: checked })}
                  />
                  <Label htmlFor="proxy_enabled">Enable Proxy</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="aws_waf_bypass_enabled"
                    checked={formData.aws_waf_bypass_enabled || false}
                    onCheckedChange={(checked) => setFormData({ ...formData, aws_waf_bypass_enabled: checked })}
                  />
                  <Label htmlFor="aws_waf_bypass_enabled">Enable AWS WAF Bypass</Label>
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  {editingConfig ? 'Update Configuration' : 'Create Configuration'}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {configs.map((config) => (
          <Card key={config.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  <CardTitle>{config.name}</CardTitle>
                  <Badge variant={config.is_active ? 'default' : 'secondary'}>
                    {config.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleEdit(config)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDelete(config.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              {config.description && (
                <CardDescription>{config.description}</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    <span className="text-sm font-medium">BLS Website</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{config.bls_website_url}</p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm font-medium">AWS WAF Bypass</span>
                  </div>
                  <Badge variant={config.aws_waf_bypass_enabled ? 'default' : 'secondary'}>
                    {config.aws_waf_bypass_enabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Key className="h-4 w-4" />
                    <span className="text-sm font-medium">API Key</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {config.api_key ? `${config.api_key.substring(0, 8)}...` : 'Not set'}
                  </p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Created: {new Date(config.created_at).toLocaleDateString()}</span>
                  <span>Updated: {new Date(config.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {configs.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Settings className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No configurations found</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first Tesla configuration to get started with automation
            </p>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Configuration
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
