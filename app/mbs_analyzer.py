import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json 

class MBSAnalyzer:
    def __init__(self):
        self.sample_tba_data = self._generate_sample_tba_data()
        self.sample_pool_data = self._generate_sample_pool_data()
    
    def _generate_sample_tba_data(self) -> pd.DataFrame:
        """Generate sample TBA data for demonstration"""
        data = {
            'cusip': [f'31291{str(i).zfill(4)}' for i in range(1, 11)],
            'agency': ['FNMA'] * 3 + ['FHLMC'] * 3 + ['GNMA'] * 4,
            'coupon': [2.5, 3.0, 3.5, 2.5, 3.0, 3.5, 2.0, 2.5, 3.0, 3.5],
            'settlement_date': pd.date_range('2024-01-01', periods=10, freq='M'),
            'price': [98.5, 99.2, 100.1, 98.8, 99.5, 100.3, 97.9, 98.6, 99.3, 100.2],
            'yield': [3.2, 3.1, 3.0, 3.15, 3.05, 2.95, 3.3, 3.25, 3.15, 3.05],
            'duration': [5.2, 4.8, 4.5, 5.1, 4.7, 4.4, 5.5, 5.3, 4.9, 4.6]
        }
        return pd.DataFrame(data)
    
    def _generate_sample_pool_data(self) -> pd.DataFrame:
        """Generate sample pool factor data"""
        dates = pd.date_range('2023-01-01', '2024-12-01', freq='M')
        pools = []
        
        for pool_id in range(1, 6):
            for date in dates:
                factor = max(0.1, 1.0 - (len(dates) - len(dates[dates <= date])) * 0.05 - np.random.normal(0, 0.02))
                pools.append({
                    'pool_id': f'POOL{str(pool_id).zfill(3)}',
                    'date': date,
                    'pool_factor': round(factor, 4),
                    'original_balance': 1000000,
                    'current_balance': int(1000000 * factor),
                    'wac': 3.5 + np.random.normal(0, 0.3),
                    'wam': 360 - (len(dates) - len(dates[dates <= date])) * 30
                })
        
        return pd.DataFrame(pools)
    
    async def analyze_question(self, question: str, relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the question and return relevant MBS data"""
        question_lower = question.lower()
        
        analysis_result = {
            'question_type': self._classify_question(question_lower),
            'data': {},
            'insights': [],
            'relevant_rules': relevant_rules
        }
        
        # TBA related questions
        if any(keyword in question_lower for keyword in ['tba', 'to be announced', 'agency']):
            analysis_result['data']['tba_summary'] = self._analyze_tba_data(question_lower)
        
        # Pool factor related questions
        if any(keyword in question_lower for keyword in ['pool factor', 'factor', 'prepayment']):
            analysis_result['data']['pool_analysis'] = self._analyze_pool_factors(question_lower)
        
        # Performance metrics
        if any(keyword in question_lower for keyword in ['performance', 'yield', 'duration', 'return']):
            analysis_result['data']['performance_metrics'] = self._calculate_performance_metrics(question_lower)
        
        # Comparison questions
        if any(keyword in question_lower for keyword in ['compare', 'difference', 'vs', 'versus']):
            analysis_result['data']['comparison'] = self._perform_comparison(question_lower)
        
        return analysis_result
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question"""
        if any(keyword in question for keyword in ['tba', 'to be announced']):
            return 'tba_analysis'
        elif any(keyword in question for keyword in ['pool factor', 'factor', 'prepayment']):
            return 'pool_factor_analysis'
        elif any(keyword in question for keyword in ['performance', 'yield', 'return']):
            return 'performance_analysis'
        elif any(keyword in question for keyword in ['compare', 'difference']):
            return 'comparison'
        else:
            return 'general_inquiry'
    
    def _analyze_tba_data(self, question: str) -> Dict[str, Any]:
        """Analyze TBA data based on question"""
        tba_summary = {
            'total_securities': len(self.sample_tba_data),
            'agency_distribution': self.sample_tba_data['agency'].value_counts().to_dict(),
            'coupon_stats': {
                'mean': self.sample_tba_data['coupon'].mean(),
                'min': self.sample_tba_data['coupon'].min(),
                'max': self.sample_tba_data['coupon'].max()
            },
            'price_stats': {
                'mean': self.sample_tba_data['price'].mean(),
                'min': self.sample_tba_data['price'].min(),
                'max': self.sample_tba_data['price'].max()
            },
            'yield_stats': {
                'mean': self.sample_tba_data['yield'].mean(),
                'min': self.sample_tba_data['yield'].min(),
                'max': self.sample_tba_data['yield'].max()
            }
        }
        
        # Filter by specific agency if mentioned
        agencies = ['fnma', 'fhlmc', 'gnma']
        for agency in agencies:
            if agency in question:
                agency_data = self.sample_tba_data[self.sample_tba_data['agency'].str.upper() == agency.upper()]
                if not agency_data.empty:
                    tba_summary[f'{agency}_specific'] = {
                        'count': len(agency_data),
                        'avg_price': agency_data['price'].mean(),
                        'avg_yield': agency_data['yield'].mean()
                    }
        
        return tba_summary
    
    def _analyze_pool_factors(self, question: str) -> Dict[str, Any]:
        """Analyze pool factor data"""
        latest_date = self.sample_pool_data['date'].max()
        latest_data = self.sample_pool_data[self.sample_pool_data['date'] == latest_date]
        
        pool_analysis = {
            'total_pools': len(latest_data),
            'avg_pool_factor': latest_data['pool_factor'].mean(),
            'total_current_balance': latest_data['current_balance'].sum(),
            'total_original_balance': latest_data['original_balance'].sum(),
            'prepayment_rate': (1 - latest_data['pool_factor'].mean()) * 100,
            'pool_distribution': {
                'healthy_pools': len(latest_data[latest_data['pool_factor'] > 0.7]),
                'moderate_pools': len(latest_data[(latest_data['pool_factor'] >= 0.3) & (latest_data['pool_factor'] <= 0.7)]),
                'declining_pools': len(latest_data[latest_data['pool_factor'] < 0.3])
            }
        }
        
        # Calculate trend if historical data is requested
        if any(keyword in question for keyword in ['trend', 'history', 'over time']):
            pool_analysis['trend'] = self._calculate_pool_factor_trend()
        
        return pool_analysis
    
    def _calculate_pool_factor_trend(self) -> Dict[str, Any]:
        """Calculate pool factor trends over time"""
        monthly_avg = self.sample_pool_data.groupby('date')['pool_factor'].mean().reset_index()
        
        # Calculate month-over-month change
        monthly_avg['mom_change'] = monthly_avg['pool_factor'].pct_change() * 100
        
        return {
            'current_trend': 'declining' if monthly_avg['mom_change'].iloc[-1] < 0 else 'improving',
            'avg_monthly_change': monthly_avg['mom_change'].mean(),
            'volatility': monthly_avg['mom_change'].std(),
            'data_points': len(monthly_avg)
        }
    
    def _calculate_performance_metrics(self, question: str) -> Dict[str, Any]:
        """Calculate performance metrics"""
        performance = {
            'weighted_avg_yield': np.average(self.sample_tba_data['yield'], weights=self.sample_tba_data['price']),
            'weighted_avg_duration': np.average(self.sample_tba_data['duration'], weights=self.sample_tba_data['price']),
            'price_volatility': self.sample_tba_data['price'].std(),
            'yield_spread': {
                'fnma_vs_gnma': self._calculate_yield_spread('FNMA', 'GNMA'),
                'fhlmc_vs_gnma': self._calculate_yield_spread('FHLMC', 'GNMA')
            }
        }
        
        return performance
    
    def _calculate_yield_spread(self, agency1: str, agency2: str) -> float:
        """Calculate yield spread between two agencies"""
        data1 = self.sample_tba_data[self.sample_tba_data['agency'] == agency1]
        data2 = self.sample_tba_data[self.sample_tba_data['agency'] == agency2]
        
        if not data1.empty and not data2.empty:
            return data1['yield'].mean() - data2['yield'].mean()
        return 0.0
    
    def _perform_comparison(self, question: str) -> Dict[str, Any]:
        """Perform comparisons between different MBS types"""
        comparison = {
            'agency_comparison': {},
            'coupon_comparison': {}
        }
        
        # Compare agencies
        for agency in self.sample_tba_data['agency'].unique():
            agency_data = self.sample_tba_data[self.sample_tba_data['agency'] == agency]
            comparison['agency_comparison'][agency] = {
                'count': len(agency_data),
                'avg_price': agency_data['price'].mean(),
                'avg_yield': agency_data['yield'].mean(),
                'avg_duration': agency_data['duration'].mean()
            }
        
        # Compare by coupon rates
        coupon_groups = self.sample_tba_data.groupby('coupon').agg({
            'price': 'mean',
            'yield': 'mean',
            'duration': 'mean'
        }).round(3).to_dict()
        
        comparison['coupon_comparison'] = coupon_groups
        
        return comparison
