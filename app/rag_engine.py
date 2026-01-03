import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import json
import os

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("mbs_business_rules")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self._initialize_business_rules()
    
    def _initialize_business_rules(self):
        """Initialize the vector database with MBS business rules""" 
        business_rules = [
            {
                "id": "rule_001",
                "content": "TBA (To Be Announced) securities are mortgage-backed securities with specified characteristics but not yet assigned to specific mortgage pools.",
                "category": "tba_basics",
                "keywords": ["TBA", "to be announced", "mortgage-backed securities", "MBS"]
            },
            {
                "id": "rule_002", 
                "content": "Pool factor represents the ratio of the current principal balance to the original principal balance of a mortgage pool.",
                "category": "pool_factor",
                "keywords": ["pool factor", "principal balance", "mortgage pool", "ratio"]
            },
            {
                "id": "rule_003",
                "content": "Agency MBS include Ginnie Mae, Fannie Mae, and Freddie Mac securities with government guarantee.",
                "category": "agency_mbs",
                "keywords": ["agency MBS", "Ginnie Mae", "Fannie Mae", "Freddie Mac", "government guarantee"]
            },
            {
                "id": "rule_004",
                "content": "TBA pricing is based on specified coupon rate, settlement date, and agency type.",
                "category": "tba_pricing",
                "keywords": ["TBA pricing", "coupon rate", "settlement date", "agency type"]
            },
            {
                "id": "rule_005",
                "content": "Pool factor analysis helps track prepayment rates and expected cash flows from mortgage pools.",
                "category": "pool_analysis",
                "keywords": ["pool factor analysis", "prepayment rates", "cash flows", "mortgage pools"]
            },
            {
                "id": "rule_006",
                "content": "CPR (Constant Prepayment Rate) measures the percentage of mortgage principal prepaid in a given year.",
                "category": "prepayment_metrics",
                "keywords": ["CPR", "constant prepayment rate", "prepayment percentage", "mortgage principal"]
            },
            {
                "id": "rule_007",
                "content": "SMM (Single Monthly Mortality) is the monthly equivalent of CPR, calculated as (1 - (1 - CPR)^(1/12)).",
                "category": "prepayment_metrics", 
                "keywords": ["SMM", "single monthly mortality", "monthly prepayment", "CPR conversion"]
            },
            {
                "id": "rule_008",
                "content": "Weighted Average Coupon (WAC) represents the average interest rate of mortgages in a pool.",
                "category": "pool_metrics",
                "keywords": ["WAC", "weighted average coupon", "average interest rate", "mortgage pool"]
            },
            {
                "id": "rule_009",
                "content": "Weighted Average Maturity (WAM) is the average time until mortgage loans in a pool mature or are paid off.",
                "category": "pool_metrics",
                "keywords": ["WAM", "weighted average maturity", "average maturity", "mortgage pool"]
            },
            {
                "id": "rule_010",
                "content": "TBA roll transactions involve selling current month TBAs and buying next month TBAs to maintain exposure.",
                "category": "tba_trading",
                "keywords": ["TBA roll", "roll transactions", "current month", "next month", "maintain exposure"]
            }
        ]
        
        # Clear existing data and add new rules
        try:
            self.collection.delete()
        except:
            pass
        
        for rule in business_rules:
            embedding = self.embedder.encode(rule["content"])
            self.collection.add(
                ids=[rule["id"]],
                embeddings=[embedding.tolist()],
                documents=[rule["content"]],
                metadatas=[{
                    "category": rule["category"],
                    "keywords": ",".join(rule["keywords"])
                }]
            )
    
    async def retrieve_relevant_rules(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant business rules based on the question"""
        try:
            # Embed the question
            question_embedding = self.embedder.encode(question)
            
            # Search for relevant rules
            results = self.collection.query(
                query_embeddings=[question_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            relevant_rules = []
            for i, doc in enumerate(results["documents"][0]):
                relevant_rules.append({
                    "content": doc,
                    "category": results["metadatas"][0][i]["category"],
                    "keywords": results["metadatas"][0][i]["keywords"].split(","),
                    "relevance_score": 1 - results["distances"][0][i]  # Convert distance to relevance
                })
            
            return relevant_rules
        except Exception as e:
            print(f"Error retrieving rules: {e}")
            return []
    
    async def add_business_rule(self, rule_content: str, category: str, keywords: List[str]):
        """Add a new business rule to the vector database"""
        rule_id = f"rule_{len(self.collection.get()['ids']) + 1:03d}"
        embedding = self.embedder.encode(rule_content)
        
        self.collection.add(
            ids=[rule_id],
            embeddings=[embedding.tolist()],
            documents=[rule_content],
            metadatas=[{
                    "category": category,
                    "keywords": ",".join(keywords)
                }]
        )
        
        return rule_id
