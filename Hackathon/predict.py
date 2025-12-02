import pickle
import yaml
import pandas as pd
import numpy as np
import time
import os
from lime.lime_text import LimeTextExplainer

class TransactionPredictor:
    def __init__(self, model_path='models/'):
        """Load trained model and configuration"""
        self.model_path = model_path
        self.load_model()
        self.load_rules()
        
        # Initialize explainer
        try:
            self.explainer = LimeTextExplainer(class_names=self.categories)
        except Exception as e:
            print(f"Warning: LIME initialization failed: {e}")
            self.explainer = None
        
    def load_model(self):
        """Load trained ML components"""
        try:
            with open(f'{self.model_path}model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            with open(f'{self.model_path}vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(f'{self.model_path}categories.pkl', 'rb') as f:
                self.categories = pickle.load(f)
            
            print("✓ Model loaded successfully")
        except FileNotFoundError:
            raise Exception("Model not found! Please run train.py first.")
    
    def load_rules(self, yaml_path='config/taxonomy.yaml'):
        """Load categorization rules from YAML"""
        self.rule_engine = {}
        self.thresholds = {}
        
        if not os.path.exists(yaml_path):
            print(f"⚠️ Warning: {yaml_path} not found. Running without rule engine.")
            return

        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'categories' in config:
                for category in config['categories']:
                    cat_name = category['name']
                    keywords = category.get('keywords', [])
                    threshold = category.get('threshold', 0.7)
                    
                    self.rule_engine[cat_name] = [kw.lower() for kw in keywords]
                    self.thresholds[cat_name] = threshold
            
            print(f"✓ Loaded rules for {len(self.rule_engine)} categories")
        except Exception as e:
            print(f"❌ Error loading rules: {e}")
    
    def preprocess_text(self, text):
        """Clean and normalize transaction text"""
        if pd.isna(text):
            return ""
        text = str(text).lower().strip()
        text = text.replace('*', '').replace('#', '')
        return text
    
    def rule_match(self, text):
        """Check if transaction matches any keyword rules"""
        text_lower = text.lower()
        
        for category, keywords in self.rule_engine.items():
            for keyword in keywords:
                # Simple substring match - can be improved with regex boundaries
                if keyword in text_lower:
                    return {
                        'category': category,
                        'confidence': 0.95,
                        'method': 'rule_match',
                        'matched_keyword': keyword
                    }
        
        return None
    
    def ml_predict(self, text):
        """Use ML model for prediction"""
        text_vec = self.vectorizer.transform([text])
        
        # Get prediction and probabilities
        category = self.model.predict(text_vec)[0]
        probabilities = self.model.predict_proba(text_vec)[0]
        
        # Get confidence for predicted category
        category_idx = list(self.categories).index(category)
        confidence = probabilities[category_idx]
        
        return {
            'category': category,
            'confidence': float(confidence),
            'method': 'ml_model',
            'probabilities': {cat: float(prob) for cat, prob in zip(self.categories, probabilities)}
        }
    
    def predict(self, transaction_text, explain=False):
        """
        Predict category for a transaction
        
        Args:
            transaction_text: Raw transaction description
            explain: If True, include LIME explanation
        
        Returns:
            Dictionary with prediction details
        """
        clean_text = self.preprocess_text(transaction_text)
        
        # Try rule matching first
        rule_result = self.rule_match(clean_text)
        
        if rule_result:
            result = rule_result
        else:
            # Fall back to ML model
            result = self.ml_predict(clean_text)
        
        result['original_text'] = transaction_text
        result['needs_review'] = result['confidence'] < 0.7
        
        # Add explanation if requested
        if explain and result['method'] == 'ml_model' and self.explainer:
            result['explanation'] = self.explain_prediction(clean_text)
        
        return result
    
    def explain_prediction(self, text, num_features=5):
        """Generate explanation for ML prediction using LIME"""
        def predict_proba_wrapper(texts):
            vec = self.vectorizer.transform(texts)
            return self.model.predict_proba(vec)
        
        try:
            exp = self.explainer.explain_instance(
                text, 
                predict_proba_wrapper,
                num_features=num_features,
                top_labels=1
            )
            
            # Get top contributing words
            top_label = exp.available_labels()[0]
            word_weights = exp.as_list(label=top_label)
            
            return {
                'top_words': word_weights,
                'predicted_class': self.categories[top_label]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def batch_predict(self, transactions, show_progress=True):
        """
        Predict categories for multiple transactions
        
        Args:
            transactions: List of transaction texts or DataFrame
            show_progress: Show progress during processing
        
        Returns:
            List of prediction results
        """
        if isinstance(transactions, pd.DataFrame):
            if 'description' not in transactions.columns:
                raise ValueError("DataFrame must have 'description' column")
            transaction_list = transactions['description'].tolist()
        else:
            transaction_list = transactions
        
        results = []
        start_time = time.time()
        
        for idx, text in enumerate(transaction_list):
            result = self.predict(text)
            results.append(result)
            
            if show_progress and (idx + 1) % 100 == 0:
                print(f"Processed {idx + 1}/{len(transaction_list)} transactions...")
        
        elapsed = time.time() - start_time
        throughput = len(transaction_list) / elapsed if elapsed > 0 else 0
        
        print(f"\n✓ Batch prediction complete!")
        print(f"  Total transactions: {len(transaction_list)}")
        print(f"  Time elapsed: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.0f} transactions/second")
        
        return results
    
    def get_statistics(self, results):
        """Calculate statistics from prediction results"""
        df = pd.DataFrame(results)
        
        stats = {
            'total_predictions': len(results),
            'rule_matches': len(df[df['method'] == 'rule_match']),
            'ml_predictions': len(df[df['method'] == 'ml_model']),
            'needs_review': len(df[df['needs_review'] == True]),
            'avg_confidence': df['confidence'].mean(),
            'category_distribution': df['category'].value_counts().to_dict(),
            'low_confidence_samples': df[df['confidence'] < 0.7][['original_text', 'category', 'confidence']].to_dict('records')[:10]
        }
        
        return stats

def demo():
    """Quick demo of the prediction system"""
    print("=" * 60)
    print("AI TRANSACTION CATEGORIZER - PREDICTION DEMO")
    print("=" * 60)
    
    try:
        # Initialize predictor
        predictor = TransactionPredictor()
        
        # Test transactions
        test_transactions = [
            "Starbucks Coffee Downtown",
            "Shell Gas Station",
            "Amazon.com Purchase",
            "Uber Ride to Airport",
            "Netflix Monthly Subscription",
            "Apollo Pharmacy Medicine",
            "DMart Grocery Shopping",
            "PVR Cinemas Movie Ticket"
        ]
        
        print("\n=== Sample Predictions ===\n")
        
        for txn in test_transactions:
            result = predictor.predict(txn, explain=True)
            
            print(f"Transaction: {txn}")
            print(f"  → Category: {result['category']}")
            print(f"  → Confidence: {result['confidence']:.2%}")
            print(f"  → Method: {result['method']}")
            if 'matched_keyword' in result:
                print(f"  → Matched Keyword: {result['matched_keyword']}")
            if result['needs_review']:
                print(f"  ⚠ Needs Review (low confidence)")
            print()
            
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("Tip: Run 'python train.py' first to train the model.")

if __name__ == "__main__":
    demo()