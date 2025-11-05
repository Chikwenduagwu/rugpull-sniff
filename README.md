#Rug Pull Checker Agent

AI-powered Solana token analyzer that detects rug pulls and scams.

## Features

- **Instant Analysis** - Paste any Solana contract address
- **AI-Powered** - Comprehensive analysis using Dobby(you can change in my .env)
- **Smart Caching** - Reduces API costs with 24-hour cache
- **Clear Verdicts** - LOW RISK / MODERATE RISK / HIGH RISK
- ⚡ **Real-time Streaming** - Live AI responses

## Quick Start

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
FIREWORKS_MODEL=use any model on fireworksAI but Dobby was used here, change in .env

# SolSniffer (Required)
SOLSNIFFER_API_KEY=Get an API key from solsniffer 

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
rug-pull-agent/
├── src/
│   └── rugpull_agent/
│       ├── agent.py              
│       ├── solsniffer_service.py 
│       ├── llm_service.py        
│       └── server.py             
├── config/
│   ├── solsniffer_config.py      
│   └── llm_config.py             
├── utils/
│   ├── cache.py                  
│   └── ca_parser.py              
├── .env                          
├── main.py                       
└── requirements.txt
```

## 🔧 Configuration

### Adjust Cache Duration

```bash
SOLSNIFFER_CACHE_TTL_HOURS=24  # Cache for 24 hours
# or
SOLSNIFFER_ENABLE_CACHE=False  # Disable cache
```

## 🐛 Troubleshooting

### "FIREWORKS_API_KEY is not set"
→ Create `.env` file and add your API key from [fireworks.ai](https://fireworks.ai)

 

### Connection errors
- Check internet connection
- Verify SolSniffer API is accessible
- Try increasing timeout in `.env`:
```bash
SOLSNIFFER_TIMEOUT=60
```

## 📊 Response Format

![Screenshot_20251026-193731_1_074028](https://github.com/user-attachments/assets/5a0b7ec4-ef2d-42d7-a5f7-4c87c1d020fe)

### Clear Cache
```bash
rm -rf .cache/
```

## Key Features

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
- SolSniffer API key (required)
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

For issues: Create an issue on GitHub or contact me on X https://x.com/agwuchikwendu.
