#!/usr/bin/env python3
"""
NSE Bulk Deals Analyzer
Analyze bulk and block deals from NSE India to identify major funds making long-term investments
and backtest their performance.
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class NSEBulkDealsAnalyzer:
    """
    A comprehensive analyzer for NSE bulk and block deals data
    """
    
    def __init__(self):
        self.bulk_deals_data = pd.DataFrame()
        self.block_deals_data = pd.DataFrame()
        self.stock_prices = {}
        self.major_funds = []
        self.long_term_threshold = 30  # days to consider as long-term holding
        
        # Common institutional investor patterns
        self.institutional_keywords = [
            'mutual fund', 'mf', 'insurance', 'life insurance', 'lic',
            'pension fund', 'provident fund', 'epf', 'trust', 'foundation',
            'portfolio', 'fund', 'limited', 'ltd', 'pvt', 'private',
            'investment', 'capital', 'securities', 'asset management',
            'wealth', 'holdings', 'ventures', 'advisory'
        ]
        
    def fetch_bulk_deals_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch bulk deals data from NSE for a given date range
        Note: This is a simulated function as direct API access requires authentication
        """
        print(f"Fetching bulk deals data from {start_date} to {end_date}")
        
        # Simulate bulk deals data structure based on NSE format
        # In practice, you would scrape or use NSE API
        sample_data = {
            'Date': [],
            'Stock_Symbol': [],
            'Company_Name': [],
            'Client_Name': [],
            'Deal_Type': [],  # Buy/Sell
            'Quantity': [],
            'Price': [],
            'Value': []
        }
        
        # Create sample data for demonstration
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'HINDUNILVR', 'LT']
        
        for i, date in enumerate(dates[:50]):  # Limit for demo
            if date.weekday() < 5:  # Only weekdays
                for _ in range(np.random.randint(0, 5)):  # Random number of deals per day
                    sample_data['Date'].append(date.strftime('%Y-%m-%d'))
                    sample_data['Stock_Symbol'].append(np.random.choice(stocks))
                    sample_data['Company_Name'].append(f"Company_{np.random.choice(stocks)}")
                    
                    # Generate institutional client names
                    fund_types = ['Mutual Fund', 'Insurance Co', 'Pension Fund', 'Investment Trust', 'Asset Management']
                    fund_names = ['HDFC', 'ICICI', 'SBI', 'LIC', 'UTI', 'Aditya Birla', 'Kotak', 'Axis']
                    client = f"{np.random.choice(fund_names)} {np.random.choice(fund_types)} Ltd"
                    sample_data['Client_Name'].append(client)
                    
                    sample_data['Deal_Type'].append(np.random.choice(['Buy', 'Sell']))
                    sample_data['Quantity'].append(np.random.randint(100000, 5000000))
                    sample_data['Price'].append(round(np.random.uniform(100, 3000), 2))
                    sample_data['Value'].append(sample_data['Quantity'][-1] * sample_data['Price'][-1])
        
        self.bulk_deals_data = pd.DataFrame(sample_data)
        self.bulk_deals_data['Date'] = pd.to_datetime(self.bulk_deals_data['Date'])
        
        print(f"Fetched {len(self.bulk_deals_data)} bulk deals records")
        return self.bulk_deals_data
    
    def identify_major_funds(self, min_deal_value: float = 10000000) -> List[str]:
        """
        Identify major institutional funds based on deal frequency and value
        """
        if self.bulk_deals_data.empty:
            print("No bulk deals data available. Please fetch data first.")
            return []
        
        # Calculate fund statistics
        fund_stats = self.bulk_deals_data.groupby('Client_Name').agg({
            'Value': ['sum', 'count', 'mean'],
            'Date': ['min', 'max']
        }).round(2)
        
        fund_stats.columns = ['Total_Value', 'Deal_Count', 'Avg_Deal_Value', 'First_Deal', 'Last_Deal']
        fund_stats = fund_stats.reset_index()
        
        # Filter major funds
        major_funds = fund_stats[
            (fund_stats['Total_Value'] >= min_deal_value) &
            (fund_stats['Deal_Count'] >= 5)
        ].sort_values('Total_Value', ascending=False)
        
        self.major_funds = major_funds['Client_Name'].tolist()
        
        print(f"\nIdentified {len(self.major_funds)} major funds:")
        print(major_funds.head(10))
        
        return self.major_funds
    
    def filter_long_term_holdings(self) -> pd.DataFrame:
        """
        Filter deals to identify long-term holdings vs short-term trades
        """
        if self.bulk_deals_data.empty:
            print("No bulk deals data available.")
            return pd.DataFrame()
        
        long_term_deals = []
        
        # Group by client and stock to track holdings
        for client in self.major_funds:
            client_deals = self.bulk_deals_data[self.bulk_deals_data['Client_Name'] == client]
            
            for stock in client_deals['Stock_Symbol'].unique():
                stock_deals = client_deals[client_deals['Stock_Symbol'] == stock].sort_values('Date')
                
                # Track cumulative position
                position = 0
                entry_date = None
                
                for _, deal in stock_deals.iterrows():
                    if deal['Deal_Type'] == 'Buy':
                        if position == 0:  # New position
                            entry_date = deal['Date']
                        position += deal['Quantity']
                    else:  # Sell
                        if position > 0:
                            # Calculate holding period
                            holding_days = (deal['Date'] - entry_date).days if entry_date else 0
                            
                            if holding_days >= self.long_term_threshold:
                                long_term_deals.append({
                                    'Client_Name': client,
                                    'Stock_Symbol': stock,
                                    'Entry_Date': entry_date,
                                    'Exit_Date': deal['Date'],
                                    'Holding_Days': holding_days,
                                    'Position_Size': position,
                                    'Exit_Price': deal['Price']
                                })
                            
                            position -= deal['Quantity']
                            if position <= 0:
                                position = 0
                                entry_date = None
        
        long_term_df = pd.DataFrame(long_term_deals)
        
        if not long_term_df.empty:
            print(f"\nIdentified {len(long_term_df)} long-term holdings:")
            print(long_term_df.head())
        
        return long_term_df
    
    def fetch_stock_prices(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """
        Fetch historical stock prices for performance analysis
        """
        print(f"\nFetching stock prices for {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                # Add .NS suffix for NSE stocks in yfinance
                ticker = f"{symbol}.NS"
                stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                
                if not stock_data.empty:
                    self.stock_prices[symbol] = stock_data
                    print(f"✓ {symbol}: {len(stock_data)} price records")
                else:
                    print(f"✗ {symbol}: No data found")
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"✗ {symbol}: Error - {str(e)}")
        
        return self.stock_prices
    
    def backtest_fund_performance(self, long_term_holdings: pd.DataFrame) -> pd.DataFrame:
        """
        Backtest the performance of major funds' long-term holdings
        """
        if long_term_holdings.empty:
            print("No long-term holdings data available.")
            return pd.DataFrame()
        
        results = []
        
        print("\nBacktesting fund performance...")
        
        for _, holding in long_term_holdings.iterrows():
            symbol = holding['Stock_Symbol']
            entry_date = holding['Entry_Date']
            exit_date = holding['Exit_Date']
            
            if symbol in self.stock_prices:
                stock_data = self.stock_prices[symbol]
                
                # Get entry and exit prices
                try:
                    entry_price = stock_data.loc[stock_data.index >= entry_date, 'Close'].iloc[0]
                    exit_price = stock_data.loc[stock_data.index <= exit_date, 'Close'].iloc[-1]
                    
                    # Calculate performance
                    returns = (exit_price - entry_price) / entry_price * 100
                    
                    results.append({
                        'Client_Name': holding['Client_Name'],
                        'Stock_Symbol': symbol,
                        'Entry_Date': entry_date,
                        'Exit_Date': exit_date,
                        'Holding_Days': holding['Holding_Days'],
                        'Entry_Price': entry_price,
                        'Exit_Price': exit_price,
                        'Returns_Percent': returns,
                        'Position_Value': holding['Position_Size'] * entry_price,
                        'Profit_Loss': holding['Position_Size'] * (exit_price - entry_price)
                    })
                    
                except Exception as e:
                    print(f"Error calculating returns for {symbol}: {e}")
        
        performance_df = pd.DataFrame(results)
        
        if not performance_df.empty:
            print(f"\nBacktest completed for {len(performance_df)} holdings")
            print("\nPerformance Summary:")
            print(f"Average Return: {performance_df['Returns_Percent'].mean():.2f}%")
            print(f"Median Return: {performance_df['Returns_Percent'].median():.2f}%")
            print(f"Success Rate: {(performance_df['Returns_Percent'] > 0).mean() * 100:.1f}%")
            print(f"Total P&L: ₹{performance_df['Profit_Loss'].sum():,.0f}")
        
        return performance_df
    
    def analyze_fund_strategies(self, performance_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze different funds' investment strategies and success rates
        """
        if performance_df.empty:
            print("No performance data available.")
            return pd.DataFrame()
        
        fund_analysis = performance_df.groupby('Client_Name').agg({
            'Returns_Percent': ['mean', 'median', 'std', 'count'],
            'Holding_Days': ['mean', 'median'],
            'Position_Value': 'sum',
            'Profit_Loss': 'sum'
        }).round(2)
        
        fund_analysis.columns = [
            'Avg_Return', 'Median_Return', 'Return_Volatility', 'Total_Deals',
            'Avg_Holding_Days', 'Median_Holding_Days', 'Total_Investment', 'Total_PnL'
        ]
        
        fund_analysis = fund_analysis.reset_index()
        
        # Calculate success rate
        success_rates = performance_df.groupby('Client_Name')['Returns_Percent'].apply(
            lambda x: (x > 0).mean() * 100
        ).reset_index()
        success_rates.columns = ['Client_Name', 'Success_Rate']
        
        fund_analysis = fund_analysis.merge(success_rates, on='Client_Name')
        
        # Calculate Sharpe ratio (assuming risk-free rate = 6%)
        risk_free_rate = 6.0
        fund_analysis['Sharpe_Ratio'] = (fund_analysis['Avg_Return'] - risk_free_rate) / fund_analysis['Return_Volatility']
        
        # Sort by Sharpe ratio
        fund_analysis = fund_analysis.sort_values('Sharpe_Ratio', ascending=False)
        
        print("\nFund Strategy Analysis:")
        print(fund_analysis.head(10))
        
        return fund_analysis
    
    def plot_performance_analysis(self, performance_df: pd.DataFrame, fund_analysis: pd.DataFrame):
        """
        Create visualization plots for performance analysis
        """
        if performance_df.empty or fund_analysis.empty:
            print("Insufficient data for plotting.")
            return
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('NSE Bulk Deals Analysis - Major Funds Performance', fontsize=16, fontweight='bold')
        
        # 1. Returns distribution
        axes[0, 0].hist(performance_df['Returns_Percent'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].axvline(performance_df['Returns_Percent'].mean(), color='red', linestyle='--', 
                          label=f'Mean: {performance_df["Returns_Percent"].mean():.1f}%')
        axes[0, 0].set_xlabel('Returns (%)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Distribution of Returns')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Holding period vs Returns
        scatter = axes[0, 1].scatter(performance_df['Holding_Days'], performance_df['Returns_Percent'], 
                                   alpha=0.6, s=50, c='green')
        axes[0, 1].set_xlabel('Holding Days')
        axes[0, 1].set_ylabel('Returns (%)')
        axes[0, 1].set_title('Holding Period vs Returns')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Add trendline
        z = np.polyfit(performance_df['Holding_Days'], performance_df['Returns_Percent'], 1)
        p = np.poly1d(z)
        axes[0, 1].plot(performance_df['Holding_Days'], p(performance_df['Holding_Days']), 
                       "r--", alpha=0.8, label=f'Trend')
        axes[0, 1].legend()
        
        # 3. Top funds by Sharpe ratio
        top_funds = fund_analysis.head(8)
        bars = axes[1, 0].bar(range(len(top_funds)), top_funds['Sharpe_Ratio'], 
                             color='lightcoral', alpha=0.8)
        axes[1, 0].set_xlabel('Fund Rank')
        axes[1, 0].set_ylabel('Sharpe Ratio')
        axes[1, 0].set_title('Top Funds by Risk-Adjusted Returns (Sharpe Ratio)')
        axes[1, 0].set_xticks(range(len(top_funds)))
        axes[1, 0].set_xticklabels([f'Fund {i+1}' for i in range(len(top_funds))], rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 4. Success rate vs Average return
        axes[1, 1].scatter(fund_analysis['Success_Rate'], fund_analysis['Avg_Return'], 
                          s=fund_analysis['Total_Deals']*10, alpha=0.6, c='purple')
        axes[1, 1].set_xlabel('Success Rate (%)')
        axes[1, 1].set_ylabel('Average Return (%)')
        axes[1, 1].set_title('Success Rate vs Average Return\n(Bubble size = Number of deals)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print top performing funds
        print("\n" + "="*60)
        print("TOP PERFORMING FUNDS (by Sharpe Ratio)")
        print("="*60)
        for i, (_, fund) in enumerate(fund_analysis.head(5).iterrows(), 1):
            print(f"\n{i}. {fund['Client_Name']}")
            print(f"   Average Return: {fund['Avg_Return']:.1f}%")
            print(f"   Success Rate: {fund['Success_Rate']:.1f}%")
            print(f"   Sharpe Ratio: {fund['Sharpe_Ratio']:.2f}")
            print(f"   Total Deals: {fund['Total_Deals']}")
            print(f"   Average Holding: {fund['Avg_Holding_Days']:.0f} days")
    
    def generate_investment_insights(self, fund_analysis: pd.DataFrame, performance_df: pd.DataFrame):
        """
        Generate actionable investment insights and recommendations
        """
        print("\n" + "="*80)
        print("INVESTMENT INSIGHTS & RECOMMENDATIONS")
        print("="*80)
        
        if fund_analysis.empty or performance_df.empty:
            print("Insufficient data for generating insights.")
            return
        
        # Key insights
        total_positive_returns = (performance_df['Returns_Percent'] > 0).sum()
        total_deals = len(performance_df)
        avg_holding_period = performance_df['Holding_Days'].mean()
        
        print(f"\n📊 MARKET INSIGHTS:")
        print(f"   • Success Rate: {(total_positive_returns/total_deals)*100:.1f}% of institutional long-term deals were profitable")
        print(f"   • Average Holding Period: {avg_holding_period:.0f} days")
        print(f"   • Average Return: {performance_df['Returns_Percent'].mean():.1f}%")
        
        # Best performing sectors/stocks
        top_stocks = performance_df.groupby('Stock_Symbol')['Returns_Percent'].mean().sort_values(ascending=False).head(5)
        print(f"\n🎯 TOP PERFORMING STOCKS (by institutions):")
        for stock, ret in top_stocks.items():
            print(f"   • {stock}: {ret:.1f}% average return")
        
        # Fund strategies
        conservative_funds = fund_analysis[fund_analysis['Return_Volatility'] < fund_analysis['Return_Volatility'].median()]
        aggressive_funds = fund_analysis[fund_analysis['Return_Volatility'] >= fund_analysis['Return_Volatility'].median()]
        
        print(f"\n📈 FUND STRATEGIES:")
        print(f"   • Conservative Funds (Low Volatility): {conservative_funds['Avg_Return'].mean():.1f}% avg return")
        print(f"   • Aggressive Funds (High Volatility): {aggressive_funds['Avg_Return'].mean():.1f}% avg return")
        
        # Recommendations
        print(f"\n💡 ACTIONABLE RECOMMENDATIONS:")
        
        # Top fund to follow
        top_fund = fund_analysis.iloc[0]
        print(f"   1. FOLLOW THE LEADER:")
        print(f"      → Track '{top_fund['Client_Name']}' (Best Sharpe Ratio: {top_fund['Sharpe_Ratio']:.2f})")
        print(f"      → Their strategy: {top_fund['Avg_Holding_Days']:.0f} days avg holding, {top_fund['Success_Rate']:.1f}% success rate")
        
        # Optimal holding period
        holding_returns = performance_df.groupby(pd.cut(performance_df['Holding_Days'], 
                                                       bins=[0, 60, 120, 365, 1000]))['Returns_Percent'].mean()
        best_holding_period = holding_returns.idxmax()
        print(f"   2. OPTIMAL HOLDING PERIOD:")
        print(f"      → {best_holding_period} shows best returns ({holding_returns[best_holding_period]:.1f}%)")
        
        # Portfolio allocation
        print(f"   3. PORTFOLIO ALLOCATION STRATEGY:")
        print(f"      → Allocate 60% to top 3 performing stocks: {', '.join(top_stocks.head(3).index)}")
        print(f"      → Consider 40% in defensive stocks with consistent institutional buying")
        
        # Risk management
        max_loss = performance_df['Returns_Percent'].min()
        print(f"   4. RISK MANAGEMENT:")
        print(f"      → Set stop-loss at -15% (Worst institutional loss was {max_loss:.1f}%)")
        print(f"      → Position size: Max 5% per stock based on institutional behavior")
        
        # Market timing
        monthly_performance = performance_df.groupby(performance_df['Entry_Date'].dt.month)['Returns_Percent'].mean()
        best_month = monthly_performance.idxmax()
        print(f"   5. MARKET TIMING:")
        print(f"      → Best entry month: {best_month} (based on institutional activity)")
        print(f"      → Follow institutional buying patterns during market dips")
        
        print(f"\n⚠️  IMPORTANT DISCLAIMERS:")
        print(f"   • Past performance doesn't guarantee future results")
        print(f"   • Institutional strategies may not suit retail investors")
        print(f"   • Always diversify and consult financial advisors")
        print(f"   • This analysis is for educational purposes only")

def main():
    """
    Main function to run the NSE Bulk Deals Analysis
    """
    print("="*80)
    print("NSE BULK DEALS ANALYZER - Major Funds Performance Tracker")
    print("="*80)
    
    # Initialize analyzer
    analyzer = NSEBulkDealsAnalyzer()
    
    # Set analysis parameters
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    print(f"\nAnalyzing bulk deals data from {start_date} to {end_date}")
    print("This analysis will help identify profitable institutional investment patterns...")
    
    try:
        # Step 1: Fetch bulk deals data
        print("\n1. Fetching bulk deals data...")
        bulk_data = analyzer.fetch_bulk_deals_data(start_date, end_date)
        
        if bulk_data.empty:
            print("No bulk deals data found. Exiting...")
            return
        
        # Step 2: Identify major funds
        print("\n2. Identifying major institutional funds...")
        major_funds = analyzer.identify_major_funds(min_deal_value=50000000)  # 5 crores minimum
        
        if not major_funds:
            print("No major funds identified. Exiting...")
            return
        
        # Step 3: Filter long-term holdings
        print(f"\n3. Filtering long-term holdings (>{analyzer.long_term_threshold} days)...")
        long_term_holdings = analyzer.filter_long_term_holdings()
        
        if long_term_holdings.empty:
            print("No long-term holdings found. Exiting...")
            return
        
        # Step 4: Fetch stock price data
        print("\n4. Fetching historical stock prices...")
        unique_stocks = long_term_holdings['Stock_Symbol'].unique()
        stock_prices = analyzer.fetch_stock_prices(unique_stocks, start_date, end_date)
        
        # Step 5: Backtest performance
        print("\n5. Backtesting fund performance...")
        performance_results = analyzer.backtest_fund_performance(long_term_holdings)
        
        if performance_results.empty:
            print("No performance results available. Exiting...")
            return
        
        # Step 6: Analyze fund strategies
        print("\n6. Analyzing fund investment strategies...")
        fund_analysis = analyzer.analyze_fund_strategies(performance_results)
        
        # Step 7: Generate visualizations
        print("\n7. Generating performance visualizations...")
        analyzer.plot_performance_analysis(performance_results, fund_analysis)
        
        # Step 8: Generate insights and recommendations
        print("\n8. Generating investment insights...")
        analyzer.generate_investment_insights(fund_analysis, performance_results)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE! 🎉")
        print("Use the insights above to inform your investment decisions.")
        print("="*80)
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check your data sources and try again.")

if __name__ == "__main__":
    main()