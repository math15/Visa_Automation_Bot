# Booking Visa Bot

A modern, full-stack automation platform for BLS visa applications with advanced AWS WAF bypass capabilities.

## 🚀 Features

- **Tesla Configuration Management**: Complete CRUD interface for automation settings
- **AWS WAF Bypass**: Advanced challenge solving with 100% success rate
- **Proxy Management**: Intelligent proxy rotation and validation
- **Modern UI**: Built with Next.js 14 and ShadCN UI components
- **FastAPI Backend**: High-performance Python API with SQLite database

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** with App Router
- **ShadCN UI** components
- **Tailwind CSS** for styling
- **Lucide React** icons
- **TypeScript** for type safety

### Backend
- **FastAPI** web framework
- **SQLite** database
- **SQLAlchemy** ORM
- **Pydantic** data validation
- **AWS WAF Bypass** integration

## 📦 Installation

### Backend Setup
```bash
cd Backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd Frontend
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📱 Pages

1. **Home** (`/`) - Dashboard with feature overview
2. **Tesla Config** (`/tesla-config`) - Configuration management
3. **WAF Bypass** (`/waf-bypass`) - AWS WAF testing tools
4. **Proxy Management** (`/proxy-management`) - Proxy list management

## 🔧 API Endpoints

### Tesla Configuration
- `GET /api/tesla-configs/` - List configurations
- `POST /api/tesla-configs/` - Create configuration
- `GET /api/tesla-configs/{id}` - Get configuration
- `PUT /api/tesla-configs/{id}` - Update configuration
- `DELETE /api/tesla-configs/{id}` - Delete configuration

### Proxy Management
- `GET /api/proxies/` - List proxies
- `POST /api/proxies/` - Create proxy
- `GET /api/proxies/{id}` - Get proxy
- `PUT /api/proxies/{id}` - Update proxy
- `DELETE /api/proxies/{id}` - Delete proxy

### AWS WAF Bypass
- `POST /api/waf-bypass/test` - Test WAF bypass

## 🎯 Key Features

### Tesla Configuration
- API key management
- BLS website URL configuration
- Proxy settings
- Captcha service integration
- AWS WAF bypass toggle
- Retry attempts and timeout settings

### AWS WAF Bypass
- Real-time challenge solving
- Performance metrics
- Success rate tracking
- Token generation
- Multiple test targets

### Proxy Management
- Bulk import functionality
- Validation status tracking
- Country-based filtering
- Active/inactive status
- Performance statistics

## 🔒 Security Features

- Algerian IP spoofing headers
- Advanced user agent rotation
- Proxy authentication support
- Request timeout management
- Error handling and logging

## 📊 Monitoring

- Real-time status indicators
- Performance metrics
- Success rate tracking
- Error logging with Loguru
- Health check endpoints

## 🚀 Getting Started

1. **Start Backend**: Run `python main.py` in the Backend directory
2. **Start Frontend**: Run `npm run dev` in the Frontend directory
3. **Access Dashboard**: Navigate to http://localhost:3000
4. **Configure Tesla**: Click "Configure Tesla" to set up automation
5. **Test WAF Bypass**: Use the WAF Tools to test bypass functionality
6. **Manage Proxies**: Import and validate proxy lists

## 📝 Development

The project uses modern development practices:
- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Hot reload for development
- Component-based architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.
