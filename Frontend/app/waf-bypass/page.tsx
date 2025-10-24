'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, Globe, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

interface WAFTestResult {
  url: string;
  status: 'success' | 'error' | 'pending';
  statusCode?: number;
  contentLength?: number;
  solveTime?: number;
  token?: string;
  error?: string;
}

export default function WAFBypassPage() {
  const [testUrl, setTestUrl] = useState('https://algeria.blsspainglobal.com');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<WAFTestResult[]>([]);

  const API_BASE = 'http://localhost:8000/api';

  const testWAFBypass = async () => {
    if (!testUrl.trim()) return;

    setIsLoading(true);
    const newResult: WAFTestResult = {
      url: testUrl,
      status: 'pending'
    };
    setResults(prev => [newResult, ...prev]);

    try {
      const response = await fetch(`${API_BASE}/waf-bypass/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testUrl })
      });

      const data = await response.json();
      
      if (response.ok) {
        setResults(prev => prev.map(r => 
          r.url === testUrl && r.status === 'pending' 
            ? { ...r, status: 'success', ...data }
            : r
        ));
      } else {
        setResults(prev => prev.map(r => 
          r.url === testUrl && r.status === 'pending' 
            ? { ...r, status: 'error', error: data.detail || 'Test failed' }
            : r
        ));
      }
    } catch (error) {
      setResults(prev => prev.map(r => 
        r.url === testUrl && r.status === 'pending' 
          ? { ...r, status: 'error', error: 'Network error' }
          : r
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="default" className="bg-green-500">Success</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'pending':
        return <Badge variant="secondary">Testing...</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            AWS WAF Bypass Tools
          </h1>
          <p className="text-muted-foreground">
            Test and manage AWS WAF bypass capabilities with advanced challenge solving
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              WAF Bypass Test
            </CardTitle>
            <CardDescription>
              Test AWS WAF bypass functionality against target URLs
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="test-url">Target URL</Label>
              <Input
                id="test-url"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                placeholder="https://example.com"
              />
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={testWAFBypass} 
                disabled={isLoading || !testUrl.trim()}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Test WAF Bypass
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={clearResults}>
                Clear Results
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Tests */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Tests</CardTitle>
            <CardDescription>
              Test against known AWS WAF protected sites
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                setTestUrl('https://algeria.blsspainglobal.com');
                testWAFBypass();
              }}
              disabled={isLoading}
            >
              <Globe className="h-4 w-4 mr-2" />
              BLS Spain Website
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                setTestUrl('https://www.binance.com');
                testWAFBypass();
              }}
              disabled={isLoading}
            >
              <Globe className="h-4 w-4 mr-2" />
              Binance (Known Working)
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                setTestUrl('https://httpbin.org/get');
                testWAFBypass();
              }}
              disabled={isLoading}
            >
              <Globe className="h-4 w-4 mr-2" />
              HTTPBin Test
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <CardDescription>
              AWS WAF bypass test results and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(result.status)}
                      <span className="font-medium">{result.url}</span>
                    </div>
                    {getStatusBadge(result.status)}
                  </div>
                  
                  {result.status === 'success' && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Status Code:</span>
                        <div className="font-medium">{result.statusCode}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Content Length:</span>
                        <div className="font-medium">{result.contentLength?.toLocaleString()} bytes</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Solve Time:</span>
                        <div className="font-medium">{result.solveTime?.toFixed(2)}s</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Token:</span>
                        <div className="font-medium text-xs truncate">
                          {result.token ? `${result.token.substring(0, 20)}...` : 'N/A'}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {result.status === 'error' && (
                    <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      <strong>Error:</strong> {result.error}
                    </div>
                  )}
                  
                  {result.status === 'pending' && (
                    <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
                      Testing AWS WAF bypass...
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {results.filter(r => r.status === 'success').length}
                </div>
                <div className="text-sm text-muted-foreground">Successful Tests</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <div>
                <div className="text-2xl font-bold">
                  {results.filter(r => r.status === 'error').length}
                </div>
                <div className="text-sm text-muted-foreground">Failed Tests</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">
                  {results.length > 0 ? (results.filter(r => r.status === 'success').length / results.length * 100).toFixed(1) : 0}%
                </div>
                <div className="text-sm text-muted-foreground">Success Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
