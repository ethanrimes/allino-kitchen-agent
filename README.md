# Ghost Kitchen AI Platform 🍽️🤖

An autonomous AI-driven platform for managing ghost kitchen operations in Colombia. This system leverages multiple AI agents to handle market research, menu creation, demand forecasting, and multi-channel marketing.

## 🚀 Features

- **Deep Market Research**: Automated competitor analysis and trend identification using Perplexity AI
- **Intelligent Menu Creation**: Data-driven menu optimization based on market insights
- **Demand Forecasting**: Multi-method forecasting for inventory optimization
- **Multi-Channel Marketing**: Automated content creation and posting across Facebook, Instagram, and WhatsApp
- **Order Management**: Complete order processing and tracking system
- **Inventory Management**: Automated supplier communication and reordering

## 🏗️ Architecture

The platform uses a hierarchical agent-based architecture:

```
MainOrchestrator
├── ResearchAgent (Perplexity-powered)
├── MenuCreationAgent
├── DemandForecastingAgent
├── SocialMediaOrchestrationAgent
└── ContentCreationAgent
```

## 📋 Prerequisites

- Python 3.11+
- Supabase account and project
- API Keys for:
  - OpenAI GPT-4
  - Perplexity AI
  - Facebook Graph API
  - Instagram Business API
  - WhatsApp Business API
  - Wompi (payments)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/ghost-kitchen-ai.git
cd ghost-kitchen-ai
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Supabase database

Run the SQL migrations in `database/migrations/initial_schema.sql` in your Supabase project.

### 5. Run the application

```bash
# Development mode
python main.py

# Production with Docker
docker-compose up -d
```

## 🔧 Configuration

### Agent Templates

Modify agent behavior by editing YAML templates in `prompts/templates/`:
- `research_agent.yaml` - Market research configuration
- `menu_creation_agent.yaml` - Menu generation rules
- `social_media_agent.yaml` - Social media strategies

### Budget Limits

Set daily budget limits in `.env`:
```
DAILY_MARKETING_BUDGET=500000  # COP
DAILY_INVENTORY_BUDGET=2000000  # COP
```

## 📡 API Endpoints

### Planning
- `POST /planning/execute` - Trigger full planning cycle
- `GET /planning/status` - Check planning status

### Research
- `POST /research/execute` - Execute market research

### Menu
- `POST /menu/create` - Create/update menu
- `GET /menu/current` - Get current menu

### Social Media
- `POST /social/post` - Post to social channels

### Orders
- `POST /orders/create` - Create order
- `PUT /orders/{id}/status` - Update order status

### Analytics
- `GET /analytics/sales` - Sales analytics
- `GET /analytics/performance` - System performance

## 🔄 Workflow

1. **Research Phase**: System researches Colombian food market trends
2. **Menu Creation**: AI creates optimized menu based on research
3. **Demand Forecasting**: Predicts demand for each menu item
4. **Content Creation**: Generates platform-specific social content
5. **Social Posting**: Posts menu updates across all channels
6. **Order Processing**: Handles incoming orders
7. **Inventory Management**: Monitors stock and reorders

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/unit/test_orchestrator.py
```

## 📊 Monitoring

Access system metrics:
- Logs: `logs/app.log`
- Memory stats: `GET /analytics/performance`
- Agent status: `GET /agents/status`

## 🚦 Health Check

```bash
curl http://localhost:8000/health
```

## 🔐 Security

- All API keys stored in environment variables
- Supabase Row Level Security (RLS) enabled
- Input validation on all endpoints
- Rate limiting on external API calls

## 📈 Scaling

The system is designed to scale:
- Horizontal scaling via Docker Swarm/Kubernetes
- Redis for caching and job queues
- Async processing for all heavy operations
- Database connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Contact: support@ghostkitchen.ai

## 🗺️ Roadmap

- [ ] Voice ordering via WhatsApp
- [ ] Multi-language support
- [ ] Advanced ML models for forecasting
- [ ] Real-time delivery tracking
- [ ] Customer loyalty program
- [ ] Integration with more delivery platforms

## 🙏 Acknowledgments

- Built with LangChain and FastAPI
- Powered by OpenAI and Perplexity AI
- Designed for the Colombian market 🇨🇴




I'll guide you through launching the orchestration agent and starting the research and menu planning workflow. Here are multiple approaches:

## 🚀 **Quick Start Guide**

### **Option 1: Direct Python Execution (Simplest)**## 🚀 **How to Launch the Orchestration Agent**

I've created several launch methods for you. Here's the complete guide:

### **📋 Step 1: First-Time Setup**

```bash
# 1. Navigate to project directory
cd ghost-kitchen-ai

# 2. Create and configure environment file
cp .env.example .env

# 3. Edit .env with your actual API keys (REQUIRED):
# - OPENAI_API_KEY (for AI agents)
# - PERPLEXITY_API_KEY (for research) 
# - SUPABASE_URL & SUPABASE_SERVICE_KEY (for database)
# - Social media keys (optional but recommended)

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create required directories
mkdir -p logs prompts/templates
```

### **✅ Step 2: Validate Your Setup**

```bash
# Run validation script to check everything is configured
python scripts/validate_setup.py

# Or using Make
make validate
```





This will check:
- ✅ Environment file exists
- ✅ Required API keys are configured
- ✅ Dependencies are installed  
- ✅ Supabase connection works
- ✅ Required directories exist

### **🎯 Step 3: Launch Methods**

#### **Method 1: Quick Start (Recommended for Testing)**
```bash
# Run a single planning cycle immediately
python scripts/start_platform.py

# Or using Make
make run-cycle
```

This will:
1. Research Colombian food market (via Perplexity)
2. Create optimized menu
3. Forecast demand
4. Create social content
5. Post to configured social channels

#### **Method 2: API Server Mode**
```bash
# Start the FastAPI server
python main.py

# Or using Make  
make run-api

# Then trigger planning cycle via API
curl -X POST http://localhost:8000/planning/execute
```

#### **Method 3: Docker (Production)**
```bash
# Start with Docker Compose
docker-compose up -d

# Or using Make
make docker-up

# Check logs
docker-compose logs -f
```

#### **Method 4: Interactive Mode**
```bash
# Use the run script for menu-driven options
chmod +x run.sh
./run.sh
```

### **🧪 Step 4: Test Individual Components**

If you want to test components separately:

```bash
# Run component tester
python scripts/test_components.py
```

Options:
1. Test Research Agent only
2. Test Menu Creation only  
3. Test Social Media posting only
4. Test all sequentially

### **📊 Step 5: Monitor Results**

#### **Via Logs:**
```bash
# Watch real-time logs
tail -f logs/app.log
```

#### **Via API Endpoints:**
```bash
# Check planning status
curl http://localhost:8000/planning/status

# Get agent status
curl http://localhost:8000/agents/status

# View performance metrics
curl http://localhost:8000/analytics/performance
```

### **⚡ Quick Commands Reference**

Using **Make** (easiest):
```bash
make install      # Install dependencies
make validate     # Check setup
make start        # Validate + run cycle
make run-api      # Start API server
make test         # Test components
```

Using **Python directly**:
```bash
python scripts/validate_setup.py      # Check setup
python scripts/start_platform.py      # Run planning cycle
python scripts/test_components.py     # Test components
python main.py                        # Start API server
```

### **🎯 What Happens When You Launch**

When you run the planning cycle, here's what happens:

1. **Research Phase** (2-3 minutes)
   - Searches for Colombian food trends
   - Analyzes competitors
   - Identifies opportunities

2. **Menu Creation** (1-2 minutes)
   - Generates menu items based on research
   - Optimizes pricing for 60%+ margins
   - Creates combos and deals

3. **Demand Forecasting** (1 minute)
   - Predicts 30-day demand for each item
   - Calculates inventory needs
   - Identifies peak periods

4. **Content Creation** (1 minute)
   - Generates platform-specific content
   - Creates Spanish/English descriptions
   - Adds relevant hashtags

5. **Social Posting** (1-2 minutes)
   - Posts to Facebook
   - Posts to Instagram
   - Sends WhatsApp broadcasts
   - Manages boost budgets

### **💡 Pro Tips**

1. **Start with validation**: Always run `make validate` first
2. **Test components**: Use test script before full cycle
3. **Monitor logs**: Keep `tail -f logs/app.log` open
4. **API mode**: Best for integration with other systems
5. **Docker**: Use for production deployment

### **🚨 Troubleshooting**

If something fails:

```bash
# Check what's missing
python scripts/validate_setup.py

# Test individual components
python scripts/test_components.py

# Check logs for errors
tail -n 50 logs/app.log

# Reset agent states
curl -X POST http://localhost:8000/agents/research_agent/reset
```

### **📈 Next Steps After Launch**

Once running successfully:
1. Monitor the created menu in Supabase
2. Check social media posts on your configured accounts
3. Review forecast data for inventory planning
4. Analyze engagement metrics
5. Adjust templates in `prompts/templates/` for better results

The system will continue learning and optimizing with each cycle!




ghost-kitchen-ai/
├── .env.example
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── README.md
├── main.py
│
├── config/
│   ├── settings.py
│   └── logging_config.py
│
├── core/
│   ├── orchestrator.py
│   ├── base_agent.py
│   ├── memory_manager.py
│   └── state_manager.py
│
├── agents/
│   ├── planning/
│   │   ├── research_agent.py
│   │   ├── menu_creation_agent.py
│   │   └── demand_forecasting_agent.py
│   │
│   └── marketing/
│       ├── social_media_orchestration_agent.py
│       └── content_creation_agent.py
│
├── integrations/
│   ├── channels/
│   │   ├── facebook_integration.py
│   │   ├── instagram_integration.py
│   │   └── whatsapp_integration.py
│   │
│   └── external/
│       └── perplexity_client.py
│
├── database/
│   └── supabase_client.py
│
├── tools/
│   ├── calculation_engine.py
│   └── data_analyzer.py
│
└── prompts/
    └── templates/
        ├── research_agent.yaml
        ├── menu_creation_agent.yaml
        └── social_media_agent.yaml