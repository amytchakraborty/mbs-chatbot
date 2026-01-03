import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import math 

class PoolFactorAnalyzer:
    """Advanced pool factor analysis for mortgage-backed securities"""
    
    def __init__(self):
        self.cpr_benchmark = 0.06  # 6% annual CPR benchmark
        self.smm_benchmark = self._cpr_to_smm(self.cpr_benchmark)
    
    def _cpr_to_smm(self, cpr: float) -> float:
        """Convert CPR to SMM (Single Monthly Mortality)"""
        return 1 - (1 - cpr) ** (1/12)
    
    def _smm_to_cpr(self, smm: float) -> float:
        """Convert SMM to CPR"""
        return 1 - (1 - smm) ** 12
    
    def calculate_prepayment_speed(self, pool_factors: pd.Series, dates: pd.Series) -> Dict[str, Any]:
        """Calculate various prepayment speed metrics"""
        if len(pool_factors) < 2:
            return {"error": "Insufficient data for prepayment calculation"}
        
        # Calculate monthly changes
        monthly_changes = pool_factors.pct_change().dropna()
        
        # Calculate SMM (actual prepayment rate)
        smm_values = -monthly_changes  # Negative because pool factors decrease with prepayments
        smm_values = smm_values.clip(lower=0, upper=1)  # Ensure valid range
        
        # Convert to CPR
        cpr_values = smm_values.apply(self._smm_to_cpr)
        
        # Calculate conditional prepayment rate (CPR) trends
        avg_cpr = cpr_values.mean()
        cpr_volatility = cpr_values.std()
        
        # Calculate PSA (Public Securities Association) benchmark comparison
        psa_multiplier = avg_cpr / self.cpr_benchmark if self.cpr_benchmark > 0 else 0
        
        return {
            "current_smm": smm_values.iloc[-1] if len(smm_values) > 0 else 0,
            "current_cpr": cpr_values.iloc[-1] if len(cpr_values) > 0 else 0,
            "average_cpr": avg_cpr,
            "cpr_volatility": cpr_volatility,
            "psa_multiplier": psa_multiplier,
            "prepayment_trend": "accelerating" if len(cpr_values) > 1 and cpr_values.iloc[-1] > cpr_values.iloc[-2] else "decelerating",
            "monthly_prepayment_history": cpr_values.tolist()[-12:]  # Last 12 months
        }
    
    def project_cash_flows(self, current_balance: float, pool_factor: float, wac: float, 
                          remaining_months: int, projected_cpr: float) -> Dict[str, Any]:
        """Project future cash flows based on pool factor and prepayment assumptions"""
        cash_flows = []
        balance = current_balance
        monthly_rate = wac / 12
        projected_smm = self._cpr_to_smm(projected_cpr)
        
        for month in range(1, remaining_months + 1):
            # Calculate scheduled payment
            if balance > 0:
                scheduled_payment = balance * monthly_rate * (1 + monthly_rate) ** remaining_months / ((1 + monthly_rate) ** remaining_months - 1)
                scheduled_interest = balance * monthly_rate
                scheduled_principal = scheduled_payment - scheduled_interest
                
                # Calculate prepayment
                prepayment = (balance - scheduled_principal) * projected_smm
                
                # Total cash flow
                total_payment = scheduled_payment + prepayment
                
                cash_flows.append({
                    "month": month,
                    "scheduled_payment": scheduled_payment,
                    "scheduled_interest": scheduled_interest,
                    "scheduled_principal": scheduled_principal,
                    "prepayment": prepayment,
                    "total_payment": total_payment,
                    "ending_balance": max(0, balance - scheduled_principal - prepayment)
                })
                
                balance = max(0, balance - scheduled_principal - prepayment)
            else:
                break
        
        # Calculate summary metrics
        total_payments = sum(cf["total_payment"] for cf in cash_flows)
        total_interest = sum(cf["scheduled_interest"] for cf in cash_flows)
        total_principal = sum(cf["scheduled_principal"] + cf["prepayment"] for cf in cash_flows)
        
        return {
            "projected_cash_flows": cash_flows,
            "summary": {
                "total_payments": total_payments,
                "total_interest": total_interest,
                "total_principal": total_principal,
                "weighted_average_life": self._calculate_wal(cash_flows, current_balance),
                "duration": self._calculate_macaulay_duration(cash_flows, wac/12)
            }
        }
    
    def _calculate_wal(self, cash_flows: List[Dict], initial_balance: float) -> float:
        """Calculate Weighted Average Life"""
        if not cash_flows:
            return 0
        
        weighted_months = sum(cf["month"] * cf["total_payment"] for cf in cash_flows)
        total_payments = sum(cf["total_payment"] for cf in cash_flows)
        
        return weighted_months / total_payments / 12  # Convert to years
    
    def _calculate_macaulay_duration(self, cash_flows: List[Dict], monthly_rate: float) -> float:
        """Calculate Macaulay duration"""
        if not cash_flows:
            return 0
        
        present_values = []
        for cf in cash_flows:
            pv = cf["total_payment"] / ((1 + monthly_rate) ** cf["month"])
            present_values.append(pv * cf["month"])
        
        total_pv = sum(cf["total_payment"] / ((1 + monthly_rate) ** cf["month"]) for cf in cash_flows)
        
        if total_pv == 0:
            return 0
        
        return sum(present_values) / total_pv / 12  # Convert to years
    
    def analyze_pool_health(self, pool_data: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive pool health analysis"""
        latest_data = pool_data.groupby('pool_id').last().reset_index()
        
        health_scores = []
        for _, pool in latest_data.iterrows():
            score = self._calculate_health_score(pool)
            health_scores.append({
                "pool_id": pool["pool_id"],
                "health_score": score,
                "health_category": self._categorize_health(score),
                "pool_factor": pool["pool_factor"],
                "current_balance": pool["current_balance"]
            })
        
        # Portfolio level analysis
        avg_health_score = np.mean([hs["health_score"] for hs in health_scores])
        
        return {
            "individual_pool_health": health_scores,
            "portfolio_health": {
                "average_health_score": avg_health_score,
                "health_distribution": self._get_health_distribution(health_scores),
                "total_balance": latest_data["current_balance"].sum(),
                "avg_pool_factor": latest_data["pool_factor"].mean()
            }
        }
    
    def _calculate_health_score(self, pool: pd.Series) -> float:
        """Calculate health score for individual pool (0-100)"""
        # Pool factor component (40% weight)
        factor_score = pool["pool_factor"] * 40
        
        # Balance stability component (30% weight)
        balance_ratio = pool["current_balance"] / pool["original_balance"]
        balance_score = min(balance_ratio * 100, 30)
        
        # WAC component (20% weight) - higher WAC generally better for investors
        wac_score = min(pool["wac"] / 5 * 20, 20)  # Assuming 5% as reference
        
        # WAM component (10% weight) - moderate remaining term is optimal
        wam = pool.get("wam", 360)
        if 120 <= wam <= 240:  # 10-20 years remaining
            wam_score = 10
        elif 60 <= wam < 120 or 240 < wam <= 300:
            wam_score = 7
        else:
            wam_score = 3
        
        return factor_score + balance_score + wac_score + wam_score
    
    def _categorize_health(self, score: float) -> str:
        """Categorize pool health based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 35:
            return "Poor"
        else:
            return "Critical"
    
    def _get_health_distribution(self, health_scores: List[Dict]) -> Dict[str, int]:
        """Get distribution of health categories"""
        distribution = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0, "Critical": 0}
        
        for hs in health_scores:
            distribution[hs["health_category"]] += 1
        
        return distribution
    
    def calculate_concentration_risk(self, pool_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate concentration risk metrics"""
        latest_data = pool_data.groupby('pool_id').last().reset_index()
        
        # Balance concentration
        total_balance = latest_data["current_balance"].sum()
        latest_data["balance_weight"] = latest_data["current_balance"] / total_balance
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = (latest_data["balance_weight"] ** 2).sum() * 10000
        
        # Large pool concentration (pools > 10% of total)
        large_pools = latest_data[latest_data["balance_weight"] > 0.1]
        large_pool_concentration = large_pools["balance_weight"].sum()
        
        return {
            "hhi_score": hhi,
            "concentration_level": "High" if hhi > 2500 else "Medium" if hhi > 1500 else "Low",
            "large_pool_concentration": large_pool_concentration,
            "number_of_large_pools": len(large_pools),
            "top_10_concentration": latest_data.nlargest(10, "balance_weight")["balance_weight"].sum()
        }
