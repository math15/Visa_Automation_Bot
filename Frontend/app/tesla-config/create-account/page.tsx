'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import { 
  User, 
  Mail, 
  Phone, 
  FileText, 
  MapPin, 
  Flag, 
  Shield,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Key,
  UserPlus,
  Save
} from 'lucide-react';

interface FormData {
  // Personal Information (BLS format)
  SurName: string;  // BLS: SurName (Family Name) - optional
  FirstName: string;  // BLS: FirstName (Given Name) - required
  LastName: string;  // BLS: LastName - required
  FamilyName: string;  // Legacy field
  DateOfBirth: string;
  Gender: string;
  
  // Passport Information
  PassportNumber: string;
  PassportType: string;
  PassportIssueDate: string;
  PassportExpiryDate: string;
  PassportIssuePlace: string;
  PassportIssueCountry: string;
  
  // Contact Information
  Email: string;
  Mobile: string;
  PhoneCountryCode: string;
  
  // Location Information
  BirthCountry: string;
  CountryOfResidence: string;
  
  // Additional Information
  MaritalStatus: string;
  NumberOfMembers: number;
  Relationship: string;
  PrimaryApplicant: boolean;
  
  // Account Credentials
  Password: string;
  ConfirmPassword: string;
}

interface ValidationErrors {
  [key: string]: string;
}

export default function CreateAccountPage() {
  const [isEditMode, setIsEditMode] = useState(false);
  const [editAccountId, setEditAccountId] = useState<number | null>(null);
  const { addToast } = useToast();
  
  const [formData, setFormData] = useState<FormData>({
    SurName: '',  // BLS: SurName (Family Name)
    FirstName: '',  // BLS: FirstName (Given Name)
    LastName: '',  // BLS: LastName
    FamilyName: '',  // Legacy
    DateOfBirth: '',
    Gender: 'Male',
    PassportNumber: '',
    PassportType: 'Ordinary',
    PassportIssueDate: '',
    PassportExpiryDate: '',
    PassportIssuePlace: '',  // BLS: Required! Changed from 'Algiers'
    PassportIssueCountry: 'Algeria',
    Email: '',
    Mobile: '',
    PhoneCountryCode: '+213',
    BirthCountry: 'Algeria',
    CountryOfResidence: 'Algeria',
    MaritalStatus: 'Single',
    NumberOfMembers: 1,
    Relationship: 'Self',
    PrimaryApplicant: true,
    Password: '',
    ConfirmPassword: ''
  });

  // Auto-generate credentials on component mount
  React.useEffect(() => {
    // Check for edit mode from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const editParam = urlParams.get('edit');
    
    if (editParam === 'true') {
      setIsEditMode(true);
      const id = urlParams.get('id');
      if (id) {
        setEditAccountId(parseInt(id));
      }
      
      // Pre-populate form with ALL URL parameters
      setFormData(prev => ({
        ...prev,
        // Personal Information (BLS format)
        SurName: urlParams.get('sur_name') || '',  // BLS: SurName
        FirstName: urlParams.get('first_name') || '',
        LastName: urlParams.get('last_name') || '',
        FamilyName: urlParams.get('family_name') || '',
        DateOfBirth: urlParams.get('date_of_birth') || '',
        Gender: urlParams.get('gender') || 'Male',
        MaritalStatus: urlParams.get('marital_status') || 'Single',
        
        // Passport Information
        PassportNumber: urlParams.get('passport_number') || '',
        PassportType: urlParams.get('passport_type') || 'Ordinary',
        PassportIssueDate: urlParams.get('passport_issue_date') || '',
        PassportExpiryDate: urlParams.get('passport_expiry_date') || '',
        PassportIssuePlace: urlParams.get('passport_issue_place') || 'Algiers',
        PassportIssueCountry: urlParams.get('passport_issue_country') || 'Algeria',
        
        // Contact Information
        Email: urlParams.get('email') || '',
        Mobile: urlParams.get('mobile') || '',
        PhoneCountryCode: urlParams.get('phone_country_code') || '+213',
        
        // Location Information
        BirthCountry: urlParams.get('birth_country') || 'Algeria',
        CountryOfResidence: urlParams.get('country_of_residence') || 'Algeria',
        
        // Additional Information
        NumberOfMembers: parseInt(urlParams.get('number_of_members') || '1'),
        Relationship: urlParams.get('relationship') || 'Self',
        PrimaryApplicant: urlParams.get('primary_applicant') === 'true',
        
        // Account Credentials
        Password: urlParams.get('password') || '',
        ConfirmPassword: urlParams.get('password') || '',
      }));
      
      addToast({
        type: 'info',
        title: 'Edit Mode',
        description: 'You are editing an existing account. Make your changes and save.'
      });
    } else {
      // Only auto-generate credentials for new accounts
      generateCredentials();
    }
  }, []);

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // Captcha solver state

  const handleInputChange = (field: keyof FormData, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    // Required field validation (BLS exact requirements)
    const requiredFields: (keyof FormData)[] = [
      'FirstName', 'LastName', 'DateOfBirth', 'PassportNumber',
      'PassportIssueDate', 'PassportExpiryDate', 'PassportIssuePlace',  // BLS requires IssuePlace!
      'Email', 'Mobile', 'Password'
    ];

    requiredFields.forEach(field => {
      if (!formData[field]) {
        newErrors[field] = `${field} is required`;
      }
    });

    // Mobile validation (BLS specific)
    if (formData.Mobile) {
      if (formData.Mobile.startsWith('0')) {
        newErrors.Mobile = 'Mobile Number Should Not Start With Zero';
      } else if (!/^[1-9]\d{7,9}$/.test(formData.Mobile)) {
        newErrors.Mobile = 'Mobile number must be 8-10 digits without leading zero';
      }
    }

    // Passport validation (BLS accepts ANY format - no strict validation!)
    // BLS does NOT enforce specific passport format
    if (formData.PassportNumber && formData.PassportNumber.length < 6) {
      newErrors.PassportNumber = 'Passport Number must be at least 6 characters';
    }

    // Email validation
    if (formData.Email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.Email)) {
      newErrors.Email = 'Please enter a valid email address';
    }

    // Password validation
    if (formData.Password && formData.Password.length < 8) {
      newErrors.Password = 'Password must be at least 8 characters long';
    }

    // Confirm password validation
    if (formData.Password !== formData.ConfirmPassword) {
      newErrors.ConfirmPassword = 'Passwords do not match';
    }

    // Date validations
    const today = new Date();
    const birthDate = new Date(formData.DateOfBirth);
    if (birthDate >= today) {
      newErrors.DateOfBirth = 'Date of birth must be in the past';
    }

    const passportIssueDate = new Date(formData.PassportIssueDate);
    const passportExpiryDate = new Date(formData.PassportExpiryDate);
    
    if (passportIssueDate >= today) {
      newErrors.PassportIssueDate = 'Passport issue date must be in the past';
    }
    
    if (passportExpiryDate <= today) {
      newErrors.PassportExpiryDate = 'Passport must not be expired';
    }
    
    if (passportIssueDate >= passportExpiryDate) {
      newErrors.PassportExpiryDate = 'Passport expiry date must be after issue date';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Prepare data for backend API (BLS format, dates in YYYY-MM-DD)
      const apiData = {
        sur_name: formData.SurName || null,  // BLS: SurName (optional)
        first_name: formData.FirstName,
        last_name: formData.LastName,
        family_name: formData.FamilyName || null,
        date_of_birth: formData.DateOfBirth,
        gender: formData.Gender,
        marital_status: formData.MaritalStatus,
        passport_number: formData.PassportNumber,
        passport_type: formData.PassportType,
        passport_issue_date: formData.PassportIssueDate,
        passport_expiry_date: formData.PassportExpiryDate,
        passport_issue_place: formData.PassportIssuePlace,  // BLS: Required!
        passport_issue_country: formData.PassportIssueCountry || null,
        email: formData.Email,
        mobile: formData.Mobile,
        phone_country_code: formData.PhoneCountryCode,
        birth_country: formData.BirthCountry || null,
        country_of_residence: formData.CountryOfResidence || null,
        number_of_members: formData.NumberOfMembers,
        relationship: formData.Relationship,
        primary_applicant: formData.PrimaryApplicant,
        password: formData.Password
      };

      console.log('Submitting to API:', apiData);

      let response;
      if (isEditMode && editAccountId) {
        // Update existing account
        response = await fetch(`http://localhost:8000/api/enhanced-bls/accounts/${editAccountId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(apiData),
        });
      } else {
        // Create new account
        response = await fetch('http://localhost:8000/api/enhanced-bls/accounts/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(apiData),
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create account');
      }

      const result = await response.json();
      console.log('Account saved successfully:', result);
      
      // Show success message
      if (isEditMode) {
        addToast({
          type: 'success',
          title: 'Account Updated',
          description: 'Account has been successfully updated!'
        });
        
        // Redirect back to account management
        setTimeout(() => {
          window.location.href = '/account-management';
        }, 2000);
      } else {
        addToast({
          type: 'success',
          title: 'Account Created',
          description: 'Account has been stored in the system. You can now create a BLS account for it from the Account Management page.'
        });
        
        // Reset form for new account
        setFormData({
          SurName: '',  // BLS: SurName field
          FirstName: '',
          LastName: '',
          FamilyName: '',
          DateOfBirth: '',
          Gender: 'Male',
          PassportNumber: '',
          PassportType: 'Ordinary',
          PassportIssueDate: '',
          PassportExpiryDate: '',
          PassportIssuePlace: '',  // Required field - start empty
          PassportIssueCountry: 'Algeria',
          Email: '',
          Mobile: '',
          PhoneCountryCode: '+213',
          BirthCountry: 'Algeria',
          CountryOfResidence: 'Algeria',
          MaritalStatus: 'Single',
          NumberOfMembers: 1,
          Relationship: 'Self',
          PrimaryApplicant: true,
          Password: '',
          ConfirmPassword: ''
        });
        
        // Regenerate credentials for new account
        generateCredentials();
      }
    } catch (error) {
      console.error('Error saving account:', error);
      
      // Handle specific validation errors
      if (error instanceof Error) {
        if (error.message.includes('Email already exists')) {
          setErrors(prev => ({ ...prev, Email: 'Email already exists' }));
        } else if (error.message.includes('Passport number already exists')) {
          setErrors(prev => ({ ...prev, PassportNumber: 'Passport number already exists' }));
        } else if (error.message.includes('Mobile Number Should Not Start With Zero')) {
          setErrors(prev => ({ ...prev, Mobile: 'Mobile Number Should Not Start With Zero' }));
        } else if (error.message.includes('Passport Number should Start with 2 Alphabet')) {
          setErrors(prev => ({ ...prev, PassportNumber: 'Passport Number should Start with 2 Alphabet followed with minimum 7 digit' }));
        } else {
          addToast({
            type: 'error',
            title: 'Save Failed',
            description: error.message
          });
        }
      } else {
        addToast({
          type: 'error',
          title: 'Save Error',
          description: 'Failed to save account. Please try again.'
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };



  const generateSampleData = () => {
    // Generate complete sample data with all required fields
    const timestamp = Date.now();
    const sampleEmail = `ahmed.benali${timestamp}@example.com`;
    
    const sampleData: FormData = {
      SurName: 'Benali',  // BLS: SurName (Family Name)
      FirstName: 'Ahmed',  // BLS: FirstName (Given Name)
      LastName: 'Benali',  // BLS: LastName
      FamilyName: 'Benali',  // Legacy
      DateOfBirth: '1990-05-15',
      Gender: 'Male',
      PassportNumber: '123456789',
      PassportType: 'Ordinary',
      PassportIssueDate: '2020-01-15',
      PassportExpiryDate: '2030-01-15',
      PassportIssuePlace: 'Algiers',  // BLS: Required!
      PassportIssueCountry: 'Algeria',
      Email: sampleEmail,  // Unique email
      Mobile: '555123456',  // Valid format (no leading 0, 8-10 digits)
      PhoneCountryCode: '+213',
      BirthCountry: 'Algeria',
      CountryOfResidence: 'Algeria',
      MaritalStatus: 'Single',
      NumberOfMembers: 1,
      Relationship: 'Self',
      PrimaryApplicant: true,
      Password: 'SecurePass123!',
      ConfirmPassword: 'SecurePass123!'
    };
    
    setFormData(sampleData);  // Replace entire form data
  };

  const generateEmail = () => {
    // Tesla 2.0 email generation pattern
    const domains = [
      'ambisens.site', 
      'ibizamails.info', 
      'ayroutod.shop', 
      'easygmail.shop', 
      'liveauto.live',
      'gmail.com', 
      'yahoo.com', 
      'hotmail.com', 
      'outlook.com'
    ];
    
    // Tesla 2.0 pattern: harrouche + timestamp
    const timestamp = Date.now();
    const username = `harrouche${timestamp}`;
    const domain = domains[Math.floor(Math.random() * domains.length)];
    
    const email = `${username}@${domain}`;
    
    setFormData(prev => ({ ...prev, Email: email }));
  };

  const generatePassword = () => {
    // Tesla 2.0 pattern: SAME password for all accounts
    // Based on Tesla 2.0: all accounts use the same password
    const password = 'Tesla2024!'; // Same password for all accounts
    
    setFormData(prev => ({ 
      ...prev, 
      Password: password,
      ConfirmPassword: password 
    }));
  };

  const generateCredentials = () => {
    // Auto-generate both email and password
    generateEmail();
    generatePassword();
  };

  const testEmailService = async () => {
    try {
      setIsSubmitting(true);
      
      const response = await fetch('http://localhost:8000/api/enhanced-bls/test-email-service', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to test email service');
      }

      const result = await response.json();
      
      // Create detailed test results message
      let message = `Email Service Test Results:\n\n`;
      message += `Overall Status: ${result.success ? 'SUCCESS' : 'FAILED'}\n`;
      message += `Service: ${result.service || 'Unknown'}\n`;
      message += `Email: ${result.email || 'Not generated'}\n\n`;
      
      message += `Test Details:\n`;
      result.tests.forEach((test: any, index: number) => {
        const status = test.status === 'success' ? '✓' : test.status === 'warning' ? '⚠' : '✗';
        message += `${index + 1}. ${status} ${test.test}: ${test.details}\n`;
      });
      
      message += `\nMessage: ${result.message}`;
      
      alert(message);
      
    } catch (error) {
      console.error('Error testing email service:', error);
      alert(`Email Service Test Failed:
      
${error instanceof Error ? error.message : 'Unknown error'}

Please check if the backend is running on http://localhost:8000`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          {isEditMode ? 'Edit Account' : 'Create Account'}
        </h1>
        <p className="text-muted-foreground">
          {isEditMode 
            ? 'Edit the account information below. Changes will be saved to the system.'
            : 'Create a new account in the system. You can create BLS accounts for it later from the Account Management page.'
          }
        </p>
        <div className="mt-2">
          <Badge variant="outline" className="text-xs">
            {isEditMode 
              ? 'Edit Mode: Make changes and save'
              : 'Step 1: Create Account → Step 2: Create BLS Account'
            }
          </Badge>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal Information
            </CardTitle>
            <CardDescription>
              Enter your personal details as they appear on your passport
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="SurName">Surname (Family Name)</Label>
                <Input
                  id="SurName"
                  value={formData.SurName}
                  onChange={(e) => handleInputChange('SurName', e.target.value)}
                  placeholder="Optional - as per BLS form"
                />
                <p className="text-xs text-muted-foreground">
                  BLS: SurName field (optional)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="FirstName">First Name (Given Name) *</Label>
                <Input
                  id="FirstName"
                  value={formData.FirstName}
                  onChange={(e) => handleInputChange('FirstName', e.target.value)}
                  className={errors.FirstName ? 'border-red-500' : ''}
                />
                {errors.FirstName && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.FirstName}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  BLS: FirstName (required)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="LastName">Last Name *</Label>
                <Input
                  id="LastName"
                  value={formData.LastName}
                  onChange={(e) => handleInputChange('LastName', e.target.value)}
                  className={errors.LastName ? 'border-red-500' : ''}
                />
                {errors.LastName && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.LastName}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  BLS: LastName (required)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="FamilyName">Family Name (Legacy)</Label>
                <Input
                  id="FamilyName"
                  value={formData.FamilyName}
                  onChange={(e) => handleInputChange('FamilyName', e.target.value)}
                  placeholder="For backward compatibility"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="DateOfBirth">Date of Birth * (YYYY-MM-DD)</Label>
                <Input
                  id="DateOfBirth"
                  type="date"
                  value={formData.DateOfBirth}
                  onChange={(e) => handleInputChange('DateOfBirth', e.target.value)}
                  className={errors.DateOfBirth ? 'border-red-500' : ''}
                />
                {errors.DateOfBirth && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.DateOfBirth}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Tesla 2.0 compatible format: YYYY-MM-DD
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="Gender">Gender</Label>
                <select
                  id="Gender"
                  value={formData.Gender}
                  onChange={(e) => handleInputChange('Gender', e.target.value)}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="MaritalStatus">Marital Status</Label>
                <select
                  id="MaritalStatus"
                  value={formData.MaritalStatus}
                  onChange={(e) => handleInputChange('MaritalStatus', e.target.value)}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md"
                >
                  <option value="Single">Single</option>
                  <option value="Married">Married</option>
                  <option value="Divorced">Divorced</option>
                  <option value="Widowed">Widowed</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Passport Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Passport Information
            </CardTitle>
            <CardDescription>
              Enter your passport details exactly as they appear on your passport
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="PassportNumber">Passport Number *</Label>
                <Input
                  id="PassportNumber"
                  value={formData.PassportNumber}
                  onChange={(e) => handleInputChange('PassportNumber', e.target.value)}
                  placeholder="123456789"
                  className={errors.PassportNumber ? 'border-red-500' : ''}
                />
                {errors.PassportNumber && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.PassportNumber}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  BLS accepts any format (min 6 characters)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="PassportType">Passport Type</Label>
                <select
                  id="PassportType"
                  value={formData.PassportType}
                  onChange={(e) => handleInputChange('PassportType', e.target.value)}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md"
                >
                  <option value="Ordinary">Ordinary</option>
                  <option value="Diplomatic">Diplomatic</option>
                  <option value="Official">Official</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="PassportIssueDate">Issue Date * (YYYY-MM-DD)</Label>
                <Input
                  id="PassportIssueDate"
                  type="date"
                  value={formData.PassportIssueDate}
                  onChange={(e) => handleInputChange('PassportIssueDate', e.target.value)}
                  className={errors.PassportIssueDate ? 'border-red-500' : ''}
                />
                {errors.PassportIssueDate && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.PassportIssueDate}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Tesla 2.0 compatible format: YYYY-MM-DD
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="PassportExpiryDate">Expiry Date * (YYYY-MM-DD)</Label>
                <Input
                  id="PassportExpiryDate"
                  type="date"
                  value={formData.PassportExpiryDate}
                  onChange={(e) => handleInputChange('PassportExpiryDate', e.target.value)}
                  className={errors.PassportExpiryDate ? 'border-red-500' : ''}
                />
                {errors.PassportExpiryDate && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.PassportExpiryDate}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Tesla 2.0 compatible format: YYYY-MM-DD
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="PassportIssuePlace">Passport Issue Place *</Label>
                <Input
                  id="PassportIssuePlace"
                  value={formData.PassportIssuePlace}
                  onChange={(e) => handleInputChange('PassportIssuePlace', e.target.value)}
                  placeholder="e.g., Algiers"
                  className={errors.PassportIssuePlace ? 'border-red-500' : ''}
                />
                {errors.PassportIssuePlace && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.PassportIssuePlace}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  BLS: IssuePlace is REQUIRED!
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="PassportIssueCountry">Issue Country</Label>
                <Input
                  id="PassportIssueCountry"
                  value={formData.PassportIssueCountry}
                  onChange={(e) => handleInputChange('PassportIssueCountry', e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="h-5 w-5" />
              Contact Information
            </CardTitle>
            <CardDescription>
              Enter your contact details for communication
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="Email">Email Address * (Auto-Generated)</Label>
                <div className="flex gap-2">
                  <Input
                    id="Email"
                    type="email"
                    value={formData.Email}
                    onChange={(e) => handleInputChange('Email', e.target.value)}
                    className={`${errors.Email ? 'border-red-500' : ''} bg-muted`}
                    placeholder="Email will be generated automatically"
                    disabled
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={generateEmail}
                    className="px-3"
                  >
                    <Mail className="h-4 w-4" />
                  </Button>
                </div>
                {errors.Email && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.Email}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Tesla 2.0 compatible email auto-generated on page load
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="Mobile">Mobile Number *</Label>
                <div className="flex gap-2">
                  <select
                    value={formData.PhoneCountryCode}
                    onChange={(e) => handleInputChange('PhoneCountryCode', e.target.value)}
                    className="px-3 py-2 border border-input bg-background rounded-md"
                  >
                    <option value="+213">+213 (Algeria)</option>
                    <option value="+33">+33 (France)</option>
                    <option value="+1">+1 (USA)</option>
                  </select>
                  <Input
                    id="Mobile"
                    value={formData.Mobile}
                    onChange={(e) => handleInputChange('Mobile', e.target.value)}
                    placeholder="123456789"
                    className={errors.Mobile ? 'border-red-500' : ''}
                  />
                </div>
                {errors.Mobile && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.Mobile}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Must not start with 0, 8-10 digits
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Location Information
            </CardTitle>
            <CardDescription>
              Enter your country information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="BirthCountry">Birth Country</Label>
                <Input
                  id="BirthCountry"
                  value={formData.BirthCountry}
                  onChange={(e) => handleInputChange('BirthCountry', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="CountryOfResidence">Country of Residence</Label>
                <Input
                  id="CountryOfResidence"
                  value={formData.CountryOfResidence}
                  onChange={(e) => handleInputChange('CountryOfResidence', e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Credentials */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Account Credentials
            </CardTitle>
            <CardDescription>
              Create secure login credentials for your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="Password">Password * (Auto-Generated)</Label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      id="Password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.Password}
                      onChange={(e) => handleInputChange('Password', e.target.value)}
                      className={`${errors.Password ? 'border-red-500' : ''} bg-muted`}
                      placeholder="Password will be generated automatically"
                      disabled
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={generatePassword}
                    className="px-3"
                  >
                    <Key className="h-4 w-4" />
                  </Button>
                </div>
                {errors.Password && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.Password}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Tesla 2.0 compatible password (same for all accounts)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ConfirmPassword">Confirm Password * (Auto-Generated)</Label>
                <div className="relative">
                  <Input
                    id="ConfirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.ConfirmPassword}
                    onChange={(e) => handleInputChange('ConfirmPassword', e.target.value)}
                    className={`${errors.ConfirmPassword ? 'border-red-500' : ''} bg-muted`}
                    placeholder="Password confirmation auto-generated"
                    disabled
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                {errors.ConfirmPassword && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.ConfirmPassword}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Additional Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Flag className="h-5 w-5" />
              Additional Information
            </CardTitle>
            <CardDescription>
              Additional details for your application
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="NumberOfMembers">Number of Members</Label>
                <Input
                  id="NumberOfMembers"
                  type="number"
                  min="1"
                  value={formData.NumberOfMembers}
                  onChange={(e) => handleInputChange('NumberOfMembers', parseInt(e.target.value) || 1)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="Relationship">Relationship</Label>
                <select
                  id="Relationship"
                  value={formData.Relationship}
                  onChange={(e) => handleInputChange('Relationship', e.target.value)}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md"
                >
                  <option value="Self">Self</option>
                  <option value="Spouse">Spouse</option>
                  <option value="Child">Child</option>
                  <option value="Parent">Parent</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={generateSampleData}
            className="flex items-center gap-2"
          >
            <CheckCircle className="h-4 w-4" />
            Fill Sample Data
          </Button>

          <div className="flex gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => window.location.reload()}
            >
              Reset Form
            </Button>
            
            <Button
              type="button"
              variant="secondary"
              onClick={testEmailService}
              className="flex items-center gap-2"
            >
              <Mail className="h-4 w-4" />
              Test Email Service
            </Button>
            
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  {isEditMode ? 'Saving Changes...' : 'Creating Account...'}
                </>
              ) : (
                <>
                  {isEditMode ? <Save className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
                  {isEditMode ? 'Save Changes' : 'Create Account'}
                </>
              )}
            </Button>
          </div>
        </div>
      </form>

      {/* Validation Summary */}
      {Object.keys(errors).length > 0 && (
        <Card className="mt-8 border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Validation Errors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {Object.entries(errors).map(([field, error]) => (
                <li key={field} className="text-sm text-red-600 flex items-center gap-2">
                  <span className="font-medium">{field}:</span>
                  <span>{error}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

    </div>
  );
}
