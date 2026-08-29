# DataMorph Studio - Production-Level ML Data Preprocessing Platform

DataMorph Studio is an enterprise-grade Machine Learning data preprocessing, feature engineering, and data quality orchestration platform built natively in Python.

---

## 1. Installation

### Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/Tassuu7/project-6-Ml-System-repo.git
cd project-6-Ml-System-repo

# Create and activate Python virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
npm install
```

---

## 2. Build

### Verify Build and Architecture
```bash
# Verify production LOC and code structure
python measure.py

# Docker container build
docker build -t datamorph-studio:v2.4 .
```

---

## 3. Run

### Start the Application Server
```bash
python run_server.py
```
- **Local Application URL**: `http://localhost:8000`
- **Login Portal**: `http://localhost:8000/login.html`
- **Default Username**: `admin`
- **Default Password**: `admin123`

---

## 4. Dependencies

### Python & Environment
- **Runtime**: Python 3.8+ (Zero mandatory binary dependencies)
- **Manifests**: `requirements.txt`, `package.json`
- **Lockfiles**: `package-lock.json`

---

## 5. Usage

### Interactive Web Studio
1. **Data Ingestion**: Click **Load Sample Data** or upload any CSV/JSON file to view live tabular records, dimensions, missing value ratios, and quality scores.
2. **DAG Pipeline Builder**: Select transformers from the palette to construct a dependency graph, execute pipeline stages, and view transformed outputs.
3. **Transformer Sandbox**: Test individual algorithms on specific feature columns in real-time.
4. **Data Drift Monitor**: Calculate Population Stability Index (PSI) and Kolmogorov-Smirnov statistics to detect distribution shift.
5. **Code Generator**: Export the visual DAG recipe into a standalone Python deployment script.

### Running Unit Test Suites
```bash
python -m unittest discover tests
```
