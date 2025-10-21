'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Globe, 
  CheckCircle, 
  XCircle, 
  Loader2, 
  ExternalLink,
  Wifi,
  WifiOff
} from 'lucide-react';

export default function BLSTestPage() {
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [proxyConfig, setProxyConfig] = useState({
    host: '',
    port: '',
    username: '',
    password: ''
  });

  const testConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    
    try {
      const params = new URLSearchParams();
      if (proxyConfig.host) params.append('proxy_host', proxyConfig.host);
      if (proxyConfig.port) params.append('proxy_port', proxyConfig.port);
      if (proxyConfig.username) params.append('proxy_username', proxyConfig.username);
      if (proxyConfig.password) params.append('proxy_password', proxyConfig.password);
      
      const response = await fetch(`http://localhost:8000/api/bls-website/test-connection?${params}`);
      const result = await response.json();
      
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: `Error: ${error}`,
        url: 'https://algeria.blsspainglobal.com/'
      });
    } finally {
      setIsTesting(false);
    }
  };

  const testRegistrationPage = async () => {
    setIsTesting(true);
    setTestResult(null);
    
    try {
      const params = new URLSearchParams();
      if (proxyConfig.host) params.append('proxy_host', proxyConfig.host);
      if (proxyConfig.port) params.append('proxy_port', proxyConfig.port);
      if (proxyConfig.username) params.append('proxy_username', proxyConfig.username);
      if (proxyConfig.password) params.append('proxy_password', proxyConfig.password);
      
      const response = await fetch(`http://localhost:8000/api/bls-website/registration-page?${params}`);
      const result = await response.json();
      
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: `Error: ${error}`,
        url: 'https://algeria.blsspainglobal.com/register'
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">BLS Website Test</h1>
        <p className="text-muted-foreground">
          Test connection and functionality with the actual BLS Algeria website
        </p>
        <div className="mt-2">
          <Badge variant="outline" className="text-xs">
            🌐 Target: https://algeria.blsspainglobal.com/
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Proxy Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Proxy Configuration (Optional)
            </CardTitle>
            <CardDescription>
              Configure proxy settings for testing with Algerian IP
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="proxy_host">Proxy Host</Label>
                <Input
                  id="proxy_host"
                  value={proxyConfig.host}
                  onChange={(e) => setProxyConfig(prev => ({ ...prev, host: e.target.value }))}
                  placeholder="proxy.example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="proxy_port">Port</Label>
                <Input
                  id="proxy_port"
                  value={proxyConfig.port}
                  onChange={(e) => setProxyConfig(prev => ({ ...prev, port: e.target.value }))}
                  placeholder="8080"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="proxy_username">Username</Label>
                <Input
                  id="proxy_username"
                  value={proxyConfig.username}
                  onChange={(e) => setProxyConfig(prev => ({ ...prev, username: e.target.value }))}
                  placeholder="username"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="proxy_password">Password</Label>
                <Input
                  id="proxy_password"
                  type="password"
                  value={proxyConfig.password}
                  onChange={(e) => setProxyConfig(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="password"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Test Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wifi className="h-5 w-5" />
              Test Actions
            </CardTitle>
            <CardDescription>
              Test different aspects of the BLS website
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <Button
                onClick={testConnection}
                disabled={isTesting}
                className="w-full"
                variant="outline"
              >
                {isTesting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Testing Connection...
                  </>
                ) : (
                  <>
                    <Wifi className="h-4 w-4 mr-2" />
                    Test Connection
                  </>
                )}
              </Button>
              
              <Button
                onClick={testRegistrationPage}
                disabled={isTesting}
                className="w-full"
                variant="outline"
              >
                {isTesting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Testing Registration Page...
                  </>
                ) : (
                  <>
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Test Registration Page
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Test Results */}
      {testResult && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {testResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              Test Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant={testResult.success ? "default" : "destructive"}>
                  {testResult.success ? "SUCCESS" : "FAILED"}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {testResult.url}
                </span>
              </div>
              
              <div className="bg-muted p-4 rounded-lg">
                <p className="text-sm font-medium mb-2">Response:</p>
                <p className="text-sm text-muted-foreground">{testResult.message}</p>
              </div>
              
              {testResult.content_length && (
                <div className="text-sm text-muted-foreground">
                  Content Length: {testResult.content_length} characters
                </div>
              )}
              
              {testResult.form_fields && (
                <div className="text-sm text-muted-foreground">
                  Form Fields Found: {Object.keys(testResult.form_fields).length}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Information */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>About BLS Algeria</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>• <strong>Website:</strong> https://algeria.blsspainglobal.com/</p>
            <p>• <strong>Registration:</strong> https://algeria.blsspainglobal.com/register</p>
            <p>• <strong>Purpose:</strong> Visa appointment booking for Spanish consulate in Algeria</p>
            <p>• <strong>Requirements:</strong> Algerian IP address, valid passport, mobile number</p>
            <p>• <strong>Validation:</strong> Mobile numbers cannot start with 0, passport format: 2 letters + 7+ digits</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
