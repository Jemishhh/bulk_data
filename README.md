# NSE Bulk Deals Analyzer 📈

A comprehensive Python-based analysis system for NSE (National Stock Exchange) India bulk and block deals data. This tool helps identify major institutional investors, analyze their long-term holdings, backtest performance, and generate actionable investment insights.

## 🎯 Overview

This system analyzes bulk deals data from NSE India to:
- **Identify major institutional funds** and their investment patterns
- **Filter long-term vs short-term trades** to focus on serious investors
- **Backtest portfolio performance** of following institutional strategies
- **Generate real-time trading signals** based on institutional activity
- **Provide actionable investment recommendations** with risk management

## 🚀 Features

### 📊 Data Collection & Analysis
- **Real-time NSE data scraping** from official NSE APIs
- **Historical bulk deals analysis** with customizable date ranges
- **Institutional investor identification** using smart pattern matching
- **Long-term holding analysis** (filters out short-term speculation)

### 🧠 Advanced Analytics
- **4 Different Investment Strategies**:
  1. **Follow Major Institutions** - Copy large institutional buys
  2. **Contrarian Institutional** - Buy when institutions reverse selling
  3. **Momentum Institutional** - Follow increasing institutional interest
  4. **Smart Money Clustering** - Buy when multiple institutions cluster

### 📈 Portfolio Backtesting
- **Performance comparison** across all strategies
- **Risk-adjusted returns** (Sharpe ratio calculation)
- **Drawdown analysis** and risk management
- **Success rate tracking** and trade logging

### 🎯 Trading Signals
- **Real-time buy/sell signals** based on recent institutional activity
- **Signal strength scoring** with detailed reasoning
- **Portfolio allocation recommendations**
- **Risk management guidelines**

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd nse-bulk-deals-analyzer

# Install required packages
pip install -r requirements.txt

# Run the main analyzer
python nse_bulk_deals_analyzer.py
```

### Manual Installation
```bash
pip install pandas numpy yfinance matplotlib seaborn requests beautifulsoup4 lxml openpyxl scipy scikit-learn plotly streamlit
```

## 📖 Usage

### 1. Basic Analysis
```python
from nse_bulk_deals_analyzer import NSEBulkDealsAnalyzer

# Initialize analyzer
analyzer = NSEBulkDealsAnalyzer()

# Fetch and analyze data
bulk_data = analyzer.fetch_bulk_deals_data("2023-01-01", "2023-12-31")
major_funds = analyzer.identify_major_funds(min_deal_value=50000000)  # 5 crores
long_term_holdings = analyzer.filter_long_term_holdings()
```

### 2. Real Data Scraping
```python
from nse_data_scraper import NSEDataScraper

# Initialize scraper
scraper = NSEDataScraper()

# Get recent bulk deals
recent_deals = scraper.get_recent_bulk_deals(days=30)

# Get specific date range
bulk_deals = scraper.fetch_date_range("01-01-2024", "31-01-2024", "bulk")
```

### 3. Strategy Backtesting
```python
from portfolio_backtester import PortfolioBacktester

# Initialize backtester with 10 lakh capital
backtester = PortfolioBacktester(initial_capital=1000000)

# Load your bulk deals data
bulk_deals = backtester.load_bulk_deals_data("bulk_deals.csv")

# Compare all strategies
results = backtester.compare_strategies(bulk_deals)

# Generate current trading signals
signals = backtester.generate_trading_signals(bulk_deals)
```

## 📊 Sample Output

### Strategy Performance Comparison
```
STRATEGY RANKINGS
=====================================
🏆 Best Total Returns:
   1. Smart_Money_Clustering: 23.5%
   2. Follow_Institutions: 18.2%
   3. Momentum_Institutional: 15.7%
   4. Contrarian_Institutional: 12.1%

📊 Best Risk-Adjusted Returns (Sharpe Ratio):
   1. Follow_Institutions: 1.45
   2. Smart_Money_Clustering: 1.32
   3. Momentum_Institutional: 1.18
   4. Contrarian_Institutional: 0.87
```

### Current Trading Signals
```
📈 CURRENT BUY SIGNALS:
   🎯 RELIANCE - STRONG BUY
      Net Flow: ₹127.5 Cr | Institutions: 4
      Reason: Strong institutional buying; Multiple institutions (4) active

   🎯 TCS - BUY
      Net Flow: ₹89.2 Cr | Institutions: 3
      Reason: Moderate institutional buying; Multiple institutions (3) active
```

### Investment Insights
```
💡 ACTIONABLE RECOMMENDATIONS:
   1. FOLLOW THE LEADER:
      → Track 'HDFC Mutual Fund Ltd' (Best Sharpe Ratio: 1.67)
      → Their strategy: 73 days avg holding, 68.4% success rate

   2. OPTIMAL HOLDING PERIOD:
      → (60, 120] days shows best returns (19.3%)

   3. PORTFOLIO ALLOCATION STRATEGY:
      → Allocate 60% to top 3 performing stocks: RELIANCE, TCS, INFY
      → Consider 40% in defensive stocks with consistent institutional buying

   4. RISK MANAGEMENT:
      → Set stop-loss at -15% (Worst institutional loss was -22.1%)
      → Position size: Max 5% per stock based on institutional behavior
```

## 📁 File Structure

```
nse-bulk-deals-analyzer/
│
├── nse_bulk_deals_analyzer.py      # Main analysis engine
├── nse_data_scraper.py             # Real-time NSE data scraper
├── portfolio_backtester.py         # Strategy backtesting system
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/                           # Data storage (created automatically)
│   ├── bulk_deals_*.csv
│   ├── block_deals_*.csv
│   └── analysis_results_*.csv
│
└── outputs/                        # Generated reports and charts
    ├── strategy_comparison.png
    ├── performance_analysis.png
    └── trading_signals.csv
```

## 🎛️ Configuration Options

### Analysis Parameters
```python
# Long-term threshold (days)
analyzer.long_term_threshold = 30  # Default: 30 days

# Minimum deal value for major funds
min_deal_value = 50000000  # 5 crores

# Strategy-specific parameters
holding_period = 60  # Days to hold positions
min_institutions = 3  # Minimum institutions for clustering
momentum_window = 30  # Days for momentum calculation
```

### Data Scraping Settings
```python
# Date format: DD-MM-YYYY
start_date = "01-01-2024"
end_date = "31-12-2024"

# Deal types
deal_type = "bulk"  # or "block"

# Rate limiting
time.sleep(0.5)  # Seconds between requests
```

## 🚨 Important Disclaimers

⚠️ **Investment Risks**
- Past performance does not guarantee future results
- This tool is for educational and research purposes only
- Always consult with qualified financial advisors
- Institutional strategies may not suit retail investors

⚠️ **Data Accuracy**
- Data is sourced from public NSE APIs
- Real-time data may have delays
- Always verify important decisions with official sources

⚠️ **Technical Limitations**
- Internet connection required for data fetching
- Some historical data may be incomplete
- Performance depends on data quality and market conditions

## 🔧 Troubleshooting

### Common Issues

**1. Data Fetching Errors**
```python
# Check internet connection
# Verify NSE website accessibility
# Try increasing sleep time between requests
time.sleep(1.0)
```

**2. Missing Stock Price Data**
```python
# Some stocks may not be available on Yahoo Finance
# Check stock symbol format (should be SYMBOL.NS)
# Verify date ranges are within available data
```

**3. Analysis Errors**
```python
# Ensure sufficient data for analysis
# Check date formats (YYYY-MM-DD for analysis, DD-MM-YYYY for scraping)
# Verify institutional keywords matching
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution
- Additional trading strategies
- Enhanced data sources
- Better visualization tools
- Performance optimizations
- Documentation improvements

## 📞 Support

For questions, issues, or suggestions:
- Create an issue in the repository
- Check existing documentation
- Review troubleshooting section

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🏆 Acknowledgments

- NSE India for providing public market data
- Yahoo Finance API for historical price data
- Python community for excellent libraries
- Contributors and testers

---

**Happy Investing! 🚀📈**

*Remember: The best investment strategy is the one that matches your risk tolerance and investment goals.*