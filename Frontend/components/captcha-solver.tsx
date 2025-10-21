'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  RefreshCw
} from 'lucide-react';

interface CaptchaSolverProps {
  captchaId: string;
  onSolved: (solution: string) => void;
  onClose: () => void;
}

export default function CaptchaSolver({ captchaId, onSolved, onClose }: CaptchaSolverProps) {
  const [captchaData, setCaptchaData] = useState<any>(null);
  const [solution, setSolution] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    loadCaptchaData();
  }, [captchaId]);

  const loadCaptchaData = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch(`http://localhost:8000/api/enhanced-bls/get-captcha-data/${captchaId}`);
      if (!response.ok) {
        throw new Error('Failed to load captcha data');
      }
      
      const data = await response.json();
      setCaptchaData(data);
      setStatus('Captcha data loaded successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load captcha data');
    } finally {
      setIsLoading(false);
    }
  };

  const openCaptchaWindow = () => {
    if (!captchaData) return;
    
    try {
      setStatus('Opening captcha window...');
      
      // Open captcha directly without proxy
      const captchaUrl = `https://algeria.blsspainglobal.com/dza/CaptchaPublic/GenerateCaptcha?data=${captchaData.data}`;
      
      // Open small popup window
      const popup = window.open(
        captchaUrl,
        'captchaWindow',
        'width=400,height=600,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
      );
      
      if (!popup) {
        throw new Error('Popup blocked! Please allow popups for this site.');
      }
      
      // Focus the popup
      popup.focus();
      
      setStatus('Captcha opened in small window! Solve it there, then enter your answer below.');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open captcha window');
    }
  };

  const handleSubmit = async () => {
    if (!solution.trim()) {
      setError('Please enter the captcha solution');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      
      const response = await fetch('http://localhost:8000/api/enhanced-bls/captcha-solution', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          captcha_id: captchaId,
          solution: solution.trim()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit captcha solution');
      }

      const result = await response.json();
      if (result.success) {
        setStatus('Captcha solved successfully!');
        onSolved(solution.trim());
        setTimeout(() => onClose(), 1000);
      } else {
        setError(result.message || 'Failed to solve captcha');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit solution');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-96">
          <CardContent className="p-6">
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Loading captcha...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-96 max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Captcha Solver
          </CardTitle>
          <CardDescription>
            Solve the captcha to continue with account creation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Instructions */}
          <div className="space-y-2">
            <h4 className="font-medium">Instructions:</h4>
            <ol className="text-sm text-muted-foreground space-y-1">
              <li>1. Click "Open Captcha" to open the captcha in a small window</li>
              <li>2. Solve the captcha in the popup window</li>
              <li>3. Enter your answer in the field below</li>
              <li>4. Click "Submit Solution"</li>
            </ol>
          </div>

          {/* Status */}
          {status && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-700">{status}</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                {error}
              </p>
            </div>
          )}

          {/* Captcha Info */}
          {captchaData && (
            <div className="p-3 bg-gray-50 border rounded-md">
              <p className="text-xs text-gray-600">
                <strong>Captcha ID:</strong> {captchaId}
              </p>
              <p className="text-xs text-gray-600">
                <strong>Data:</strong> {captchaData.data ? captchaData.data.substring(0, 20) + '...' : 'Not available'}
              </p>
              <p className="text-xs text-gray-600">
                <strong>Direct URL:</strong> Will open BLS captcha directly
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={openCaptchaWindow}
              className="w-full"
              disabled={!captchaData}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Open Captcha (Small Window)
            </Button>

            <div className="space-y-2">
              <Label htmlFor="solution">Captcha Solution</Label>
              <Input
                id="solution"
                value={solution}
                onChange={(e) => setSolution(e.target.value)}
                placeholder="Enter the captcha answer"
                className="w-full"
              />
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting || !solution.trim()}
                className="flex-1"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Submit Solution
                  </>
                )}
              </Button>
              
              <Button
                onClick={onClose}
                variant="outline"
              >
                Cancel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
