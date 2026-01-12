# AI Insights Integration Guide

## Overview
The dashboard now includes AI-powered insights using Google Gemini API. This provides intelligent analysis across multiple dashboard sections.

## Setup Instructions

### 1. Obtain Gemini API Key
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key
- Copy the key

### 2. Configure Secrets
Add your API key to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

**Important:** Keep this file in `.gitignore` - never commit API keys to version control!

### 3. Install Dependencies
```bash
pip install google-generativeai
```

## AI Features Integrated

### 📊 Executive Suite
**🔮 AI-Powered Deep Insights**
- Analyzes KPI data (revenue, margin, returns)
- Provides strategic recommendations
- Identifies areas of concern
- Located as expandable section after rule-based insights

### 📈 Trends & Performance
**🤖 AI Analysis of Trends**
- Analyzes revenue and margin patterns
- Identifies seasonal trends
- Provides predictions for next period
- Expandable section below weekly data

### 🏪 Operations - Inventory
**🤖 AI Analysis of Inventory**
- Evaluates inventory health
- Identifies reorder priorities
- Recommends stockout prevention strategies
- Expandable section after inventory distribution chart

### 🔍 Operations - Data Quality
**🤖 AI Analysis of Data Quality**
- Rates overall data quality
- Prioritizes issues to fix
- Suggests quick wins
- Expandable section after quality metrics

## Files Modified

### New Files
- `.streamlit/utils/ai_insights.py` - AI insight generation functions
- `.streamlit/utils/__init__.py` - Package initialization

### Modified Files
- `app.py` - Integrated AI insights across dashboard sections

## API Functions Available

```python
initialize_gemini(api_key)           # Initialize Gemini API
generate_kpi_insights(model, kpi_data) # Analyze KPI data
generate_chart_insights(model, data_summary, chart_type)  # Analyze charts
generate_simulation_insights(model, sim_results, violations)  # Analyze campaigns
generate_inventory_insights(model, inventory_summary)  # Analyze inventory
generate_data_quality_insights(model, quality_metrics, issues)  # Analyze data quality
```

## Performance Notes

- AI generation takes 2-10 seconds depending on API load
- Insights appear in collapsible sections (not blocking main display)
- Gracefully handles API errors with user-friendly warnings
- All AI functions include error handling

## Cost Considerations

- Gemini API is free tier for reasonable usage
- Monitor your usage in [Google AI Console](https://aistudio.google.com/)
- Each dashboard view generates 1-3 API calls

## Troubleshooting

### "Gemini API key not found"
- Verify `.streamlit/secrets.toml` exists
- Check API key is correctly formatted
- Restart Streamlit after updating secrets

### "Could not initialize AI"
- Ensure `google-generativeai` package is installed
- Check API key is valid
- Verify internet connection

### Slow AI responses
- This is normal for first request (cold start)
- Subsequent requests are faster
- API may be experiencing load - try again

## Security Best Practices

1. ✅ Store API keys in `secrets.toml`
2. ✅ Add `.streamlit/secrets.toml` to `.gitignore`
3. ✅ Use environment variables in production
4. ✅ Never commit credentials to version control
5. ✅ Rotate API keys periodically
