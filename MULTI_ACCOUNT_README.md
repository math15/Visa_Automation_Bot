# Multi-Account Management System

A comprehensive system for managing multiple accounts and creating BLS accounts concurrently.

## Features

### Backend Features
- **Account Management**: Create, read, update, delete accounts
- **Concurrent BLS Creation**: Process multiple BLS accounts simultaneously
- **Status Tracking**: Real-time status monitoring for each account
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Proxy Rotation**: Automatic proxy management for BLS creation
- **Database Models**: Separate Account and BLSAccount models

### Frontend Features
- **Account List Interface**: View all accounts with status indicators
- **Multi-Select**: Select multiple accounts for concurrent BLS creation
- **Individual Actions**: Create BLS account for individual accounts
- **Statistics Dashboard**: Real-time statistics and progress tracking
- **Error Display**: Clear error messages and retry options
- **Responsive Design**: Modern, mobile-friendly interface

## Architecture

### Database Models

#### Account Model
- Stores basic account information before BLS creation
- Tracks BLS creation status and progress
- Maintains processing attempts and error messages

#### BLSAccount Model (Legacy)
- Maintained for backward compatibility
- Contains BLS-specific credentials and status

### API Endpoints

#### Account Management (`/api/enhanced-bls/accounts/`)
- `POST /create` - Create new account
- `GET /` - List all accounts with filtering
- `GET /{id}` - Get specific account
- `PUT /{id}` - Update account
- `DELETE /{id}` - Delete account
- `POST /create-bls` - Create BLS accounts for multiple accounts
- `POST /retry-failed-bls` - Retry failed BLS creations
- `GET /processing-status` - Get processing status
- `GET /stats/summary` - Get account statistics

### Services

#### MultiAccountBLSService
- Handles concurrent BLS account creation
- Manages semaphores for rate limiting
- Provides status tracking and error handling
- Supports retry mechanisms for failed accounts

## Installation & Setup

### 1. Database Migration
```bash
cd Booking_Visa_Bot/Backend
python migrate_multi_account.py
```

### 2. Start Backend Server
```bash
cd Booking_Visa_Bot/Backend
python main.py
```

### 3. Start Frontend Server
```bash
cd Booking_Visa_Bot/Frontend
npm run dev
```

### 4. Access the Interface
Navigate to `http://localhost:3000/account-management`

## Usage

### Creating Accounts
1. Click "Create Account" button
2. Fill in account details (name, email, passport, etc.)
3. Click "Create Account" to save

### Creating BLS Accounts
1. **Individual Creation**: Click the play button next to any account
2. **Batch Creation**: 
   - Select multiple accounts using checkboxes
   - Click "Create BLS" button
   - Monitor progress in real-time

### Monitoring Progress
- **Status Badges**: Visual indicators for account and BLS status
- **Statistics Cards**: Overview of total accounts and their states
- **Error Messages**: Detailed error information for failed accounts
- **Retry Options**: Retry failed BLS creations

## Account Statuses

### Account Status
- `created` - Account created, BLS not started
- `bls_creating` - BLS account creation in progress
- `bls_created` - BLS account successfully created
- `bls_failed` - BLS account creation failed
- `inactive` - Account disabled

### BLS Status
- `not_created` - BLS account not created yet
- `creating` - BLS account creation in progress
- `created` - BLS account successfully created
- `failed` - BLS account creation failed

## Configuration

### Concurrent Processing
The system supports configurable concurrent processing:
```python
# In MultiAccountBLSService
self.max_concurrent = 5  # Maximum concurrent BLS creations
```

### Proxy Management
- Automatic proxy rotation for BLS creation
- Proxy validation and health checking
- Support for Algerian and Spanish proxies

## Error Handling

### Common Errors
- **Email Already Exists**: Account with email already exists
- **Passport Already Exists**: Account with passport number already exists
- **BLS Creation Failed**: Various BLS-specific errors
- **Proxy Issues**: Proxy connection or validation errors

### Retry Mechanisms
- Automatic retry for failed BLS creations
- Configurable retry attempts
- Exponential backoff for rate limiting

## Development

### Adding New Features
1. Update database models in `models/database.py`
2. Add API endpoints in `routes/enhanced_bls/account_management.py`
3. Update frontend components in `app/account-management/page.tsx`
4. Run database migration if needed

### Testing
- Use the BLS Test page for individual account testing
- Monitor logs for detailed error information
- Use the statistics dashboard for system health

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure database is running and accessible
2. **Proxy Issues**: Check proxy configuration and availability
3. **BLS Website Changes**: Monitor for website structure changes
4. **Rate Limiting**: Adjust concurrent processing limits if needed

### Logs
- Backend logs: Check console output for detailed error messages
- Frontend logs: Use browser developer tools for client-side errors
- Database logs: Check database logs for connection issues

## Future Enhancements

- **Scheduled Processing**: Automatic BLS creation scheduling
- **Advanced Filtering**: More sophisticated account filtering options
- **Bulk Import**: CSV import for multiple accounts
- **Email Notifications**: Notifications for completion/failure
- **Analytics Dashboard**: Advanced analytics and reporting
- **API Rate Limiting**: Enhanced rate limiting and throttling
