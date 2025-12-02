import pandas as pd
import numpy as np
import pickle
import yaml
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os

class TransactionCategorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2,
            lowercase=True
        )
        
        # Ensemble model for better accuracy
        lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
        rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        
        self.model = VotingClassifier(
            estimators=[('lr', lr), ('rf', rf)],
            voting='soft'
        )
        
        self.categories = []
        
    def preprocess_text(self, text):
        """Clean and normalize transaction text"""
        if pd.isna(text):
            return ""
        text = str(text).lower().strip()
        # Remove common noise
        text = text.replace('*', '').replace('#', '')
        return text
    
    def train(self, df):
        """Train the model on transaction data"""
        print("\n=== Training Transaction Categorizer ===\n")
        
        # Preprocess
        df['clean_description'] = df['description'].apply(self.preprocess_text)
        
        # Store categories
        self.categories = sorted(df['category'].unique())
        print(f"Categories: {', '.join(self.categories)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df['clean_description'], 
            df['category'],
            test_size=0.2,
            random_state=42,
            stratify=df['category']
        )
        
        print(f"\nTraining samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")
        
        # Vectorize
        print("\n→ Vectorizing text...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model
        print("→ Training ensemble model...")
        self.model.fit(X_train_vec, y_train)
        
        # Cross-validation
        try:
            cv_scores = cross_val_score(self.model, X_train_vec, y_train, cv=5, scoring='f1_macro')
            print(f"\n✓ Cross-validation F1 (macro): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        except Exception as e:
            print(f"CV skipped due to small dataset: {e}")
            cv_mean = 0
            cv_std = 0
        
        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        
        # Metrics
        print("\n=== Model Performance ===\n")
        print(classification_report(y_test, y_pred, zero_division=0))
        
        # Save metrics
        metrics = {
            'f1_macro': f1_score(y_test, y_pred, average='macro'),
            'f1_weighted': f1_score(y_test, y_pred, average='weighted'),
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'categories': self.categories,
            'timestamp': datetime.now().isoformat()
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=self.categories)
        self._plot_confusion_matrix(cm, self.categories)
        
        return metrics, X_test, y_test, y_pred
    
    def _plot_confusion_matrix(self, cm, categories):
        """Visualize confusion matrix"""
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=categories, yticklabels=categories)
        plt.title('Confusion Matrix - Transaction Categorization')
        plt.ylabel('True Category')
        plt.xlabel('Predicted Category')
        plt.tight_layout()
        plt.savefig('outputs/confusion_matrix.png', dpi=150)
        print("\n✓ Confusion matrix saved to outputs/confusion_matrix.png")
        plt.close()
    
    def save_model(self, path='models/'):
        """Save trained model and vectorizer"""
        os.makedirs(path, exist_ok=True)
        
        with open(f'{path}model.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(f'{path}vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(f'{path}categories.pkl', 'wb') as f:
            pickle.dump(self.categories, f)
        
        print(f"\n✓ Model saved to {path}")

def generate_and_save_config(categories_config, path='config/taxonomy.yaml'):
    """Generate YAML config based on synthetic data definitions"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    yaml_structure = {'categories': []}
    
    for cat_name, keywords in categories_config.items():
        # Use the merchants list as keywords for the rule engine
        yaml_structure['categories'].append({
            'name': cat_name,
            'threshold': 0.7,
            'keywords': keywords,
            'description': f'Transactions related to {cat_name.lower()}'
        })
        
    with open(path, 'w') as f:
        yaml.dump(yaml_structure, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Generated taxonomy configuration at {path}")

def generate_synthetic_data(n_samples=1000):
    """Generate synthetic transaction data for demonstration"""
    
    # Define Categories and associated Keywords/Merchants
    categories_config = {
        'Coffee/Dining': [
            'Starbucks', 'Dunkin Donuts', 'McDonalds', 'Subway', 'Pizza Hut',
            'KFC', 'Dominos', 'Chipotle', 'Panera Bread', 'Cafe Coffee Day',
            'Local Restaurant', 'Food Court', 'Dinner', 'Lunch'
        ],
        'Fuel': [
            'Shell Gas', 'Chevron', 'BP Station', 'Exxon', 'Indian Oil',
            'HP Petrol', 'Bharat Petroleum', 'Gas Station', 'Fuel Stop'
        ],
        'Groceries': [
            'Walmart', 'Target', 'Whole Foods', 'Costco', 'Safeway',
            'BigBasket', 'DMart', 'Reliance Fresh', 'Supermarket', 'Grocery Store'
        ],
        'Shopping': [
            'Amazon', 'Flipkart', 'Myntra', 'AJIO', 'H&M', 'Zara',
            'Nike Store', 'Adidas', 'Apple Store', 'Best Buy', 'Mall Purchase'
        ],
        'Healthcare': [
            'Apollo Pharmacy', 'CVS Pharmacy', 'Walgreens', 'Medical Center',
            'Dental Clinic', 'Hospital', 'Lab Test', 'Doctor Visit'
        ],
        'Transportation': [
            'Uber', 'Lyft', 'Ola Cab', 'Metro Card', 'Bus Pass',
            'Railway Ticket', 'Parking Fee', 'Toll Plaza'
        ],
        'Entertainment': [
            'Netflix', 'Amazon Prime', 'Spotify', 'Movie Theater',
            'PVR Cinemas', 'Gaming Store', 'Concert Ticket'
        ],
        'Utilities': [
            'Electric Bill', 'Water Bill', 'Internet Bill', 'Phone Bill',
            'Gas Bill', 'Airtel', 'Jio', 'Vodafone'
        ],
        'Education': [
            'Coursera', 'Udemy', 'Book Store', 'School Fee',
            'Tuition Payment', 'Online Course', 'Library'
        ],
        'Fitness': [
            'Gym Membership', 'Yoga Studio', 'Sports Equipment',
            'Fitness Center', 'Swimming Pool'
        ]
    }
    
    data = []
    for category, merchants in categories_config.items():
        samples_per_category = n_samples // len(categories_config)
        for _ in range(samples_per_category):
            merchant = np.random.choice(merchants)
            # Add some noise
            noise = ['', ' Downtown', ' Online', ' Store', ' #123', ' - Purchase']
            description = merchant + np.random.choice(noise)
            amount = np.random.uniform(5, 500)
            
            data.append({
                'description': description,
                'amount': round(amount, 2),
                'category': category
            })
    
    df = pd.DataFrame(data)
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df, categories_config

if __name__ == "__main__":
    # Create directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    print("=" * 60)
    print("AI TRANSACTION CATEGORIZER - TRAINING PIPELINE")
    print("=" * 60)
    
    # Generate synthetic data
    print("\n→ Generating synthetic transaction data...")
    df, cat_config = generate_synthetic_data(n_samples=1000)
    df.to_csv('data/synthetic_transactions.csv', index=False)
    print(f"✓ Generated {len(df)} transactions")
    print(f"✓ Saved to data/synthetic_transactions.csv")
    
    # Generate taxonomy.yaml based on the data generation rules
    # This ensures the Rule Engine matches the Training Data
    generate_and_save_config(cat_config)
    
    # Initialize and train
    categorizer = TransactionCategorizer()
    
    metrics, X_test, y_test, y_pred = categorizer.train(df)
    
    # Save model
    categorizer.save_model()
    
    # Save metrics
    with open('outputs/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\nMacro F1 Score: {metrics['f1_macro']:.3f}")
    print(f"Weighted F1 Score: {metrics['f1_weighted']:.3f}")
    print("\nNext steps:")
    print("1. Run 'streamlit run app.py' to test the demo")
    print("2. Check outputs/ folder for metrics and visualizations")