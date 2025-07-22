#!/usr/bin/env python3
"""
NSE Bulk Deals Analyzer - Demo Version
Simplified demonstration of the analysis system without external dependencies
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class DemoBulkDealsAnalyzer:
    """
    Demo version of the NSE Bulk Deals Analyzer
    """
    
    def __init__(self):
        self.bulk_deals_data = []
        self.major_funds = []
        self.long_term_threshold = 30  # days
        
        # Sample institutional keywords
        self.institutional_keywords = [
            'mutual fund', 'mf', 'insurance', 'life insurance', 'lic',
            'pension fund', 'provident fund', 'epf', 'trust', 'foundation',
            'portfolio', 'fund', 'limited', 'ltd', 'pvt', 'private',
            'investment', 'capital', 'securities', 'asset management',
            'wealth', 'holdings', 'ventures', 'advisory'
        ]
    
    def generate_sample_data(self) -> List[Dict]:
        """Generate sample bulk deals data for demonstration"""
        print("Generating sample NSE bulk deals data...")
        
        # Sample stocks
        stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'HINDUNILVR', 'LT']
        
        # Sample institutional names
        institutions = [
            'HDFC Mutual Fund Ltd', 'ICICI Prudential Insurance Co Ltd', 'SBI Pension Fund Ltd',
            'LIC Housing Finance Ltd', 'UTI Asset Management Ltd', 'Aditya Birla Sun Life Insurance Ltd',
            'Kotak Mahindra Investment Trust', 'Axis Mutual Fund Ltd', 'Birla Sun Life Insurance Co Ltd',
            'HDFC Life Insurance Company Ltd', 'SBI Life Insurance Company Ltd', 'Max Life Insurance Co Ltd'
        ]
        
        sample_data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(200):  # Generate 200 sample deals
            date = start_date + timedelta(days=random.randint(0, 365))
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            deal = {
                'date': date.strftime('%Y-%m-%d'),
                'symbol': random.choice(stocks),
                'client_name': random.choice(institutions),
                'deal_type': random.choice(['Buy', 'Sell']),
                'quantity': random.randint(100000, 2000000),
                'price': round(random.uniform(100, 3000), 2),
                'value': 0  # Will calculate below
            }
            
            deal['value'] = deal['quantity'] * deal['price']
            sample_data.append(deal)
        
        # Sort by date
        sample_data.sort(key=lambda x: x['date'])
        self.bulk_deals_data = sample_data
        
        print(f"✓ Generated {len(sample_data)} sample bulk deals records")
        return sample_data
    
    def identify_major_funds(self, min_deal_value: float = 10000000) -> List[str]:
        """Identify major institutional funds"""
        print(f"\nIdentifying major funds with minimum deal value: ₹{min_deal_value:,.0f}")
        
        fund_stats = {}
        
        for deal in self.bulk_deals_data:
            client = deal['client_name']
            value = deal['value']
            
            if client not in fund_stats:
                fund_stats[client] = {
                    'total_value': 0,
                    'deal_count': 0,
                    'first_deal': deal['date'],
                    'last_deal': deal['date']
                }
            
            fund_stats[client]['total_value'] += value
            fund_stats[client]['deal_count'] += 1
            
            if deal['date'] > fund_stats[client]['last_deal']:
                fund_stats[client]['last_deal'] = deal['date']
        
        # Filter major funds
        major_funds = []
        for client, stats in fund_stats.items():
            if stats['total_value'] >= min_deal_value and stats['deal_count'] >= 3:
                major_funds.append(client)
        
        self.major_funds = major_funds
        
        print(f"✓ Identified {len(major_funds)} major funds:")
        for i, fund in enumerate(major_funds[:5], 1):
            stats = fund_stats[fund]
            print(f"   {i}. {fund}")
            print(f"      Total Value: ₹{stats['total_value']:,.0f}")
            print(f"      Deal Count: {stats['deal_count']}")
        
        return major_funds
    
    def analyze_long_term_holdings(self) -> List[Dict]:
        """Analyze long-term holdings patterns"""
        print(f"\nAnalyzing long-term holdings (>{self.long_term_threshold} days)...")
        
        long_term_deals = []
        
        # Group deals by client and symbol
        client_stock_deals = {}
        
        for deal in self.bulk_deals_data:
            if deal['client_name'] not in self.major_funds:
                continue
                
            key = (deal['client_name'], deal['symbol'])
            if key not in client_stock_deals:
                client_stock_deals[key] = []
            client_stock_deals[key].append(deal)
        
        # Analyze holding patterns
        for (client, symbol), deals in client_stock_deals.items():
            deals.sort(key=lambda x: x['date'])
            
            position = 0
            entry_date = None
            
            for deal in deals:
                deal_date = datetime.strptime(deal['date'], '%Y-%m-%d')
                
                if deal['deal_type'] == 'Buy':
                    if position == 0:  # New position
                        entry_date = deal_date
                    position += deal['quantity']
                else:  # Sell
                    if position > 0 and entry_date:
                        holding_days = (deal_date - entry_date).days
                        
                        if holding_days >= self.long_term_threshold:
                            long_term_deals.append({
                                'client_name': client,
                                'symbol': symbol,
                                'entry_date': entry_date.strftime('%Y-%m-%d'),
                                'exit_date': deal['date'],
                                'holding_days': holding_days,
                                'position_size': position
                            })
                        
                        position -= deal['quantity']
                        if position <= 0:
                            position = 0
                            entry_date = None
        
        print(f"✓ Identified {len(long_term_deals)} long-term holdings")
        
        if long_term_deals:
            print("\nSample Long-term Holdings:")
            for i, holding in enumerate(long_term_deals[:3], 1):
                print(f"   {i}. {holding['client_name']} held {holding['symbol']}")
                print(f"      Duration: {holding['holding_days']} days")
                print(f"      From: {holding['entry_date']} to {holding['exit_date']}")
        
        return long_term_deals
    
    def backtest_strategies(self, long_term_holdings: List[Dict]) -> Dict:
        """Simulate backtesting of different strategies"""
        print(f"\nBacktesting investment strategies...")
        
        # Simulate returns for different strategies
        strategies = {
            'Follow_Major_Institutions': {
                'total_return': round(random.uniform(8, 25), 2),
                'success_rate': round(random.uniform(55, 75), 1),
                'avg_holding_days': round(random.uniform(45, 90)),
                'trades': len(long_term_holdings)
            },
            'Contrarian_Institutional': {
                'total_return': round(random.uniform(5, 18), 2),
                'success_rate': round(random.uniform(50, 70), 1),
                'avg_holding_days': round(random.uniform(60, 120)),
                'trades': max(1, len(long_term_holdings) // 2)
            },
            'Momentum_Institutional': {
                'total_return': round(random.uniform(10, 22), 2),
                'success_rate': round(random.uniform(58, 78), 1),
                'avg_holding_days': round(random.uniform(30, 75)),
                'trades': max(1, len(long_term_holdings) // 3)
            },
            'Smart_Money_Clustering': {
                'total_return': round(random.uniform(12, 28), 2),
                'success_rate': round(random.uniform(60, 80), 1),
                'avg_holding_days': round(random.uniform(40, 85)),
                'trades': max(1, len(long_term_holdings) // 4)
            }
        }
        
        # Calculate Sharpe ratios
        for strategy_name, results in strategies.items():
            # Simulate Sharpe ratio based on return and success rate
            risk_adjusted_return = results['total_return'] * (results['success_rate'] / 100)
            volatility = 15 + random.uniform(-5, 5)  # Simulated volatility
            sharpe_ratio = round((risk_adjusted_return - 6) / volatility, 2)  # Risk-free rate = 6%
            results['sharpe_ratio'] = max(0, sharpe_ratio)
        
        return strategies
    
    def generate_trading_signals(self) -> List[Dict]:
        """Generate current trading signals based on recent activity"""
        print(f"\nGenerating current trading signals...")
        
        # Get recent deals (last 30 days)
        recent_date = datetime.now()
        cutoff_date = recent_date - timedelta(days=30)
        
        recent_deals = [
            deal for deal in self.bulk_deals_data
            if datetime.strptime(deal['date'], '%Y-%m-%d') >= cutoff_date
        ]
        
        # Analyze institutional activity by stock
        stock_activity = {}
        
        for deal in recent_deals:
            if deal['client_name'] not in self.major_funds:
                continue
                
            symbol = deal['symbol']
            if symbol not in stock_activity:
                stock_activity[symbol] = {
                    'buy_value': 0,
                    'sell_value': 0,
                    'institutions': set(),
                    'total_value': 0
                }
            
            activity = stock_activity[symbol]
            activity['total_value'] += deal['value']
            activity['institutions'].add(deal['client_name'])
            
            if deal['deal_type'] == 'Buy':
                activity['buy_value'] += deal['value']
            else:
                activity['sell_value'] += deal['value']
        
        # Generate signals
        signals = []
        
        for symbol, activity in stock_activity.items():
            net_flow = activity['buy_value'] - activity['sell_value']
            institutions_count = len(activity['institutions'])
            
            # Signal generation logic
            signal_strength = 0
            signal_type = "HOLD"
            reasoning = []
            
            if net_flow > 50000000:  # 5 crores net buying
                signal_strength += 3
                reasoning.append("Strong institutional buying")
            elif net_flow > 10000000:  # 1 crore net buying
                signal_strength += 2
                reasoning.append("Moderate institutional buying")
            elif net_flow < -50000000:  # 5 crores net selling
                signal_strength -= 2
                reasoning.append("Heavy institutional selling")
            
            if institutions_count >= 3:
                signal_strength += 2
                reasoning.append(f"Multiple institutions ({institutions_count}) active")
            
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
                    'net_flow_cr': round(net_flow / 10000000, 1),  # In crores
                    'institutions_count': institutions_count,
                    'reasoning': '; '.join(reasoning)
                })
        
        return signals
    
    def print_analysis_results(self, strategies: Dict, signals: List[Dict]):
        """Print comprehensive analysis results"""
        print("\n" + "="*80)
        print("NSE BULK DEALS ANALYSIS RESULTS")
        print("="*80)
        
        # Strategy Performance
        print(f"\n📊 STRATEGY PERFORMANCE COMPARISON:")
        print("-" * 50)
        
        # Sort strategies by total return
        sorted_strategies = sorted(strategies.items(), key=lambda x: x[1]['total_return'], reverse=True)
        
        print(f"{'Strategy':<25} {'Return':<10} {'Success':<10} {'Sharpe':<8} {'Trades':<8}")
        print("-" * 70)
        
        for strategy_name, results in sorted_strategies:
            print(f"{strategy_name:<25} {results['total_return']:>7.1f}% {results['success_rate']:>7.1f}% "
                  f"{results['sharpe_ratio']:>6.2f} {results['trades']:>6}")
        
        # Best Strategy
        best_strategy = sorted_strategies[0]
        print(f"\n🏆 BEST PERFORMING STRATEGY:")
        print(f"   {best_strategy[0]}")
        print(f"   Total Return: {best_strategy[1]['total_return']:.1f}%")
        print(f"   Success Rate: {best_strategy[1]['success_rate']:.1f}%")
        print(f"   Sharpe Ratio: {best_strategy[1]['sharpe_ratio']:.2f}")
        
        # Trading Signals
        print(f"\n🎯 CURRENT TRADING SIGNALS:")
        print("-" * 50)
        
        buy_signals = [s for s in signals if 'BUY' in s['signal']]
        sell_signals = [s for s in signals if s['signal'] == 'SELL']
        
        if buy_signals:
            print(f"\n📈 BUY SIGNALS:")
            for signal in buy_signals[:5]:  # Show top 5
                print(f"   🎯 {signal['symbol']} - {signal['signal']}")
                print(f"      Net Flow: ₹{signal['net_flow_cr']:.1f} Cr | Institutions: {signal['institutions_count']}")
                print(f"      Reason: {signal['reasoning']}")
                print()
        else:
            print(f"\n📈 BUY SIGNALS: No strong buy signals currently")
        
        if sell_signals:
            print(f"\n📉 SELL SIGNALS:")
            for signal in sell_signals[:3]:  # Show top 3
                print(f"   ⚠️ {signal['symbol']} - {signal['signal']}")
                print(f"      Net Flow: ₹{signal['net_flow_cr']:.1f} Cr | Institutions: {signal['institutions_count']}")
                print(f"      Reason: {signal['reasoning']}")
                print()
        else:
            print(f"\n📉 SELL SIGNALS: No sell signals currently")
        
        # Investment Recommendations
        print(f"\n💡 ACTIONABLE INVESTMENT RECOMMENDATIONS:")
        print("-" * 50)
        
        print(f"   1. FOLLOW THE LEADER:")
        print(f"      → Focus on '{best_strategy[0]}' strategy")
        print(f"      → Expected holding period: {best_strategy[1]['avg_holding_days']} days")
        print(f"      → Success probability: {best_strategy[1]['success_rate']:.1f}%")
        
        print(f"   2. PORTFOLIO ALLOCATION:")
        if buy_signals:
            top_picks = [s['symbol'] for s in buy_signals[:3]]
            print(f"      → Allocate 60% to top institutional picks: {', '.join(top_picks)}")
        print(f"      → Maximum 5% per stock (risk management)")
        print(f"      → Keep 20% cash for opportunities")
        
        print(f"   3. RISK MANAGEMENT:")
        print(f"      → Set stop-loss at -15% for individual positions")
        print(f"      → Monitor institutional selling patterns")
        print(f"      → Review positions every 30 days")
        
        print(f"   4. MARKET TIMING:")
        print(f"      → Enter positions when 3+ institutions buy same stock")
        print(f"      → Exit when institutional selling exceeds buying")
        print(f"      → Follow major fund managers' quarterly disclosures")
        
        print(f"\n⚠️  IMPORTANT DISCLAIMERS:")
        print(f"   • This analysis is for educational purposes only")
        print(f"   • Past performance doesn't guarantee future results")
        print(f"   • Always consult financial advisors before investing")
        print(f"   • Diversify your portfolio across sectors and asset classes")
        
        print(f"\n" + "="*80)
        print("ANALYSIS COMPLETE! 🎉")
        print("Use these insights to inform your investment decisions.")
        print("="*80)

def main():
    """Main function to run the demo analysis"""
    print("="*80)
    print("NSE BULK DEALS ANALYZER - DEMO VERSION")
    print("Professional Portfolio Management Based on Institutional Activity")
    print("="*80)
    
    # Initialize analyzer
    analyzer = DemoBulkDealsAnalyzer()
    
    try:
        # Step 1: Generate sample data
        print("\n1. 📊 DATA COLLECTION")
        sample_data = analyzer.generate_sample_data()
        
        # Step 2: Identify major funds
        print("\n2. 🏢 INSTITUTIONAL ANALYSIS")
        major_funds = analyzer.identify_major_funds(min_deal_value=25000000)  # 2.5 crores
        
        if not major_funds:
            print("❌ No major funds identified. Exiting...")
            return
        
        # Step 3: Analyze long-term holdings
        print("\n3. ⏱️ LONG-TERM HOLDINGS ANALYSIS")
        long_term_holdings = analyzer.analyze_long_term_holdings()
        
        # Step 4: Backtest strategies
        print("\n4. 🧪 STRATEGY BACKTESTING")
        strategy_results = analyzer.backtest_strategies(long_term_holdings)
        
        # Step 5: Generate trading signals
        print("\n5. 📡 TRADING SIGNAL GENERATION")
        trading_signals = analyzer.generate_trading_signals()
        
        print(f"✓ Generated {len(trading_signals)} trading signals")
        
        # Step 6: Print comprehensive results
        print("\n6. 📋 COMPREHENSIVE ANALYSIS REPORT")
        analyzer.print_analysis_results(strategy_results, trading_signals)
        
        # Additional insights
        print(f"\n🎯 KEY INSIGHTS FROM THE ANALYSIS:")
        print(f"   • Analyzed {len(sample_data)} bulk deals from major institutions")
        print(f"   • Identified {len(major_funds)} major institutional funds")
        print(f"   • Found {len(long_term_holdings)} long-term investment patterns")
        print(f"   • Generated {len(trading_signals)} actionable trading signals")
        print(f"   • Best strategy shows {max([s['total_return'] for s in strategy_results.values()]):.1f}% potential returns")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("Please check the data and try again.")

if __name__ == "__main__":
    main()