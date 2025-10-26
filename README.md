# 🔍 Rug Pull Checker Agent

AI-powered Solana token analyzer that detects rug pulls and scams using SolSniffer API and FireworksAI.

## ✨ Features

- 🔍 **Instant Analysis** - Paste any Solana contract address
- 🤖 **AI-Powered** - Comprehensive analysis using Llama 3.1
- 💾 **Smart Caching** - Reduces API costs with 24-hour cache
- 🎯 **Clear Verdicts** - LOW RISK / MODERATE RISK / HIGH RISK
- ⚡ **Real-time Streaming** - Live AI responses

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```bash
# FireworksAI (Required) - Get from https://fireworks.ai
FIREWORKS_API_KEY=your_fireworks_key_here
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-8b-instruct

# SolSniffer (Optional - has default)
SOLSNIFFER_API_KEY=to5p72yao22ajhlxiw6bvj8hogt896

# Cache Settings
SOLSNIFFER_ENABLE_CACHE=True
SOLSNIFFER_CACHE_TTL_HOURS=24
```

### 3. Run the Server

```bash
python main.py
```

You should see:
```
============================================================
🔍 Rug Pull Checker Agent Started
============================================================
🚀 Server starting on http://0.0.0.0:8000
```

## 💬 Usage

### Option 1: Use cURL

```bash
curl -N --location 'http://localhost:8000/assist' \
--header 'Content-Type: application/json' \
--data '{
  "query": {
    "id": "001",
    "prompt": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
  },
  "session": {
    "processor_id": "Rug Pull Checker",
    "activity_id": "act_001",
    "request_id": "req_001",
    "interactions": []
  }
}'
```

### Option 2: Use Sentient Client

```bash
# Clone and setup the client
git clone https://github.com/sentient-agi/Sentient-Agent-Client.git
cd Sentient-Agent-Client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Connect to your agent
python3 -m src.sentient_agent_client --url http://localhost:8000/assist
```

### Example Queries

Just paste a Solana contract address:

```
DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

Or ask questions:

```
Is this token safe? 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
Check this CA: [paste address]
```

## 📊 What It Checks

### Token Information
- Token name and symbol
- Current price
- Market cap & liquidity
- Total supply
- Holder distribution

### Security Analysis
- ✅ Mint authority (disabled = good)
- ✅ Freeze authority (disabled = good)
- ✅ Liquidity pool (burned = good)
- ✅ Holder concentration (low = good)

### AI Risk Assessment
- Overall risk score (0-100)
- Risk level (LOW/MODERATE/HIGH)
- Specific red flags
- Specific green flags
- Clear recommendations

## 📁 Project Structure

```
rug-pull-checker/
├── src/
│   └── rugpull_agent/
│       ├── agent.py              # Main agent logic
│       ├── solsniffer_service.py # API integration
│       ├── llm_service.py        # AI analysis
│       └── server.py             # FastAPI server
├── config/
│   ├── solsniffer_config.py      # API settings
│   └── llm_config.py             # AI settings
├── utils/
│   ├── cache.py                  # Caching system
│   └── ca_parser.py              # Address parser
├── .env                          # Your API keys
├── main.py                       # Entry point
└── requirements.txt
```

## 🔧 Configuration

### Switch AI Models

In `.env`:
```bash
# Fast & Free (default)
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-8b-instruct

# Better Quality
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-70b-instruct

# Best Quality
FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-405b-instruct
```

### Adjust Cache Duration

```bash
SOLSNIFFER_CACHE_TTL_HOURS=24  # Cache for 24 hours
# or
SOLSNIFFER_ENABLE_CACHE=False  # Disable cache
```

### CORS Settings

Edit `main.py` if you need specific origins:
```python
server = RugPullServerWithCORS(
    agent,
    allow_origins=["http://localhost:3000"]  # Your frontend URL
)
```

## 🐛 Troubleshooting

### "FIREWORKS_API_KEY is not set"
→ Create `.env` file and add your API key from [fireworks.ai](https://fireworks.ai)

### Token showing as "Unknown"
```bash
# Test the API directly
python debug_api.py

# Check logs for:
# ✅ Successfully parsed JSON
# 📊 Sending X bytes to AI
```

### CA not detected
```bash
# Test the parser
python -c "from utils.ca_parser import CAParser; print(CAParser.extract_contract_address('your message'))"
```

### Connection errors
- Check internet connection
- Verify SolSniffer API is accessible
- Try increasing timeout in `.env`:
```bash
SOLSNIFFER_TIMEOUT=60
```

## 📊 Response Format

The AI provides a comprehensive analysis:

```markdown
# 📊 Token Analysis: [Token Name] ([SYMBOL])

**Contract:** `DezXAZ8z...`

## 💰 Market Data
- Price: $0.00000123
- Market Cap: $1,234,567
- Liquidity: $456,789
- Supply: 1,000,000,000

## 🔒 Security Analysis
✅ Mint authority disabled
✅ Freeze authority disabled
⚠️ LP not burned
⚠️ High holder concentration

## 🎯 Risk Assessment
**Risk Level:** 🟡 MODERATE RISK
**Risk Score:** 45/100

## 📋 Verdict
[Detailed AI explanation and recommendations]
```

## 🧪 Testing

### Check Health Endpoint
```bash
curl http://localhost:8000/health
```

### Test Contract Detection
```bash
python -c "from utils.ca_parser import CAParser; \
print(CAParser.extract_contract_address('DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'))"
```

### Clear Cache
```bash
rm -rf .cache/
```

## 🌟 Key Features

### AI-First Architecture
- Raw API data sent directly to AI
- AI extracts and formats everything
- No hardcoded field paths
- Adapts to API changes automatically

### Smart Contract Detection
- Detects CAs in any message format
- Handles questions like "Is [CA] safe?"
- Works with abbreviated formats
- Validates Base58 encoding

### Caching System
- Reduces API costs
- Configurable TTL
- Automatic cleanup
- Optional disable for testing

## 📝 Requirements

- Python 3.9+
- FireworksAI API key (required)
- SolSniffer API key (optional - has default)
- Internet connection

## 🔗 Links

- [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)
- [SolSniffer API](https://solsniffer.com)
- [FireworksAI](https://fireworks.ai/)

## 📄 License

MIT License

## 🙏 Acknowledgments

Built with [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)

---

**Ready to analyze tokens!** 🚀

For issues: Create an issue on GitHub or contact support.