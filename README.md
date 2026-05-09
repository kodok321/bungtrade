# BungTrade - AI Trading Platform

Professional AI-powered trading platform with Binance integration, real-time market data, automated trading, and advanced analytics.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![React](https://img.shields.io/badge/React-18-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Features

### Trading
- **Binance Integration** - Direct API connection for Spot & Futures trading
- **Auto Trading Engine** - Manual, Semi-Auto, and Full Auto modes
- **Paper Trading** - Risk-free simulated trading with virtual balance
- **Multi-Pair Scanner** - AI-powered scanner for BTC, ETH, SOL, XRP, and more

### AI & Analysis
- **AI Signal Engine** - Multi-timeframe analysis with confidence scoring
- **Technical Indicators** - EMA, RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, VWAP
- **6 Modular Strategies** - EMA Cross, RSI, MACD, Scalping, Breakout, AI Adaptive
- **Backtesting System** - Historical testing with equity curves, Sharpe ratio, drawdown analysis

### Risk Management
- Risk per trade limits
- Max daily loss protection
- Max drawdown monitoring
- Position sizing calculator
- Emergency close all positions
- Auto-stop trading on limits

### Dashboard & UI
- Professional dark mode interface (Binance/TradingView style)
- Real-time price updates via WebSocket
- Equity curves, top movers, Fear & Greed index
- Glassmorphism design with smooth animations
- Responsive layout with collapsible sidebar

### Notifications
- Telegram bot integration for signal alerts, trade notifications, daily reports, and error alerts

### Security
- JWT authentication with bcrypt password hashing
- AES-256 encrypted API key storage
- Rate limit protection
- Secure session management

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Redis |
| **Frontend** | React 18, TailwindCSS, Recharts, Framer Motion |
| **Trading** | ccxt (Binance), WebSocket real-time data |
| **AI** | Pandas, NumPy, Scikit-learn |
| **Deploy** | Docker, Docker Compose |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### 1. Clone & Configure

```bash
git clone https://github.com/kodok321/bungtrade.git
cd bungtrade
cp .env.example .env
# Edit .env with your settings
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on port 8000
- **Frontend** on port 3000

### 3. Access the Platform

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
bungtrade/
├── backend/
│   ├── api/              # FastAPI route handlers
│   │   ├── auth.py             # Login, register, JWT
│   │   ├── exchange_routes.py  # Binance API key management
│   │   ├── trading_routes.py   # Order placement, positions
│   │   ├── dashboard_routes.py # Dashboard stats
│   │   ├── signal_routes.py    # AI signals & scanner
│   │   ├── backtest_routes.py  # Backtesting engine
│   │   ├── paper_routes.py     # Paper trading accounts
│   │   ├── market_routes.py    # Market data endpoints
│   │   ├── settings_routes.py  # User preferences
│   │   ├── strategy_routes.py  # Strategy listing
│   │   └── risk_routes.py      # Risk management controls
│   ├── ai/               # AI signal engine
│   ├── exchange/          # Binance client (ccxt)
│   ├── indicators/        # Technical analysis (EMA, RSI, MACD, etc.)
│   ├── strategies/        # Modular trading strategies
│   ├── risk/              # Risk management engine
│   ├── services/          # Auto trading service
│   ├── websocket_handlers/# Real-time WebSocket proxy
│   ├── telegram_bot/      # Telegram notifications
│   ├── backtesting/       # Backtesting engine
│   ├── database/          # SQLAlchemy models & session
│   ├── core/              # Config, security, encryption
│   └── main.py            # FastAPI app entrypoint
├── frontend/
│   └── src/
│       ├── components/    # Layout, shared components
│       ├── pages/         # Dashboard, Trading, Signals, etc.
│       ├── context/       # Auth context
│       ├── hooks/         # WebSocket hook
│       └── services/      # API client
├── docker/                # Dockerfiles & nginx config
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |

### Exchange
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/exchange/keys` | Add API key (encrypted) |
| GET | `/api/exchange/keys` | List API keys |
| DELETE | `/api/exchange/keys/{id}` | Delete API key |
| POST | `/api/exchange/test-connection/{id}` | Test connection |
| GET | `/api/exchange/balance/{id}` | Get balance |

### Trading
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/trading/order` | Place order |
| GET | `/api/trading/positions` | Open positions |
| GET | `/api/trading/history` | Trade history |
| POST | `/api/trading/close/{id}` | Close position |
| POST | `/api/trading/close-all` | Emergency close all |

### AI Signals
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/signals/` | List signals |
| POST | `/api/signals/generate` | Generate AI signal |
| GET | `/api/signals/scanner` | Multi-pair scanner |

### Market Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/market/ticker/{symbol}` | Price ticker |
| GET | `/api/market/klines/{symbol}` | Candlestick data |
| GET | `/api/market/orderbook/{symbol}` | Order book |
| GET | `/api/market/top-movers` | Top movers |
| GET | `/api/market/fear-greed` | Fear & Greed index |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/market/{symbol}?stream=ticker` | Live price |
| `ws://host/ws/market/{symbol}?stream=kline` | Live candles |
| `ws://host/ws/market/{symbol}?stream=depth` | Order book |

## Configuration

### Binance API Setup
1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create a new API key
3. Enable Spot/Futures trading permissions
4. Set IP whitelist (recommended)
5. Add key in BungTrade Exchange page

### Telegram Bot Setup
1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get your Chat ID via [@userinfobot](https://t.me/userinfobot)
3. Add bot token and chat ID in Settings or `.env`

## Security Considerations

- All API keys are encrypted with AES-256 (Fernet)
- Passwords are hashed with bcrypt
- JWT tokens with configurable expiry
- Change `SECRET_KEY` and `ENCRYPTION_KEY` in production
- Use IP whitelist for Binance API keys
- HTTPS recommended for production deployment

## License

MIT License
