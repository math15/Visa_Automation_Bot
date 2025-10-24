'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import { 
  Users, 
  CheckCircle, 
  XCircle, 
  Clock, 
  RefreshCw, 
  Trash2, 
  Play,
  AlertCircle,
  Edit
} from 'lucide-react';

interface Account {
  id: number;
  // Personal Information
  first_name: string;
  last_name: string;
  family_name?: string;
  date_of_birth: string;
  gender: string;
  marital_status: string;
  
  // Passport Information
  passport_number: string;
  passport_type: string;
  passport_issue_date: string;
  passport_expiry_date: string;
  passport_issue_place?: string;
  passport_issue_country?: string;
  
  // Contact Information
  email: string;
  mobile: string;
  phone_country_code: string;
  
  // Location Information
  birth_country?: string;
  country_of_residence?: string;
  
  // Additional Information
  number_of_members: number;
  relationship: string;
  primary_applicant: boolean;
  
  // Account Credentials
  password: string;
  
  // Account Status
  status: string;
  bls_status: string;
  bls_username?: string;
  bls_created_at?: string;
  bls_error_message?: string;
  is_enabled: boolean;
  created_at: string;
  processing_attempts: number;
  last_processing_attempt?: string;
}

interface AccountStats {
  total_accounts: number;
  created_accounts: number;
  bls_creating: number;
  bls_created: number;
  bls_failed: number;
  bls_not_created: number;
}

export default function AccountManagementPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [stats, setStats] = useState<AccountStats | null>(null);
  const [selectedAccounts, setSelectedAccounts] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    fetchAccounts();
    fetchStats();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/enhanced-bls/accounts/');
      const data = await response.json();
      setAccounts(data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/enhanced-bls/accounts/stats/summary');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };


  const createBLSAccounts = async (accountIds: number[]) => {
    try {
      setCreating(true);
      const response = await fetch('http://localhost:8000/api/enhanced-bls/accounts/create-bls', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ account_ids: accountIds }),
      });

      const result = await response.json();
      
      if (response.ok) {
        addToast({
          type: 'success',
          title: 'BLS Creation Started',
          description: `${result.successful_count} accounts processing, ${result.failed_count} failed`
        });
        await fetchAccounts();
        await fetchStats();
        setSelectedAccounts([]);
      } else {
        addToast({
          type: 'error',
          title: 'BLS Creation Failed',
          description: result.detail || 'Failed to start BLS creation'
        });
      }
    } catch (error) {
      console.error('Error creating BLS accounts:', error);
      addToast({
        type: 'error',
        title: 'BLS Creation Error',
        description: 'Failed to create BLS accounts. Please try again.'
      });
    } finally {
      setCreating(false);
    }
  };

  const retryFailedAccounts = async () => {
    try {
      setCreating(true);
      const response = await fetch('http://localhost:8000/api/enhanced-bls/accounts/retry-failed-bls', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      
      if (response.ok) {
        addToast({
          type: 'success',
          title: 'Retry Started',
          description: `${result.successful_count} accounts retrying, ${result.failed_count} failed`
        });
        await fetchAccounts();
        await fetchStats();
      } else {
        addToast({
          type: 'error',
          title: 'Retry Failed',
          description: result.detail || 'Failed to retry failed accounts'
        });
      }
    } catch (error) {
      console.error('Error retrying failed accounts:', error);
      addToast({
        type: 'error',
        title: 'Retry Error',
        description: 'Failed to retry failed accounts. Please try again.'
      });
    } finally {
      setCreating(false);
    }
  };

  const deleteAccount = async (accountId: number) => {
    if (!confirm('Are you sure you want to delete this account?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/enhanced-bls/accounts/${accountId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        addToast({
          type: 'success',
          title: 'Account Deleted',
          description: 'Account has been successfully deleted'
        });
        await fetchAccounts();
        await fetchStats();
      } else {
        const error = await response.json();
        addToast({
          type: 'error',
          title: 'Delete Failed',
          description: error.detail || 'Failed to delete account'
        });
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      addToast({
        type: 'error',
        title: 'Delete Error',
        description: 'Failed to delete account. Please try again.'
      });
    }
  };

  const editAccount = (accountId: number) => {
    // Find the account to edit
    const account = accounts.find(acc => acc.id === accountId);
    if (!account) {
      addToast({
        type: 'error',
        title: 'Account Not Found',
        description: 'The account you are trying to edit was not found'
      });
      return;
    }

    // Create URL parameters with ALL account data for editing
    const params = new URLSearchParams({
      edit: 'true',
      id: accountId.toString(),
      // Personal Information
      first_name: account.first_name,
      last_name: account.last_name,
      family_name: account.family_name || '',
      date_of_birth: account.date_of_birth,
      gender: account.gender,
      marital_status: account.marital_status,
      
      // Passport Information
      passport_number: account.passport_number,
      passport_type: account.passport_type,
      passport_issue_date: account.passport_issue_date,
      passport_expiry_date: account.passport_expiry_date,
      passport_issue_place: account.passport_issue_place || '',
      passport_issue_country: account.passport_issue_country || '',
      
      // Contact Information
      email: account.email,
      mobile: account.mobile,
      phone_country_code: account.phone_country_code,
      
      // Location Information
      birth_country: account.birth_country || '',
      country_of_residence: account.country_of_residence || '',
      
      // Additional Information
      number_of_members: account.number_of_members.toString(),
      relationship: account.relationship,
      primary_applicant: account.primary_applicant.toString(),
      
      // Account Credentials
      password: account.password,
    });

    // Navigate to create account page with edit parameters
    window.location.href = `/tesla-config/create-account?${params.toString()}`;
  };

  const toggleAccountSelection = (accountId: number) => {
    setSelectedAccounts(prev => 
      prev.includes(accountId) 
        ? prev.filter(id => id !== accountId)
        : [...prev, accountId]
    );
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      created: { color: 'bg-blue-500', text: 'Created' },
      bls_creating: { color: 'bg-yellow-500', text: 'Creating BLS' },
      bls_created: { color: 'bg-green-500', text: 'BLS Created' },
      bls_failed: { color: 'bg-red-500', text: 'BLS Failed' },
      inactive: { color: 'bg-gray-500', text: 'Inactive' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || { color: 'bg-gray-500', text: status };
    return <Badge className={`${config.color} text-white`}>{config.text}</Badge>;
  };

  const getBLSStatusBadge = (blsStatus: string) => {
    const statusConfig = {
      not_created: { color: 'bg-gray-500', text: 'Not Created', icon: Clock },
      creating: { color: 'bg-yellow-500', text: 'Creating', icon: RefreshCw },
      created: { color: 'bg-green-500', text: 'Created', icon: CheckCircle },
      failed: { color: 'bg-red-500', text: 'Failed', icon: XCircle }
    };
    
    const config = statusConfig[blsStatus as keyof typeof statusConfig] || { color: 'bg-gray-500', text: blsStatus, icon: AlertCircle };
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} text-white flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.text}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading accounts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Account Management</h1>
          <p className="text-gray-600">Manage accounts and create BLS accounts</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={() => createBLSAccounts(selectedAccounts)} 
            disabled={selectedAccounts.length === 0 || creating}
            variant="outline"
          >
            <Play className="w-4 h-4 mr-2" />
            Create BLS ({selectedAccounts.length})
          </Button>
          <Button 
            onClick={retryFailedAccounts} 
            disabled={creating}
            variant="outline"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry Failed
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{stats.total_accounts}</div>
              <p className="text-sm text-gray-600">Total Accounts</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">{stats.created_accounts}</div>
              <p className="text-sm text-gray-600">Created</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-yellow-600">{stats.bls_creating}</div>
              <p className="text-sm text-gray-600">Creating BLS</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">{stats.bls_created}</div>
              <p className="text-sm text-gray-600">BLS Created</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-red-600">{stats.bls_failed}</div>
              <p className="text-sm text-gray-600">BLS Failed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-gray-600">{stats.bls_not_created}</div>
              <p className="text-sm text-gray-600">Not Created</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Accounts List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Accounts ({accounts.length})
          </CardTitle>
          <CardDescription>
            Select accounts to create BLS accounts concurrently
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {accounts.map((account) => (
              <div key={account.id} className="border rounded-lg p-4 hover:bg-gray-100 transition-colors duration-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={selectedAccounts.includes(account.id)}
                      onChange={() => toggleAccountSelection(account.id)}
                      className="w-4 h-4"
                    />
                    <div>
                      <div className="font-semibold text-gray-900">
                        {account.first_name} {account.last_name}
                      </div>
                      <div className="text-sm text-gray-700">
                        {account.email} • {account.passport_number}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(account.status)}
                    {getBLSStatusBadge(account.bls_status)}
                    {account.bls_error_message && (
                      <Badge variant="destructive" className="text-xs">
                        Error
                      </Badge>
                    )}
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => createBLSAccounts([account.id])}
                        disabled={account.bls_status !== 'not_created' || creating}
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => editAccount(account.id)}
                        title="Edit Account"
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deleteAccount(account.id)}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </div>
                {account.bls_error_message && (
                  <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                    {account.bls_error_message}
                  </div>
                )}
                {account.processing_attempts > 0 && (
                  <div className="mt-2 text-xs text-gray-500">
                    Processing attempts: {account.processing_attempts}
                    {account.last_processing_attempt && (
                      <span> • Last attempt: {new Date(account.last_processing_attempt).toLocaleString()}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}