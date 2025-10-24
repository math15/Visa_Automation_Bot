'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye,
  EyeOff,
  RefreshCw,
  Download,
  Upload
} from 'lucide-react';

interface TeslaAccount {
  id: number;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  passport_number: string;
  phone: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  created_at: string;
  last_login?: string;
  appointments_count: number;
  success_rate: number;
  notes?: string;
}

export default function TeslaAccountsPage() {
  const [accounts, setAccounts] = useState<TeslaAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingAccount, setEditingAccount] = useState<TeslaAccount | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showPassword, setShowPassword] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    passport_number: '',
    phone: '',
    status: 'pending' as TeslaAccount['status'],
    notes: ''
  });
  const [bulkImport, setBulkImport] = useState('');
  const [runningAccounts, setRunningAccounts] = useState<number[]>([]);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      // Mock data for now - replace with actual API call
      const mockAccounts: TeslaAccount[] = [
        {
          id: 1,
          email: 'user1@example.com',
          password: 'password123',
          first_name: 'Ahmed',
          last_name: 'Benali',
          passport_number: 'A1234567',
          phone: '+213123456789',
          status: 'active',
          created_at: '2025-01-15T10:00:00Z',
          last_login: '2025-01-19T14:30:00Z',
          appointments_count: 3,
          success_rate: 85.5,
          notes: 'VIP customer'
        },
        {
          id: 2,
          email: 'user2@example.com',
          password: 'password456',
          first_name: 'Fatima',
          last_name: 'Zohra',
          passport_number: 'B7654321',
          phone: '+213987654321',
          status: 'pending',
          created_at: '2025-01-18T09:15:00Z',
          appointments_count: 0,
          success_rate: 0,
          notes: 'New account'
        }
      ];
      setAccounts(mockAccounts);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Mock implementation - replace with actual API call
      const newAccount: TeslaAccount = {
        id: Date.now(),
        ...formData,
        created_at: new Date().toISOString(),
        appointments_count: 0,
        success_rate: 0
      };
      
      if (editingAccount) {
        setAccounts(prev => prev.map(acc => acc.id === editingAccount.id ? { ...acc, ...formData } : acc));
      } else {
        setAccounts(prev => [newAccount, ...prev]);
      }
      
      setShowForm(false);
      setEditingAccount(null);
      resetForm();
    } catch (error) {
      console.error('Failed to save account:', error);
    }
  };

  const handleEdit = (account: TeslaAccount) => {
    setEditingAccount(account);
    setFormData({
      email: account.email,
      password: account.password,
      first_name: account.first_name,
      last_name: account.last_name,
      passport_number: account.passport_number,
      phone: account.phone,
      status: account.status,
      notes: account.notes || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this account?')) {
      setAccounts(prev => prev.filter(acc => acc.id !== id));
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      passport_number: '',
      phone: '',
      status: 'pending' as TeslaAccount['status'],
      notes: ''
    });
  };

  const handleBulkImport = async () => {
    if (!bulkImport.trim()) return;

    const lines = bulkImport.split('\n').filter(line => line.trim());
    const newAccounts = lines.map((line, index) => {
      const parts = line.trim().split(',');
      return {
        id: Date.now() + index,
        email: parts[0] || '',
        password: parts[1] || '',
        first_name: parts[2] || '',
        last_name: parts[3] || '',
        passport_number: parts[4] || '',
        phone: parts[5] || '',
        status: 'pending' as TeslaAccount['status'],
        created_at: new Date().toISOString(),
        appointments_count: 0,
        success_rate: 0,
        notes: ''
      };
    });

    setAccounts(prev => [...newAccounts, ...prev]);
    setBulkImport('');
  };

  const startAutomation = async (id: number) => {
    setRunningAccounts(prev => [...prev, id]);
    // Mock automation start
    setTimeout(() => {
      setRunningAccounts(prev => prev.filter(accId => accId !== id));
    }, 3000);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500">Active</Badge>;
      case 'inactive':
        return <Badge variant="secondary">Inactive</Badge>;
      case 'suspended':
        return <Badge variant="destructive">Suspended</Badge>;
      case 'pending':
        return <Badge variant="outline">Pending</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'suspended':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading Tesla accounts...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="h-8 w-8" />
            Tesla Account Management
          </h1>
          <p className="text-muted-foreground">
            Manage Tesla automation accounts, credentials, and automation status
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Account
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Add/Edit Account Form */}
        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>{editingAccount ? 'Edit Account' : 'Add New Account'}</CardTitle>
              <CardDescription>
                Configure Tesla automation account credentials
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      value={formData.first_name}
                      onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                      placeholder="Ahmed"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      value={formData.last_name}
                      onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                      placeholder="Benali"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="user@example.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="password123"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="passport_number">Passport Number</Label>
                    <Input
                      id="passport_number"
                      value={formData.passport_number}
                      onChange={(e) => setFormData({ ...formData, passport_number: e.target.value })}
                      placeholder="A1234567"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="+213123456789"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    placeholder="Additional notes..."
                    rows={3}
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">
                    {editingAccount ? 'Update Account' : 'Add Account'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => {
                    setShowForm(false);
                    setEditingAccount(null);
                    resetForm();
                  }}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Bulk Import */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Bulk Import
            </CardTitle>
            <CardDescription>
              Import multiple accounts at once (CSV format)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bulk-import">Account List</Label>
              <Textarea
                id="bulk-import"
                value={bulkImport}
                onChange={(e) => setBulkImport(e.target.value)}
                placeholder="email,password,first_name,last_name,passport_number,phone&#10;user1@example.com,pass123,Ahmed,Benali,A1234567,+213123456789&#10;user2@example.com,pass456,Fatima,Zohra,B7654321,+213987654321"
                rows={6}
              />
              <p className="text-sm text-muted-foreground">
                Format: email,password,first_name,last_name,passport_number,phone (one per line)
              </p>
            </div>
            <Button onClick={handleBulkImport} className="w-full">
              <Upload className="h-4 w-4 mr-2" />
              Import Accounts
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Account List */}
      <Card>
        <CardHeader>
          <CardTitle>Account List ({accounts.length})</CardTitle>
          <CardDescription>
            Manage Tesla automation accounts and their status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {accounts.map((account) => (
              <div key={account.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(account.status)}
                    <div>
                      <div className="font-medium">
                        {account.first_name} {account.last_name}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {account.email}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(account.status)}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startAutomation(account.id)}
                      disabled={runningAccounts.includes(account.id)}
                    >
                      {runningAccounts.includes(account.id) ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                  <div>
                    <span className="text-muted-foreground">Password:</span>
                    <div className="font-medium flex items-center gap-1">
                      {showPassword === account.id ? account.password : '••••••••'}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowPassword(showPassword === account.id ? null : account.id)}
                      >
                        {showPassword === account.id ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                      </Button>
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Passport:</span>
                    <div className="font-medium">{account.passport_number || 'N/A'}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Appointments:</span>
                    <div className="font-medium">{account.appointments_count}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Success Rate:</span>
                    <div className="font-medium">{account.success_rate}%</div>
                  </div>
                </div>

                {account.notes && (
                  <div className="text-sm text-muted-foreground mb-3 p-2 bg-muted rounded">
                    <strong>Notes:</strong> {account.notes}
                  </div>
                )}
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Created: {new Date(account.created_at).toLocaleDateString()}
                    {account.last_login && (
                      <span className="ml-4">
                        Last login: {new Date(account.last_login).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(account)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(account.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{accounts.length}</div>
                <div className="text-sm text-muted-foreground">Total Accounts</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {accounts.filter(a => a.status === 'active').length}
                </div>
                <div className="text-sm text-muted-foreground">Active Accounts</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-yellow-500" />
              <div>
                <div className="text-2xl font-bold">
                  {accounts.filter(a => a.status === 'pending').length}
                </div>
                <div className="text-sm text-muted-foreground">Pending Accounts</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Play className="h-5 w-5 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">
                  {runningAccounts.length}
                </div>
                <div className="text-sm text-muted-foreground">Running</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
