#!/usr/bin/env python3
"""
Portfolio Backtester for Institutional Strategies
Advanced backtesting system to test various investment strategies based on NSE bulk deals data
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PortfolioBacktester:
    """
    Advanced portfolio backtester for institutional investment strategies
    """
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.portfolio_history = []
        self.trades_log = []
        self.benchmark_data = None
        
    def load_bulk_deals_data(self, file_path: str) -> pd.DataFrame:
        """Load bulk deals data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'] if 'date' in df.columns else df['trade_date'])
            print(f"✓ Loaded {len(df)} bulk deals records")
            return df
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return pd.DataFrame()
    
    def strategy_follow_institutions(self, bulk_deals: pd.DataFrame, 
                                   min_deal_value: float = 10000000,
                                   holding_period: int = 60) -> Dict:
        """
        Strategy 1: Follow major institutional buyers
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            min_deal_value: Minimum deal value to consider (default: 1 crore)
            holding_period: Days to hold the position
            
        Returns:
            Dictionary with strategy results
        """
        print(f"\n🔄 Running Strategy: Follow Major Institutions")
        print(f"   Min Deal Value: ₹{min_deal_value:,.0f}")
        print(f"   Holding Period: {holding_period} days")
        
        # Filter major institutional buys
        institutional_keywords = ['mutual fund', 'insurance', 'pension', 'trust', 'fund', 'ltd', 'limited']
        major_buys = bulk_deals[
            (bulk_deals['deal_type'].str.lower() == 'buy') &
            (bulk_deals['value'] >= min_deal_value) &
            (bulk_deals['client_name'].str.lower().str.contains('|'.join(institutional_keywords), na=False))
        ].copy()
        
        if major_buys.empty:
            return {'total_return': 0, 'trades': 0, 'success_rate': 0}
        
        # Group by stock and take the earliest institutional buy
        major_buys = major_buys.sort_values('date').groupby('symbol').first().reset_index()
        
        results = self._backtest_positions(major_buys, holding_period)
        
        print(f"   📊 Results: {results['success_rate']:.1f}% success rate, {results['total_return']:.2f}% return")
        return results
    
    def strategy_contrarian_institutional(self, bulk_deals: pd.DataFrame,
                                        min_consecutive_buys: int = 3,
                                        holding_period: int = 90) -> Dict:
        """
        Strategy 2: Contrarian - Buy when institutions are selling heavily
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            min_consecutive_buys: Minimum institutional buys after heavy selling
            holding_period: Days to hold the position
            
        Returns:
            Dictionary with strategy results
        """
        print(f"\n🔄 Running Strategy: Contrarian Institutional")
        print(f"   Min Consecutive Buys: {min_consecutive_buys}")
        print(f"   Holding Period: {holding_period} days")
        
        # Find stocks with heavy institutional selling followed by buying
        institutional_keywords = ['mutual fund', 'insurance', 'pension', 'trust', 'fund', 'ltd', 'limited']
        institutional_deals = bulk_deals[
            bulk_deals['client_name'].str.lower().str.contains('|'.join(institutional_keywords), na=False)
        ].copy()
        
        contrarian_picks = []
        
        for symbol in institutional_deals['symbol'].unique():
            symbol_deals = institutional_deals[institutional_deals['symbol'] == symbol].sort_values('date')
            
            # Look for pattern: heavy selling followed by consistent buying
            for i in range(len(symbol_deals) - min_consecutive_buys):
                # Check if there are consecutive buys after this point
                future_deals = symbol_deals.iloc[i:i+min_consecutive_buys+1]
                buy_ratio = (future_deals['deal_type'].str.lower() == 'buy').mean()
                
                if buy_ratio >= 0.7:  # 70% of recent deals are buys
                    contrarian_picks.append(symbol_deals.iloc[i])
                    break
        
        if not contrarian_picks:
            return {'total_return': 0, 'trades': 0, 'success_rate': 0}
        
        contrarian_df = pd.DataFrame(contrarian_picks)
        results = self._backtest_positions(contrarian_df, holding_period)
        
        print(f"   📊 Results: {results['success_rate']:.1f}% success rate, {results['total_return']:.2f}% return")
        return results
    
    def strategy_momentum_institutional(self, bulk_deals: pd.DataFrame,
                                      momentum_window: int = 30,
                                      holding_period: int = 45) -> Dict:
        """
        Strategy 3: Momentum - Buy stocks with increasing institutional interest
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            momentum_window: Days to look back for momentum calculation
            holding_period: Days to hold the position
            
        Returns:
            Dictionary with strategy results
        """
        print(f"\n🔄 Running Strategy: Institutional Momentum")
        print(f"   Momentum Window: {momentum_window} days")
        print(f"   Holding Period: {holding_period} days")
        
        institutional_keywords = ['mutual fund', 'insurance', 'pension', 'trust', 'fund', 'ltd', 'limited']
        institutional_deals = bulk_deals[
            bulk_deals['client_name'].str.lower().str.contains('|'.join(institutional_keywords), na=False)
        ].copy()
        
        momentum_picks = []
        
        for symbol in institutional_deals['symbol'].unique():
            symbol_deals = institutional_deals[institutional_deals['symbol'] == symbol].sort_values('date')
            
            # Calculate momentum (increasing institutional activity)
            for i in range(momentum_window, len(symbol_deals)):
                recent_deals = symbol_deals.iloc[i-momentum_window:i]
                older_deals = symbol_deals.iloc[max(0, i-2*momentum_window):i-momentum_window]
                
                if len(recent_deals) > len(older_deals) and len(recent_deals) >= 3:
                    # Increasing activity
                    recent_buy_ratio = (recent_deals['deal_type'].str.lower() == 'buy').mean()
                    
                    if recent_buy_ratio > 0.6:  # More buys than sells
                        momentum_picks.append(symbol_deals.iloc[i-1])
                        break
        
        if not momentum_picks:
            return {'total_return': 0, 'trades': 0, 'success_rate': 0}
        
        momentum_df = pd.DataFrame(momentum_picks)
        results = self._backtest_positions(momentum_df, holding_period)
        
        print(f"   📊 Results: {results['success_rate']:.1f}% success rate, {results['total_return']:.2f}% return")
        return results
    
    def strategy_smart_money_clustering(self, bulk_deals: pd.DataFrame,
                                      min_institutions: int = 3,
                                      time_window: int = 15,
                                      holding_period: int = 75) -> Dict:
        """
        Strategy 4: Smart Money Clustering - Buy when multiple institutions buy same stock
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            min_institutions: Minimum number of different institutions buying
            time_window: Days window for clustering analysis
            holding_period: Days to hold the position
            
        Returns:
            Dictionary with strategy results
        """
        print(f"\n🔄 Running Strategy: Smart Money Clustering")
        print(f"   Min Institutions: {min_institutions}")
        print(f"   Time Window: {time_window} days")
        print(f"   Holding Period: {holding_period} days")
        
        institutional_keywords = ['mutual fund', 'insurance', 'pension', 'trust', 'fund', 'ltd', 'limited']
        institutional_deals = bulk_deals[
            (bulk_deals['client_name'].str.lower().str.contains('|'.join(institutional_keywords), na=False)) &
            (bulk_deals['deal_type'].str.lower() == 'buy')
        ].copy()
        
        clustering_picks = []
        
        for symbol in institutional_deals['symbol'].unique():
            symbol_deals = institutional_deals[institutional_deals['symbol'] == symbol].sort_values('date')
            
            # Find clustering of institutional buys
            for i, deal in symbol_deals.iterrows():
                window_start = deal['date']
                window_end = window_start + timedelta(days=time_window)
                
                window_deals = symbol_deals[
                    (symbol_deals['date'] >= window_start) &
                    (symbol_deals['date'] <= window_end)
                ]
                
                unique_institutions = window_deals['client_name'].nunique()
                
                if unique_institutions >= min_institutions:
                    clustering_picks.append(deal)
                    break
        
        if not clustering_picks:
            return {'total_return': 0, 'trades': 0, 'success_rate': 0}
        
        clustering_df = pd.DataFrame(clustering_picks)
        results = self._backtest_positions(clustering_df, holding_period)
        
        print(f"   📊 Results: {results['success_rate']:.1f}% success rate, {results['total_return']:.2f}% return")
        return results
    
    def _backtest_positions(self, positions_df: pd.DataFrame, holding_period: int) -> Dict:
        """
        Backtest a set of positions
        
        Args:
            positions_df: DataFrame with positions to test
            holding_period: Days to hold each position
            
        Returns:
            Dictionary with backtest results
        """
        if positions_df.empty:
            return {'total_return': 0, 'trades': 0, 'success_rate': 0, 'avg_return': 0, 'max_drawdown': 0}
        
        successful_trades = 0
        total_trades = 0
        total_return = 0
        trade_returns = []
        
        portfolio_value = self.initial_capital
        max_portfolio_value = portfolio_value
        max_drawdown = 0
        
        for _, position in positions_df.iterrows():
            try:
                symbol = position['symbol']
                entry_date = position['date']
                exit_date = entry_date + timedelta(days=holding_period)
                
                # Fetch stock data
                ticker = f"{symbol}.NS"
                stock_data = yf.download(ticker, 
                                       start=entry_date - timedelta(days=5),
                                       end=exit_date + timedelta(days=5),
                                       progress=False)
                
                if stock_data.empty:
                    continue
                
                # Get entry and exit prices
                entry_price = self._get_closest_price(stock_data, entry_date)
                exit_price = self._get_closest_price(stock_data, exit_date)
                
                if entry_price is None or exit_price is None:
                    continue
                
                # Calculate return
                trade_return = (exit_price - entry_price) / entry_price * 100
                trade_returns.append(trade_return)
                
                # Update portfolio
                position_size = 0.05  # 5% of portfolio per position
                position_value = portfolio_value * position_size
                position_return = position_value * (trade_return / 100)
                portfolio_value += position_return
                
                # Track drawdown
                if portfolio_value > max_portfolio_value:
                    max_portfolio_value = portfolio_value
                else:
                    current_drawdown = (max_portfolio_value - portfolio_value) / max_portfolio_value * 100
                    max_drawdown = max(max_drawdown, current_drawdown)
                
                total_return += trade_return
                total_trades += 1
                
                if trade_return > 0:
                    successful_trades += 1
                
                # Log trade
                self.trades_log.append({
                    'symbol': symbol,
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return_pct': trade_return,
                    'portfolio_value': portfolio_value
                })
                
            except Exception as e:
                continue
        
        success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        avg_return = np.mean(trade_returns) if trade_returns else 0
        total_portfolio_return = (portfolio_value - self.initial_capital) / self.initial_capital * 100
        
        return {
            'total_return': total_portfolio_return,
            'avg_return': avg_return,
            'trades': total_trades,
            'success_rate': success_rate,
            'max_drawdown': max_drawdown,
            'final_portfolio_value': portfolio_value,
            'trade_returns': trade_returns
        }
    
    def _get_closest_price(self, stock_data: pd.DataFrame, target_date: datetime) -> Optional[float]:
        """Get the closest available price to the target date"""
        try:
            # Convert target_date to pandas timestamp if it's not already
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date)
            
            # Find the closest date
            closest_date = stock_data.index[stock_data.index.get_indexer([target_date], method='nearest')[0]]
            return float(stock_data.loc[closest_date, 'Close'])
        except:
            return None
    
    def compare_strategies(self, bulk_deals: pd.DataFrame) -> pd.DataFrame:
        """
        Compare all strategies and return results
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            
        Returns:
            DataFrame with strategy comparison
        """
        print("\n" + "="*80)
        print("STRATEGY COMPARISON - INSTITUTIONAL FOLLOWING BACKTESTS")
        print("="*80)
        
        # Reset for each strategy
        strategies = {}
        
        # Strategy 1: Follow Major Institutions
        self.trades_log = []
        strategies['Follow_Institutions'] = self.strategy_follow_institutions(bulk_deals)
        
        # Strategy 2: Contrarian Institutional
        self.trades_log = []
        strategies['Contrarian_Institutional'] = self.strategy_contrarian_institutional(bulk_deals)
        
        # Strategy 3: Momentum Institutional
        self.trades_log = []
        strategies['Momentum_Institutional'] = self.strategy_momentum_institutional(bulk_deals)
        
        # Strategy 4: Smart Money Clustering
        self.trades_log = []
        strategies['Smart_Money_Clustering'] = self.strategy_smart_money_clustering(bulk_deals)
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(strategies).T
        comparison_df = comparison_df.round(2)
        
        # Add Sharpe ratio calculation
        for strategy_name in comparison_df.index:
            trade_returns = strategies[strategy_name].get('trade_returns', [])
            if trade_returns:
                sharpe_ratio = (np.mean(trade_returns) - 6) / np.std(trade_returns) if np.std(trade_returns) > 0 else 0
                comparison_df.loc[strategy_name, 'sharpe_ratio'] = round(sharpe_ratio, 2)
            else:
                comparison_df.loc[strategy_name, 'sharpe_ratio'] = 0
        
        return comparison_df
    
    def plot_strategy_comparison(self, comparison_df: pd.DataFrame):
        """
        Create visualization comparing different strategies
        
        Args:
            comparison_df: DataFrame with strategy comparison results
        """
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Institutional Investment Strategies - Performance Comparison', 
                     fontsize=16, fontweight='bold')
        
        # 1. Total Returns
        axes[0, 0].bar(comparison_df.index, comparison_df['total_return'], 
                       color=['skyblue', 'lightcoral', 'lightgreen', 'orange'], alpha=0.8)
        axes[0, 0].set_title('Total Portfolio Returns (%)')
        axes[0, 0].set_ylabel('Return (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(comparison_df['total_return']):
            axes[0, 0].text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 2. Success Rates
        axes[0, 1].bar(comparison_df.index, comparison_df['success_rate'], 
                       color=['purple', 'brown', 'pink', 'gray'], alpha=0.8)
        axes[0, 1].set_title('Success Rate (%)')
        axes[0, 1].set_ylabel('Success Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(comparison_df['success_rate']):
            axes[0, 1].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 3. Risk-Adjusted Returns (Sharpe Ratio)
        axes[1, 0].bar(comparison_df.index, comparison_df['sharpe_ratio'], 
                       color=['gold', 'silver', 'bronze', 'darkblue'], alpha=0.8)
        axes[1, 0].set_title('Risk-Adjusted Returns (Sharpe Ratio)')
        axes[1, 0].set_ylabel('Sharpe Ratio')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(comparison_df['sharpe_ratio']):
            axes[1, 0].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Number of Trades
        axes[1, 1].bar(comparison_df.index, comparison_df['trades'], 
                       color=['red', 'blue', 'green', 'yellow'], alpha=0.8)
        axes[1, 1].set_title('Number of Trades')
        axes[1, 1].set_ylabel('Trade Count')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(comparison_df['trades']):
            axes[1, 1].text(i, v + 0.5, f'{int(v)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        # Print detailed comparison
        print("\n" + "="*100)
        print("DETAILED STRATEGY PERFORMANCE COMPARISON")
        print("="*100)
        print(comparison_df.to_string())
        
        # Rank strategies
        print("\n" + "="*60)
        print("STRATEGY RANKINGS")
        print("="*60)
        
        # Rank by total return
        return_ranking = comparison_df.sort_values('total_return', ascending=False)
        print("\n🏆 Best Total Returns:")
        for i, (strategy, row) in enumerate(return_ranking.iterrows(), 1):
            print(f"   {i}. {strategy}: {row['total_return']:.1f}%")
        
        # Rank by Sharpe ratio
        sharpe_ranking = comparison_df.sort_values('sharpe_ratio', ascending=False)
        print("\n📊 Best Risk-Adjusted Returns (Sharpe Ratio):")
        for i, (strategy, row) in enumerate(sharpe_ranking.iterrows(), 1):
            print(f"   {i}. {strategy}: {row['sharpe_ratio']:.2f}")
        
        # Rank by success rate
        success_ranking = comparison_df.sort_values('success_rate', ascending=False)
        print("\n✅ Best Success Rate:")
        for i, (strategy, row) in enumerate(success_ranking.iterrows(), 1):
            print(f"   {i}. {strategy}: {row['success_rate']:.1f}%")
    
    def generate_trading_signals(self, bulk_deals: pd.DataFrame) -> pd.DataFrame:
        """
        Generate current trading signals based on recent institutional activity
        
        Args:
            bulk_deals: DataFrame with bulk deals data
            
        Returns:
            DataFrame with current trading recommendations
        """
        print("\n" + "="*80)
        print("CURRENT TRADING SIGNALS - Based on Recent Institutional Activity")
        print("="*80)
        
        # Get recent data (last 30 days)
        recent_date = bulk_deals['date'].max()
        cutoff_date = recent_date - timedelta(days=30)
        recent_deals = bulk_deals[bulk_deals['date'] >= cutoff_date]
        
        institutional_keywords = ['mutual fund', 'insurance', 'pension', 'trust', 'fund', 'ltd', 'limited']
        institutional_deals = recent_deals[
            recent_deals['client_name'].str.lower().str.contains('|'.join(institutional_keywords), na=False)
        ]
        
        signals = []
        
        # Analyze each stock for signals
        for symbol in institutional_deals['symbol'].unique():
            symbol_deals = institutional_deals[institutional_deals['symbol'] == symbol]
            
            # Calculate metrics
            total_value = symbol_deals['value'].sum()
            buy_value = symbol_deals[symbol_deals['deal_type'].str.lower() == 'buy']['value'].sum()
            sell_value = symbol_deals[symbol_deals['deal_type'].str.lower() == 'sell']['value'].sum()
            
            net_institutional_flow = buy_value - sell_value
            unique_institutions = symbol_deals['client_name'].nunique()
            
            # Generate signal
            signal_strength = 0
            signal_type = "HOLD"
            reasoning = []
            
            if net_institutional_flow > 50000000:  # 5 crores net buying
                signal_strength += 3
                reasoning.append("Strong institutional buying")
            elif net_institutional_flow > 10000000:  # 1 crore net buying
                signal_strength += 2
                reasoning.append("Moderate institutional buying")
            elif net_institutional_flow < -50000000:  # 5 crores net selling
                signal_strength -= 2
                reasoning.append("Heavy institutional selling")
            
            if unique_institutions >= 3:
                signal_strength += 2
                reasoning.append(f"Multiple institutions ({unique_institutions}) active")
            
            # Determine signal
            if signal_strength >= 3:
                signal_type = "STRONG BUY"
            elif signal_strength >= 1:
                signal_type = "BUY"
            elif signal_strength <= -2:
                signal_type = "SELL"
            
            if signal_type != "HOLD":
                signals.append({
                    'symbol': symbol,
                    'signal': signal_type,
                    'signal_strength': signal_strength,
                    'net_flow_cr': net_institutional_flow / 10000000,  # In crores
                    'institutions_count': unique_institutions,
                    'total_value_cr': total_value / 10000000,  # In crores
                    'reasoning': '; '.join(reasoning)
                })
        
        signals_df = pd.DataFrame(signals)
        
        if not signals_df.empty:
            signals_df = signals_df.sort_values('signal_strength', ascending=False)
            
            print(f"\n📈 CURRENT BUY SIGNALS:")
            buy_signals = signals_df[signals_df['signal'].str.contains('BUY')]
            if not buy_signals.empty:
                for _, signal in buy_signals.iterrows():
                    print(f"   🎯 {signal['symbol']} - {signal['signal']}")
                    print(f"      Net Flow: ₹{signal['net_flow_cr']:.1f} Cr | Institutions: {signal['institutions_count']}")
                    print(f"      Reason: {signal['reasoning']}")
                    print()
            else:
                print("   No strong buy signals currently")
            
            print(f"\n📉 CURRENT SELL SIGNALS:")
            sell_signals = signals_df[signals_df['signal'] == 'SELL']
            if not sell_signals.empty:
                for _, signal in sell_signals.iterrows():
                    print(f"   ⚠️ {signal['symbol']} - {signal['signal']}")
                    print(f"      Net Flow: ₹{signal['net_flow_cr']:.1f} Cr | Institutions: {signal['institutions_count']}")
                    print(f"      Reason: {signal['reasoning']}")
                    print()
            else:
                print("   No sell signals currently")
        else:
            print("   No significant signals found based on recent institutional activity")
        
        return signals_df

def main():
    """
    Main function to run the portfolio backtester
    """
    print("="*80)
    print("INSTITUTIONAL INVESTMENT STRATEGIES - PORTFOLIO BACKTESTER")
    print("="*80)
    
    # Initialize backtester
    backtester = PortfolioBacktester(initial_capital=1000000)  # 10 lakh starting capital
    
    # For demonstration, create sample bulk deals data
    # In practice, you would load real data using:
    # bulk_deals = backtester.load_bulk_deals_data("bulk_deals.csv")
    
    # Create sample data
    print("Creating sample bulk deals data for demonstration...")
    sample_data = create_sample_bulk_deals_data()
    
    # Run strategy comparison
    comparison_results = backtester.compare_strategies(sample_data)
    
    # Plot results
    backtester.plot_strategy_comparison(comparison_results)
    
    # Generate trading signals
    trading_signals = backtester.generate_trading_signals(sample_data)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("Use the strategies and signals above to inform your investment decisions.")
    print("⚠️ This is for educational purposes only. Past performance doesn't guarantee future results.")
    print("="*80)

def create_sample_bulk_deals_data() -> pd.DataFrame:
    """Create sample bulk deals data for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    # Sample stocks
    stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC']
    
    # Sample institutional names
    institutions = [
        'HDFC Mutual Fund Ltd', 'ICICI Prudential Insurance Ltd', 'SBI Pension Fund Ltd',
        'LIC Housing Finance Ltd', 'UTI Asset Management Ltd', 'Aditya Birla Sun Life Insurance Ltd',
        'Kotak Mahindra Investment Trust', 'Axis Mutual Fund Ltd'
    ]
    
    data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(500):  # Generate 500 sample deals
        date = start_date + timedelta(days=random.randint(0, 365))
        
        # Skip weekends
        if date.weekday() >= 5:
            continue
            
        data.append({
            'date': date,
            'symbol': random.choice(stocks),
            'client_name': random.choice(institutions),
            'deal_type': random.choice(['Buy', 'Sell']),
            'quantity': random.randint(100000, 2000000),
            'price': round(random.uniform(100, 3000), 2),
            'value': 0  # Will calculate below
        })
    
    df = pd.DataFrame(data)
    df['value'] = df['quantity'] * df['price']
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"✓ Created {len(df)} sample bulk deals records")
    return df

if __name__ == "__main__":
    main()