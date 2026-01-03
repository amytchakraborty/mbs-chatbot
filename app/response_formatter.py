import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import json

class ResponseFormatter:
    """Format chatbot responses with tables, charts, and summaries"""
    
    def __init__(self):
        self.chart_templates = {
            'pie': self._create_pie_chart,
            'bar': self._create_bar_chart,
            'line': self._create_line_chart
        }
    
    async def format_response(self, question: str, analysis_result: Dict[str, Any], 
                            relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format the complete response with tables, charts, and summary""" 
        
        # Generate answer text
        answer = self._generate_answer_text(question, analysis_result, relevant_rules)
        
        # Generate tables
        tables = self._generate_tables(analysis_result)
        
        # Generate charts
        charts = self._generate_charts(analysis_result)
        
        # Generate summary
        summary = self._generate_summary(question, analysis_result)
        
        return {
            "answer": answer,
            "tables": tables,
            "charts": charts,
            "summary": summary
        }
    
    def _generate_answer_text(self, question: str, analysis_result: Dict[str, Any], 
                             relevant_rules: List[Dict[str, Any]]) -> str:
        """Generate the main answer text"""
        question_lower = question.lower()
        
        # Start with context from relevant rules
        rule_context = ""
        if relevant_rules:
            rule_context = "Based on the following relevant information: "
            rule_context += "; ".join([rule["content"] for rule in relevant_rules[:2]])
            rule_context += "\n\n"
        
        # Generate specific answer based on question type
        if "tba" in question_lower:
            answer = self._generate_tba_answer(analysis_result)
        elif "pool factor" in question_lower or "factor" in question_lower:
            answer = self._generate_pool_factor_answer(analysis_result)
        elif "compare" in question_lower:
            answer = self._generate_comparison_answer(analysis_result)
        elif "performance" in question_lower or "yield" in question_lower:
            answer = self._generate_performance_answer(analysis_result)
        else:
            answer = self._generate_general_answer(analysis_result)
        
        return rule_context + answer
    
    def _generate_tba_answer(self, analysis_result: Dict[str, Any]) -> str:
        """Generate TBA-specific answer"""
        tba_data = analysis_result.get('data', {}).get('tba_summary', {})
        
        if not tba_data:
            return "I don't have specific TBA data available for your question."
        
        answer = f"Current TBA market analysis shows {tba_data.get('total_securities', 0)} securities tracked. "
        
        agency_dist = tba_data.get('agency_distribution', {})
        if agency_dist:
            top_agency = max(agency_dist, key=agency_dist.get)
            answer += f"{top_agency} has the highest representation with {agency_dist[top_agency]} securities. "
        
        price_stats = tba_data.get('price_stats', {})
        if price_stats:
            answer += f"The average price is {price_stats.get('mean', 0):.2f} "
            answer += f"with a range from {price_stats.get('min', 0):.2f} to {price_stats.get('max', 0):.2f}. "
        
        yield_stats = tba_data.get('yield_stats', {})
        if yield_stats:
            answer += f"Average yield is {yield_stats.get('mean', 0):.2f}%."
        
        return answer
    
    def _generate_pool_factor_answer(self, analysis_result: Dict[str, Any]) -> str:
        """Generate pool factor-specific answer"""
        pool_data = analysis_result.get('data', {}).get('pool_analysis', {})
        
        if not pool_data:
            return "I don't have specific pool factor data available for your question."
        
        answer = f"Current pool factor analysis covers {pool_data.get('total_pools', 0)} pools. "
        
        avg_factor = pool_data.get('avg_pool_factor', 0)
        answer += f"The average pool factor is {avg_factor:.4f}, "
        answer += f"indicating a prepayment rate of {pool_data.get('prepayment_rate', 0):.2f}%. "
        
        current_balance = pool_data.get('total_current_balance', 0)
        original_balance = pool_data.get('total_original_balance', 0)
        if original_balance > 0:
            answer += f"Total current balance is ${current_balance:,.0f} "
            answer += f"out of an original ${original_balance:,.0f}. "
        
        pool_dist = pool_data.get('pool_distribution', {})
        if pool_dist:
            healthy = pool_dist.get('healthy_pools', 0)
            answer += f"{healthy} pools are maintaining healthy factors (>0.7)."
        
        return answer
    
    def _generate_comparison_answer(self, analysis_result: Dict[str, Any]) -> str:
        """Generate comparison-specific answer"""
        comparison_data = analysis_result.get('data', {}).get('comparison', {})
        
        if not comparison_data:
            return "I don't have sufficient data for the comparison you requested."
        
        answer = "Comparison analysis shows the following key differences: "
        
        agency_comp = comparison_data.get('agency_comparison', {})
        if agency_comp:
            answer += "Across agencies, "
            for agency, metrics in agency_comp.items():
                answer += f"{agency} has avg yield of {metrics.get('avg_yield', 0):.2f}% "
                answer += f"and avg price of {metrics.get('avg_price', 0):.1f}. "
        
        return answer
    
    def _generate_performance_answer(self, analysis_result: Dict[str, Any]) -> str:
        """Generate performance-specific answer"""
        perf_data = analysis_result.get('data', {}).get('performance_metrics', {})
        
        if not perf_data:
            return "I don't have specific performance data available for your question."
        
        answer = f"Performance metrics indicate a weighted average yield of {perf_data.get('weighted_avg_yield', 0):.2f}% "
        answer += f"with weighted average duration of {perf_data.get('weighted_avg_duration', 0):.1f} years. "
        
        volatility = perf_data.get('price_volatility', 0)
        answer += f"Price volatility is {volatility:.3f}, "
        
        yield_spreads = perf_data.get('yield_spread', {})
        if yield_spreads:
            fnma_spread = yield_spreads.get('fnma_vs_gnma', 0)
            answer += f"and the FNMA vs GNMA yield spread is {fnma_spread:.3f}%."
        
        return answer
    
    def _generate_general_answer(self, analysis_result: Dict[str, Any]) -> str:
        """Generate general answer"""
        return "I can help you analyze mortgage-backed securities data including TBA securities, pool factors, and performance metrics. Please ask a specific question about any of these areas."
    
    def _generate_tables(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data tables"""
        tables = []
        
        # TBA Summary Table
        if 'tba_summary' in analysis_result.get('data', {}):
            tba_table = self._create_tba_table(analysis_result['data']['tba_summary'])
            tables.append(tba_table)
        
        # Pool Analysis Table
        if 'pool_analysis' in analysis_result.get('data', {}):
            pool_table = self._create_pool_table(analysis_result['data']['pool_analysis'])
            tables.append(pool_table)
        
        # Performance Table
        if 'performance_metrics' in analysis_result.get('data', {}):
            perf_table = self._create_performance_table(analysis_result['data']['performance_metrics'])
            tables.append(perf_table)
        
        # Comparison Table
        if 'comparison' in analysis_result.get('data', {}):
            comp_table = self._create_comparison_table(analysis_result['data']['comparison'])
            tables.append(comp_table)
        
        return tables
    
    def _create_tba_table(self, tba_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create TBA summary table"""
        table_data = []
        
        # Agency distribution
        agency_dist = tba_data.get('agency_distribution', {})
        for agency, count in agency_dist.items():
            table_data.append({
                "Agency": agency,
                "Count": count,
                "Type": "Agency Distribution"
            })
        
        # Coupon statistics
        coupon_stats = tba_data.get('coupon_stats', {})
        if coupon_stats:
            table_data.extend([
                {"Metric": "Average Coupon", "Value": f"{coupon_stats.get('mean', 0):.2f}%", "Type": "Coupon Stats"},
                {"Metric": "Min Coupon", "Value": f"{coupon_stats.get('min', 0):.2f}%", "Type": "Coupon Stats"},
                {"Metric": "Max Coupon", "Value": f"{coupon_stats.get('max', 0):.2f}%", "Type": "Coupon Stats"}
            ])
        
        return {
            "title": "TBA Securities Summary",
            "headers": ["Metric", "Value", "Type"],
            "data": table_data
        }
    
    def _create_pool_table(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pool analysis table"""
        table_data = [
            {"Metric": "Total Pools", "Value": pool_data.get('total_pools', 0), "Category": "Pool Summary"},
            {"Metric": "Average Pool Factor", "Value": f"{pool_data.get('avg_pool_factor', 0):.4f}", "Category": "Pool Summary"},
            {"Metric": "Prepayment Rate", "Value": f"{pool_data.get('prepayment_rate', 0):.2f}%", "Category": "Prepayment"},
            {"Metric": "Total Current Balance", "Value": f"${pool_data.get('total_current_balance', 0):,.0f}", "Category": "Balance"},
            {"Metric": "Total Original Balance", "Value": f"${pool_data.get('total_original_balance', 0):,.0f}", "Category": "Balance"}
        ]
        
        # Add pool distribution
        pool_dist = pool_data.get('pool_distribution', {})
        for category, count in pool_dist.items():
            table_data.append({
                "Metric": category.replace('_', ' ').title(),
                "Value": count,
                "Category": "Distribution"
            })
        
        return {
            "title": "Pool Factor Analysis",
            "headers": ["Metric", "Value", "Category"],
            "data": table_data
        }
    
    def _create_performance_table(self, perf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance metrics table"""
        table_data = [
            {"Metric": "Weighted Avg Yield", "Value": f"{perf_data.get('weighted_avg_yield', 0):.2f}%", "Category": "Yield"},
            {"Metric": "Weighted Avg Duration", "Value": f"{perf_data.get('weighted_avg_duration', 0):.1f} years", "Category": "Duration"},
            {"Metric": "Price Volatility", "Value": f"{perf_data.get('price_volatility', 0):.3f}", "Category": "Risk"}
        ]
        
        # Add yield spreads
        yield_spreads = perf_data.get('yield_spread', {})
        for spread_name, spread_value in yield_spreads.items():
            table_data.append({
                "Metric": spread_name.replace('_', ' ').title(),
                "Value": f"{spread_value:.3f}%",
                "Category": "Yield Spread"
            })
        
        return {
            "title": "Performance Metrics",
            "headers": ["Metric", "Value", "Category"],
            "data": table_data
        }
    
    def _create_comparison_table(self, comp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comparison table"""
        table_data = []
        
        # Agency comparison
        agency_comp = comp_data.get('agency_comparison', {})
        for agency, metrics in agency_comp.items():
            table_data.append({
                "Agency": agency,
                "Average Price": f"{metrics.get('avg_price', 0):.2f}",
                "Average Yield": f"{metrics.get('avg_yield', 0):.2f}%",
                "Average Duration": f"{metrics.get('avg_duration', 0):.1f}",
                "Type": "Agency"
            })
        
        return {
            "title": "Agency Comparison",
            "headers": ["Agency", "Average Price", "Average Yield", "Average Duration", "Type"],
            "data": table_data
        }
    
    def _generate_charts(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts"""
        charts = []
        
        # Agency distribution pie chart
        if 'tba_summary' in analysis_result.get('data', {}):
            agency_dist = analysis_result['data']['tba_summary'].get('agency_distribution', {})
            if agency_dist:
                pie_chart = self._create_pie_chart(
                    list(agency_dist.keys()),
                    list(agency_dist.values()),
                    "Agency Distribution"
                )
                charts.append(pie_chart)
        
        # Pool health distribution pie chart
        if 'pool_analysis' in analysis_result.get('data', {}):
            pool_dist = analysis_result['data']['pool_analysis'].get('pool_distribution', {})
            if pool_dist:
                pool_chart = self._create_pie_chart(
                    list(pool_dist.keys()),
                    list(pool_dist.values()),
                    "Pool Health Distribution"
                )
                charts.append(pool_chart)
        
        return charts
    
    def _create_pie_chart(self, labels: List[str], values: List[float], title: str) -> Dict[str, Any]:
        """Create a pie chart"""
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(title=title)
        
        return {
            "type": "pie",
            "title": title,
            "data": fig.to_dict()
        }
    
    def _create_bar_chart(self, x: List[str], y: List[float], title: str) -> Dict[str, Any]:
        """Create a bar chart"""
        fig = go.Figure(data=[go.Bar(x=x, y=y)])
        fig.update_layout(title=title)
        
        return {
            "type": "bar",
            "title": title,
            "data": fig.to_dict()
        }
    
    def _create_line_chart(self, x: List[str], y: List[float], title: str) -> Dict[str, Any]:
        """Create a line chart"""
        fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='lines+markers')])
        fig.update_layout(title=title)
        
        return {
            "type": "line",
            "title": title,
            "data": fig.to_dict()
        }
    
    def _generate_summary(self, question: str, analysis_result: Dict[str, Any]) -> str:
        """Generate a concise summary"""
        question_lower = question.lower()
        
        if "tba" in question_lower:
            return "TBA analysis shows current market conditions with agency distribution and pricing metrics."
        elif "pool factor" in question_lower:
            return "Pool factor analysis reveals prepayment rates and pool health across the portfolio."
        elif "compare" in question_lower:
            return "Comparison highlights key differences between agencies and coupon rates."
        elif "performance" in question_lower:
            return "Performance analysis provides yield, duration, and risk metrics."
        else:
            return "Analysis completed with relevant MBS data insights and visualizations."
