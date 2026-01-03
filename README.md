# MBS Chatbot - Mortgage-Backed Securities Analysis System

A sophisticated chatbot system for analyzing mortgage-backed securities (MBS) with RAG architecture, specializing in TBA (To Be Announced) securities and pool factor analysis.

## Features

### Core Capabilities
- **RAG Architecture**: Advanced retrieval-augmented generation with vector database for business rules
- **TBA Analysis**: Comprehensive analysis of To Be Announced mortgage-backed securities
- **Pool Factor Analysis**: Detailed pool factor calculations and prepayment rate analysis
- **Multi-format Responses**: Tabular data, pie charts, and report summaries
- **Interactive Chat Interface**: Modern web-based chat UI with real-time responses

### Technical Features
- **Vector Database**: ChromaDB for efficient business rule retrieval
- **Semantic Search**: Sentence transformers for intelligent question understanding
- **Data Visualization**: Plotly charts for interactive data presentation
- **REST API**: FastAPI backend with comprehensive endpoints
- **Sample Data**: Pre-populated with realistic MBS data for demonstration

## Architecture

```
mbs-chatbot/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── static/
│   └── index.html         # Frontend chat interface
└── app/
    ├── __init__.py
    ├── rag_engine.py      # RAG architecture with vector database
    ├── mbs_analyzer.py    # MBS data analysis logic
    ├── pool_factor_analyzer.py  # Advanced pool factor calculations
    └── response_formatter.py    # Response formatting and visualization
```

## Installation

1. **Clone and navigate to the project**:
   ```bash
   cd mbs-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the chatbot**:
   Open your browser and navigate to `http://localhost:8000/static/index.html`

## API Endpoints

### Chat Endpoint
- **POST** `/chat`
  - Request: `{"question": "string", "session_id": "string"}`
  - Response: `{"answer": "string", "tables": [], "charts": [], "summary": "string", "session_id": "string"}`

### Health Check
- **GET** `/health`
  - Returns: `{"status": "healthy"}`

## Sample Questions

The chatbot can handle various types of MBS-related questions:

### TBA Securities
- "What is the current TBA market analysis?"
- "Show me agency distribution in TBA securities"
- "Compare TBA pricing across different agencies"

### Pool Factor Analysis
- "Show me pool factor analysis for all pools"
- "Analyze prepayment rates across the portfolio"
- "How do pool factors affect cash flows?"

### Performance Metrics
- "What are the current yield spreads?"
- "What is the weighted average duration?"
- "Compare performance between FNMA and FHLMC securities"

### Comparative Analysis
- "Compare performance between different agencies"
- "Show me differences in coupon rates"
- "Which agency has the best yield?"

## Business Rules

The system includes comprehensive business rules for MBS analysis:

- **TBA Securities**: Definition, pricing factors, agency types
- **Pool Factors**: Calculation methods, prepayment metrics
- **Agency MBS**: Ginnie Mae, Fannie Mae, Freddie Mac characteristics
- **Prepayment Metrics**: CPR, SMM, PSA benchmarks
- **Performance Metrics**: WAC, WAM, duration calculations

## Data Models

### TBA Securities Data
- CUSIP identifiers
- Agency types (FNMA, FHLMC, GNMA)
- Coupon rates and settlement dates
- Pricing and yield information
- Duration metrics

### Pool Factor Data
- Pool identifiers and dates
- Current and original balances
- Pool factor ratios
- Weighted Average Coupon (WAC)
- Weighted Average Maturity (WAM)

## Response Formats

### Tables
Structured data presentation with:
- TBA securities summaries
- Pool factor analysis
- Performance metrics
- Agency comparisons

### Charts
Interactive visualizations including:
- Agency distribution pie charts
- Pool health distribution
- Performance trend analysis
- Yield spread comparisons

### Summaries
Concise report summaries highlighting:
- Key insights and findings
- Risk assessments
- Performance indicators
- Recommendations

## Advanced Features

### Pool Factor Analysis
- **Prepayment Speed Calculations**: CPR and SMM conversions
- **Cash Flow Projections**: Future payment schedules
- **Health Scoring**: Pool quality assessments
- **Concentration Risk**: Portfolio diversification analysis

### RAG Capabilities
- **Semantic Search**: Intelligent business rule retrieval
- **Context Awareness**: Question-specific rule selection
- **Dynamic Learning**: Add new business rules runtime

## Configuration

### Environment Variables
Create a `.env` file for configuration:
```env
# Optional: OpenAI API key for enhanced responses
OPENAI_API_KEY=your_api_key_here

# Optional: Custom model settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Custom Business Rules
Add new business rules through the API:
```python
await rag_engine.add_business_rule(
    rule_content="Your new business rule",
    category="custom_category",
    keywords=["relevant", "keywords"]
)
```

## Development

### Adding New Analysis Types
1. Extend `MBSAnalyzer` class with new analysis methods
2. Update response formatter for new data types
3. Add corresponding visualization templates

### Customizing Visualizations
Modify chart templates in `ResponseFormatter`:
- Pie charts for distributions
- Bar charts for comparisons
- Line charts for trends
- Custom Plotly configurations

## Testing

### Sample Data
The system includes realistic sample data for:
- 10 TBA securities across 3 agencies
- 5 mortgage pools with 24 months of history
- Various coupon rates and performance metrics

### API Testing
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the current TBA analysis?"}'
```

## Performance

### Vector Database
- ChromaDB for efficient similarity search
- Persistent storage for business rules
- Fast retrieval with sentence transformers

### Response Generation
- Parallel processing for analysis and formatting
- Cached embeddings for improved performance
- Optimized data structures for large datasets

## Security

- CORS configuration for web access
- Input validation and sanitization
- Error handling for robust operation
- Session management for conversation context

## License

This project is provided as a demonstration of MBS analysis capabilities with RAG architecture.

## Support

For questions or issues with the MBS Chatbot system, please refer to the documentation or check the API health endpoint at `/health`.
