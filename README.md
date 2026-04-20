# Intelligent News Assistant – System Overview

## 1. Problem Context

The objective is to design an **Intelligent Assistant** that automatically:

* Collects news articles from Vietnamese online newspapers
* Filters and processes relevant information
* Produces a **weekly summary report** for a selected domain

### Data Sources

* VnExpress
* Thanh Nien
* Tuoi Tre

### Domain Scope

One of the following topics:

* Fashion
* Sports
* Entertainment
* Technology

### Time Constraint

* Focus on **news within the last 7 days**

---

## 2. System Objectives

The system should generate a structured weekly report consisting of:

### 2.1 Executive Summary

* High-level overview of the week's developments
* Identification of dominant trends
* Key events and shifts in the domain

### 2.2 Trending Keywords

* Extracted keywords representing:

  * Topics with high frequency
  * Emerging themes
  * Named entities (people, organizations, products)

### 2.3 Highlighted News

* Curated list of important articles
* Each item includes:

  * Title
  * Short summary
  * Source link

---

## 3. System Architecture

### 3.1 Data Ingestion Layer

**Function:**

* Crawl or fetch articles from defined sources

**Approaches:**

* RSS feeds (preferred for stability)
* Web scraping (fallback when RSS unavailable)

---

### 3.2 Data Filtering Layer

**Function:**

* Remove irrelevant or outdated articles

**Techniques:**

* Time-based filtering (last 7 days)
* Topic classification (rule-based or ML-based)

---

### 3.3 NLP Processing Layer

**Function:**
Transform raw text into structured insights

**Subcomponents:**

* Tokenization & normalization
* Keyword extraction (TF-IDF, KeyBERT, or embedding-based methods)
* Named Entity Recognition (NER)
* Topic clustering

---

### 3.4 Summarization Engine

**Function:**
Generate concise summaries

**Approaches:**

* Extractive summarization (TextRank, LexRank)
* Abstractive summarization (Transformer-based models, LLMs)

---

### 3.5 Ranking & Selection Module

**Function:**
Identify “highlighted news”

**Criteria:**

* Source credibility
* Article engagement (if available)
* Keyword density / importance
* Semantic relevance

---

### 3.6 Report Generation Layer

**Function:**
Produce structured output

**Output Format:**

* Markdown / JSON / HTML

---

## 4. Core Functionalities

### 4.1 Automated News Collection

* Periodic ingestion pipeline (daily or hourly)
* Deduplication of articles

---

### 4.2 Topic Classification

* Assign each article to the selected domain
* Optional: multi-label classification

---

### 4.3 Keyword Extraction

* Generate top-N keywords
* Capture both frequency and semantic importance

---

### 4.4 Summarization

* Article-level summaries
* Global summary (executive summary)

---

### 4.5 Highlight Detection

* Rank and select top-K important articles

---

### 4.6 Report Assembly

* Combine all components into final structured report

---

## 5. Recommended Technical Stack

### 5.1 Data Collection

* `requests`, `BeautifulSoup`, `newspaper3k`
* RSS parsers

---

### 5.2 NLP & Processing

* Classical:

  * TF-IDF (scikit-learn)
* Advanced:

  * Sentence Transformers (semantic similarity)
  * KeyBERT (keyword extraction)
  * spaCy / underthesea (Vietnamese NLP)

---

### 5.3 Summarization

* Lightweight:

  * TextRank
* Advanced:

  * Pretrained Transformer models
  * LLM APIs (if allowed)

---

### 5.4 Storage

* Local: JSON / SQLite
* Scalable: MongoDB / PostgreSQL

---

### 5.5 Pipeline Orchestration

* Simple: Python scripts + cron jobs
* Advanced: Airflow / Prefect

---

## 6. Design Recommendations

### 6.1 Start Simple, Then Scale

* Begin with:

  * RSS ingestion
  * TF-IDF keywords
  * Extractive summarization
* Then upgrade to:

  * Embedding-based ranking
  * LLM summarization

---

### 6.2 Prioritize Data Quality

* Deduplicate articles aggressively
* Normalize encoding (Vietnamese text handling)

---

### 6.3 Modular Architecture

* Separate:

  * Data ingestion
  * Processing
  * Output generation

This enables:

* Easier debugging
* Independent scaling

---

### 6.4 Evaluation Strategy

* Manual validation of summaries
* Keyword relevance checks
* Compare extracted highlights with real trending news

---

### 6.5 Optional Enhancements

* Sentiment analysis of news
* Trend evolution over time
* Visualization dashboard

---

## 7. Expected Deliverables

### 7.1 Source Code

* GitHub repository
* Clear project structure
* README with setup instructions

---

### 7.2 Technical Report

Should include:

* System architecture
* Implementation details
* Design decisions
* Sample weekly report output

---

## 8. Summary

This system is essentially a **pipeline combining data engineering and NLP**, with three core goals:

1. **Aggregate** relevant news data
2. **Extract** meaningful insights
3. **Summarize** into a human-readable weekly report

A well-designed solution should balance:

* Simplicity (for reliability)
* Scalability (for future extension)
* Interpretability (for evaluation and debugging)

---
