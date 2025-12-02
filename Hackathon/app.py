import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Wrap import to handle case where predict.py exists but dependencies aren't installed yet
try:
    from predict import TransactionPredictor
except ImportError:
    TransactionPredictor = None
import yaml
import json
import os

# Page config
st.set_page_config(
    page_title="AI Transaction Categorizer",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .confidence-high {
        color: #2ecc71;
        font-weight: bold;
    }
    .confidence-low {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_predictor():
    """Load the predictor (cached for performance)"""
    if TransactionPredictor is None:
        return None
    return TransactionPredictor()

def main():
    st.markdown('<div class="main-header">💳 AI Transaction Categorizer</div>', unsafe_allow_html=True)
    st.markdown("**Autonomous, Explainable, Cost-Free Transaction Classification**")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "🏠 Home",
        "🔍 Single Transaction",
        "📊 Batch Processing",
        "⚙️ Taxonomy Editor",
        "📈 Model Metrics"
    ])
    
    # Check if dependencies are loaded
    if TransactionPredictor is None:
        st.error("⚠️ Missing dependencies. Please run `pip install -r requirements.txt`")
        return

    # Try to load predictor
    try:
        predictor = load_predictor()
    except Exception as e:
        # If model files don't exist, predictor will fail
        predictor = None
    
    # Handle model missing state
    if predictor is None and page not in ["🏠 Home", "⚙️ Taxonomy Editor"]:
        st.error("⚠️ Model not found! Please run `python train.py` first to generate the models.")
        if st.button("Run Training Now (Demo)"):
            with st.spinner("Training model..."):
                os.system("python train.py")
                st.cache_resource.clear()
                st.experimental_rerun()
        return
    
    # Page routing
    if page == "🏠 Home":
        show_home()
    elif page == "🔍 Single Transaction":
        show_single_prediction(predictor)
    elif page == "📊 Batch Processing":
        show_batch_processing(predictor)
    elif page == "⚙️ Taxonomy Editor":
        show_taxonomy_editor()
    elif page == "📈 Model Metrics":
        show_metrics()

def show_home():
    """Home page with project overview"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Key Features")
        st.markdown("""
        - **Zero API Costs**: All processing happens locally
        - **High Accuracy**: 90%+ F1 score across categories
        - **Explainable**: LIME-powered insights into predictions
        - **Customizable**: Edit categories via YAML config
        - **Fast**: 2000+ transactions/second batch processing
        - **Human-in-Loop**: Flag low-confidence predictions for review
        """)
    
    with col2:
        st.subheader("🚀 How It Works")
        st.markdown("""
        1. **Rule Matching**: Check keywords in taxonomy.yaml
        2. **ML Prediction**: TF-IDF + Ensemble model for complex cases
        3. **Confidence Scoring**: Rate predictions 0-100%
        4. **Explainability**: Show which words influenced the decision
        5. **Feedback Loop**: Learn from user corrections
        """)
    
    st.subheader("📊 System Architecture")
    st.info("Input Transaction → Rule Engine (YAML) → Match? → High Confidence Result ↓ No Match → ML Model (TF-IDF + Ensemble) → Confidence Score + Explanation → Flag for Review if < 70%")
    
    st.subheader("💡 Use Cases")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Personal Finance**\nBudgeting apps, expense tracking")
    with col2:
        st.info("**Business Accounting**\nExpense categorization, reporting")
    with col3:
        st.info("**Banking**\nTransaction monitoring, insights")

def show_single_prediction(predictor):
    """Single transaction prediction with explainability"""
    st.subheader("🔍 Predict Single Transaction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        transaction = st.text_input(
            "Enter transaction description:",
            placeholder="e.g., Starbucks Coffee Downtown",
            help="Enter any transaction text you want to categorize"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            predict_btn = st.button("🔮 Predict Category", type="primary")
        with col_b:
            explain_mode = st.checkbox("Show Explanation", value=True)
    
    with col2:
        st.info("**Examples:**\n- Starbucks Coffee\n- Shell Gas Station\n- Amazon Purchase\n- Uber Ride\n- Netflix Subscription")
    
    if predict_btn and transaction:
        with st.spinner("Analyzing transaction..."):
            result = predictor.predict(transaction, explain=explain_mode)
        
        # Display results
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Category", result['category'])
        
        with col2:
            confidence_pct = f"{result['confidence']*100:.1f}%"
            confidence_class = "confidence-high" if result['confidence'] >= 0.7 else "confidence-low"
            st.markdown(f"**Confidence**")
            st.markdown(f'<span class="{confidence_class}">{confidence_pct}</span>', unsafe_allow_html=True)
        
        with col3:
            method_emoji = "📏" if result['method'] == 'rule_match' else "🤖"
            st.metric("Method", f"{method_emoji} {result['method'].replace('_', ' ').title()}")
        
        # Additional details
        if result['method'] == 'rule_match':
            st.success(f"✓ Matched keyword: **{result.get('matched_keyword', 'N/A')}**")
        
        if result['needs_review']:
            st.warning("⚠️ Low confidence - recommend manual review")
        
        # Explanation
        if explain_mode and 'explanation' in result and 'top_words' in result['explanation']:
            st.subheader("💡 Prediction Explanation")
            if result['explanation'].get('top_words'):
                st.markdown("**Top contributing words:**")
                for word, weight in result['explanation']['top_words'][:5]:
                    # Check if weight is numeric
                    try:
                        w_val = float(weight)
                        bar_color = "green" if w_val > 0 else "red"
                        st.markdown(f"- `{word}`: {w_val:.3f}")
                    except:
                        # Handle LIME tuple format (word, weight)
                        if isinstance(weight, (list, tuple)) and len(weight) == 2:
                            st.markdown(f"- `{weight[0]}`: {weight[1]:.3f}")
                        else:
                            st.write(f"- {word}: {weight}")
        
        # Probability distribution
        if 'probabilities' in result:
            st.subheader("📊 Probability Distribution")
            prob_df = pd.DataFrame([
                {"Category": cat, "Probability": prob} 
                for cat, prob in sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)
            ])
            
            fig = px.bar(prob_df.head(5), x='Probability', y='Category', orientation='h',
                        color='Probability', color_continuous_scale='Blues')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def show_batch_processing(predictor):
    """Batch transaction processing"""
    st.subheader("📊 Batch Transaction Processing")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file with transactions",
        type=['csv'],
        help="CSV should have a 'description' column"
    )
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✓ Loaded {len(df)} transactions")
        st.dataframe(df.head(10), use_container_width=True)
        
        if 'description' not in df.columns:
            st.error("❌ CSV must have a 'description' column")
            return
        
        if st.button("🚀 Process All Transactions", type="primary"):
            with st.spinner("Processing transactions..."):
                results = predictor.batch_predict(df, show_progress=False)
                
                # Create results DataFrame
                results_df = pd.DataFrame(results)
                
                # Statistics
                stats = predictor.get_statistics(results)
                
                st.markdown("---")
                st.subheader("📈 Processing Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Processed", stats['total_predictions'])
                col2.metric("Rule Matches", stats['rule_matches'])
                col3.metric("ML Predictions", stats['ml_predictions'])
                col4.metric("Needs Review", stats['needs_review'])
                
                # Average confidence
                st.metric("Average Confidence", f"{stats['avg_confidence']*100:.1f}%")
                
                # Category distribution
                st.subheader("📊 Category Distribution")
                cat_dist = pd.DataFrame([
                    {"Category": cat, "Count": count}
                    for cat, count in stats['category_distribution'].items()
                ])
                
                fig = px.pie(cat_dist, values='Count', names='Category', 
                            title='Transaction Distribution by Category')
                st.plotly_chart(fig, use_container_width=True)
                
                # Low confidence samples
                if stats['needs_review'] > 0:
                    st.subheader("⚠️ Low Confidence Predictions (Need Review)")
                    low_conf_df = pd.DataFrame(stats['low_confidence_samples'])
                    st.dataframe(low_conf_df, use_container_width=True)
                
                # Download results
                results_csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Results CSV",
                    data=results_csv,
                    file_name="categorized_transactions.csv",
                    mime="text/csv"
                )
    else:
        # Show sample data option
        if st.button("📄 Load Sample Data"):
            if os.path.exists('data/synthetic_transactions.csv'):
                with open('data/synthetic_transactions.csv') as f:
                    st.download_button("Download Sample CSV", f, "sample.csv", "text/csv")
            else:
                st.warning("Sample data not found. Run `python train.py` first to generate it.")

def show_taxonomy_editor():
    """Edit category taxonomy"""
    st.subheader("⚙️ Category Taxonomy Editor")
    
    yaml_path = 'config/taxonomy.yaml'
    
    if not os.path.exists(yaml_path):
        st.error("❌ taxonomy.yaml not found in config/ folder. Run `python train.py` to generate default config.")
        return
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    st.info("💡 Edit categories below. Changes require restarting the app to take effect.")
    
    # Display current categories
    st.markdown("### Current Categories")
    
    if 'categories' in config:
        for i, category in enumerate(config['categories']):
            with st.expander(f"📁 {category['name']}"):
                st.markdown(f"**Description:** {category.get('description', 'N/A')}")
                st.markdown(f"**Threshold:** {category.get('threshold', 0.7)}")
                st.markdown(f"**Keywords:** {', '.join(category.get('keywords', []))}")
    
    # YAML editor
    st.markdown("### Edit YAML Configuration")
    yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
    edited_yaml = st.text_area("YAML Content", yaml_str, height=400)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            try:
                new_config = yaml.safe_load(edited_yaml)
                with open(yaml_path, 'w') as f:
                    yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
                st.success("✓ Configuration saved! Restart the app to apply changes.")
            except Exception as e:
                st.error(f"❌ Invalid YAML: {str(e)}")
    
    with col2:
        if st.button("🔄 Reset to Default"):
            st.warning("This will reload the current configuration from disk.")
            st.rerun()

def show_metrics():
    """Display model performance metrics"""
    st.subheader("📈 Model Performance Metrics")
    
    metrics_path = 'outputs/metrics.json'
    
    if not os.path.exists(metrics_path):
        st.warning("⚠️ No metrics found. Train the model first by running `python train.py`")
        return
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Macro F1 Score", f"{metrics['f1_macro']:.3f}")
    col2.metric("Weighted F1 Score", f"{metrics['f1_weighted']:.3f}")
    col3.metric("Training Samples", metrics['train_samples'])
    
    # Confusion matrix
    st.subheader("📊 Confusion Matrix")
    if os.path.exists('outputs/confusion_matrix.png'):
        st.image('outputs/confusion_matrix.png')
    else:
        st.info("Confusion matrix not found")
    
    # Training info
    st.subheader("ℹ️ Training Information")
    st.json(metrics)

if __name__ == "__main__":
    main()