"""Build the portfolio and Markdown articles/notes into _site for GitHub Pages."""
from pathlib import Path
from datetime import date, datetime, timezone
from html import escape
from urllib.parse import quote
import argparse
import json
import re
import shutil
import xml.etree.ElementTree as ET
import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
CONFIG = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
PROFILE = json.loads((ROOT / 'content/profile.json').read_text(encoding='utf-8'))
CONFIG.update(name='Muhammad Saad Uddin', title='Applied AI Scientist')
BASE = CONFIG.get('base_path', '').rstrip('/')
ORIGIN = CONFIG['url'].rstrip('/')
NAV = [('Home', '/'), ('Work', '/work/'), ('Writing', '/writing/'), ('Notes', '/notes/'), ('Platforms', '/platforms/'), ('Speaking', '/speaking/'), ('About', '/about/')]
PAGES = []

def e(value): return escape(str(value), quote=True)
def url(path): return BASE + '/' + path.lstrip('/')
def absolute(path): return ORIGIN + url(path)
def a(path, label, cls='text-link'):
    return f'<a class="{cls}" href="{e(url(path))}">{label}</a>'
def tags(items): return '<div class="tags">' + ''.join(f'<span class="tag">{e(t)}</span>' for t in items) + '</div>'
def nice_date(value): return value.strftime('%d %b %Y')

# Project media lives in images/projects/<slug>/ and
# assets/workflows/<slug>/index.html. Missing media is optional.
BIO = [
    "I'm Muhammad Saad Uddin, an Applied AI Scientist driven by curiosity about AI and mathematics. My work focuses on explainable AI, multi-agent workflows, and the architectures that bring them together.",
    "I share ideas on Medium and LinkedIn, speak and train on AI, and find inspiration in books and poetry both reading it and writing my own."
]


def project(number, slug, title, category, banner, description, skills,
            workflow=False, legacy=()):
    return dict(number=number, slug=slug, title=title, category=category,
                banner=banner, description=description, tags=skills.split('|'),
                workflow=workflow, legacy=legacy)


PROJECTS = [
    project(1, 'purchase-order-automation', 'Multi Agent Purchase Order Automation',
        'Enterprise AI & Agents', 'Documents → SAP',
        'Architected, built, and deployed an end to end multi agent workflow from discovery and technical scoping through production rollout. Integrated document extraction, validation, XML creation, SAP submission, observability, and human verification. Improved processing efficiency by 90% and reduced delivery cost to less than 25% of the previous workflow.',
        'Multi-Agent Workflows|Document Intelligence|SAP Integration|Human in theLoop|Observability|Solution Architecture', True),
    project(2, 'enterprise-rag', 'Enterprise RAG & Knowledge Search',
        'Enterprise AI & Agents', 'Knowledge → Answers',
        'Built production knowledge retrieval using Azure search and LLMs. Defined approaches for retrieval design, context engineering, evaluation, and knowledge access. Deployed the solution in late 2023 and presented the work at Machine Learning Week Europe 2024.',
        'RAG|Azure AI Search|Vector Search|Semantic Search|LangChain|Azure OpenAI|Evaluation', True),
    project(3, 'sustainability-reporting', 'Agentic Sustainability Reporting',
        'Enterprise AI & Agents', 'Sources → Reports',
        'Created an AI-driven reporting workflow combining RAG, SQL agents, and browser agents to retrieve, analyze, and synthesize information across fragmented internal and external sources.',
        'RAG|LangChain|SQL Agents|Browser Agents|Information Synthesis|Reporting Automation', True),
    project(4, 'feban-extraction', 'FEBAN / Payment Advice Extraction API',
        'Applications & APIs', 'Documents → Data',
        'Built a deployed API for vision based extraction of payment and reference information from PDFs.',
        'FastAPI|Azure OpenAI Vision|PyMuPDF|Structured Extraction|Docker|Kubernetes', True),
    project(5, 'bi-clue-assistant', 'BI CLUE Knowledge Assistant',
        'Enterprise AI & Agents', 'Questions → Evidence',
        'Built conversational access to internal BI knowledge using retrieval planning, MCP integration, and grounded answers with citations.',
        'RAG|MCP|Azure AI Search|Streamlit|Retrieval Planning|Grounding', True),
    project(6, 'product-knowledge-agent', 'Product Knowledge Base Agent',
        'Enterprise AI & Agents', 'Knowledge → Support',
        'Built a Copilot Studio agent that uses an internal technical-document API to answer product questions with sources.',
        'Copilot Studio|API Integration|Knowledge Retrieval|Agent Instructions|Grounding', True),
    project(7, 'pricing-prediction-api', 'Pricing Prediction API',
        'Applications & APIs', 'Models → Service',
        'Served a trained random forest pricing model through an API, including concurrency and deployment configuration.',
        'FastAPI|Random Forests|Model Serving|Concurrency|Docker|Kubernetes', True),
    project(8, 'sap-fraud-detection', 'SAP Transaction Fraud Detection',
        'Machine Learning & Deep Learning', 'Signals → Insight',
        'Developed an autoencoder based system to identify unusual and potentially fraudulent SAP transactions. Combined exploratory data analysis, unsupervised learning, and anomaly detection to support financial risk monitoring.',
        'Autoencoders|Deep Learning|Unsupervised Learning|Anomaly Detection|EDA|SAP', True),
    project(9, 'knowledge-article-generator', 'Human-in-the-Loop Knowledge Article Generator',
        'Enterprise AI & Agents', 'Manuals → Guidance',
        'Built a multi-agent workflow that transforms lengthy product manuals into how-to guides and knowledge articles, with human review of the generated content.',
        'Multi-Agent Systems|LLMs|RAG|Document Processing|Content Generation|Human-in-the-Loop', True),
    project(10, 'survey-feedback-analyzer', 'AI Survey & Feedback Analyzer',
        'Enterprise AI & Agents', 'Feedback → Understanding',
        'Created a multi-agent workflow for reading survey responses, summarizing feedback, identifying sentiment and themes, and producing structured reports.',
        'Multi-Agent Workflows|NLP|Sentiment Analysis|Summarization|Thematic Analysis', True),
    project(11, 'social-media-generator', 'Multi-Agent Social Media Generator',
        'Enterprise AI & Agents', 'Signals → Stories',
        'Built a multi-agent workflow for research, planning, and content generation with human oversight. News, articles, blogs, and previous human-authored posts accumulate in a persistent relationship graph. Agents retrieve relevant information and connections from this growing memory to maintain continuity and improve attention to context, relationships, and factual detail.',
        'Multi-Agent Workflows|Graph-Based Memory|Context Retrieval|Content Generation|Human-in-the-Loop', True),
    project(12, 'baselhack-rag', 'BaselHack 2024 - RAG with Browser & Memory Agents',
        'Enterprise AI & Agents', 'Explore → Remember',
        'Built the winning BaselHack 2024 MDPI solution: a scalable RAG prototype incorporating browser and memory agents.',
        'RAG|Browser Agents|Agent Memory|Prototyping|Hackathon Delivery', True),
    project(13, 'explainable-ai', 'Explainable AI Frameworks',
        'Machine Learning & Deep Learning', 'Models → Understanding',
        'Developed XAI capabilities in R and Python to explain model decisions, improve transparency, and support stakeholder trust and adoption of machine learning.',
        'Python|R|Explainable AI|Model Interpretability|Feature Importance|SHAP|LIME'),
    project(14, 'enterprise-forecasting', 'Enterprise Forecasting on Palantir Foundry',
        'Data Science & Analytics', 'Patterns → Foresight',
        'Built and operationalized forecasting and advanced analytics solutions to support demand planning, business planning, and operational decisions. Evaluated and improved models through structured experimentation and performance analysis.',
        'Palantir Foundry|Predictive Analytics|Statistical Forecasting|Time Series|Model Evaluation'),
    project(15, 'ml-analytics-pipelines', 'Scalable ML & Analytics Pipelines',
        'Data Science & Analytics', 'Data → Scale',
        'Optimized enterprise data-processing and machine learning pipelines using PySpark and parallelization to improve processing efficiency.',
        'PySpark|Parallel Computing|Data Pipelines|Performance Optimization|Enterprise Analytics'),
    project(16, 'competitive-intelligence', 'Competitive Intelligence & Product Trend Forecasting',
        'Data Science & Analytics', 'Markets → Decisions',
        'Integrated data from multiple sources into a competitive intelligence dashboard and applied probabilistic and Bayesian models to forecast product trends.',
        'Data Mining|Data Cleaning|SQL|Dashboards|Bayesian Modeling|Forecasting'),
    project(17, 'sales-churn-analytics', 'Sales, Churn & Operational Analytics',
        'Data Science & Analytics', 'Patterns → Opportunity',
        'Applied predictive analytics to sales, churn, and faults. Used SQL, Python, and geospatial analysis to identify opportunities, declining areas, and actionable business insights.',
        'Python|SQL|Predictive Modeling|Churn Analysis|Geospatial Analytics|Marketing Analytics'),
    project(18, 'movie-recommender', 'Movie Recommendation System on Big Data',
        'Machine Learning & Deep Learning', 'Preferences → Discovery',
        'Built a database-backed recommendation application using MovieLens’s 25 million ratings, with a Streamlit interface and analytical reporting.',
        'Python|Streamlit|SQLAlchemy|SQL|PySpark|Matrix Factorization|Feature Engineering',
        legacy=('images/mov1.jpg','images/mov1.PNG','images/mov2.PNG','images/mov3.PNG')),
    project(19, 'ev-mobility', 'Electric Vehicle Mobility Detection',
        'Machine Learning & Deep Learning', 'Movement → Meaning',
        'Classified electric vehicle states using yearly data across vehicle models and types, incorporating emobpy and ACN data and investigating data drift.',
        'Python|Classification|Predictive Modeling|Time Series|Statistical Analysis|Data Drift',
        legacy=('images/ev1.JPG','images/ev2.JPG','images/ev3.JPG')),
    project(20, 'particle-swarm-optimization', 'Particle Swarm Optimization',
        'Machine Learning & Deep Learning', 'Search → Solutions',
        'Implemented particle swarm optimization for unconstrained numerical optimization problems, including fitness function design and convergence analysis.',
        'Python|Swarm Intelligence|Numerical Optimization|Algorithm Design|Fitness Functions|Convergence Analysis'),
    project(21, 'traffic-sign-detection', 'Traffic Sign Detection & Classification',
        'Machine Learning & Deep Learning', 'Pixels → Recognition',
        'Applied transfer learning with Inception-ResNet-v2 and VGG16 to traffic sign detection and classification.',
        'Computer Vision|Deep Learning|Transfer Learning|Model Fine-Tuning|Data Annotation',
        legacy=('images/obj0.png','images/obj1.PNG','images/obj2.PNG','images/obj3.PNG')),
    project(22, 'boruta-feature-selection', 'Feature Selection with Boruta',
        'Machine Learning & Deep Learning', 'Features → Signal',
        'Implemented Boruta-based feature selection to identify relevant predictors for machine learning models.',
        'Python|Boruta|Feature Selection|Statistical Testing|Model Interpretability|Hyperparameter Tuning'),
    project(23, 'payment-default-prediction', 'Payment Default Prediction',
        'Machine Learning & Deep Learning', 'History → Risk',
        'Compared Azure AutoML and tuned tree-based approaches to predict default from payment history, including attention to imbalanced data and algorithmic bias.',
        'Azure ML|AutoML|Classification|Tree-Based Models|Feature Engineering|Imbalanced Data|Fairness',
        legacy=('images/Az1.jpg', 'images/az1.PNG','images/az2.PNG','images/az3.PNG')),
    project(24, 'human-activity-recognition', 'Human Activity Recognition',
        'Machine Learning & Deep Learning', 'Sensors → Activity',
        'Used deep learning to recognize human activities from sensor data as an IBM Advanced Data Science capstone.',
        'Python|Deep Learning|Sensor Data|Time Series|Statistical Analysis',
        legacy=('images/har1.PNG','images/har2.PNG','images/har3.PNG')),
    project(25, 'geospatial-business-analysis', 'Geospatial Business Opportunity Analysis',
        'Data Science & Analytics', 'Places → Possibilities',
        'Created a dataset from Pakistani government data and used spatial analysis and mapping to identify potential business opportunities within a city.',
        'Python|Folium|Geospatial Analysis|Spatial Data Processing|Public Data|Visualization',
        legacy=('images/fol1.PNG','images/fol2.PNG','images/fol3.PNG')),
    project(26, 'soccer-analysis', 'Soccer Data Analysis & Visualization',
        'Data Science & Analytics', 'The Game → Insight',
        'Explored soccer data and created visualizations to investigate patterns in the sport.',
        'Python|Data Analysis|Data Visualization|JSON',
        legacy=('images/soc1.PNG','images/soc2.PNG','images/soc3.PNG')),
    project(27, 'streamlit-resume', 'Interactive Streamlit Résumé',
        'Applications & APIs', 'Experience → Exploration',
        'Built an interactive résumé with experience navigation, project details, skill visualizations, credentials, and predefined-question chat.',
        'Streamlit|Python|Plotly|Interactive Dashboards|UI Development'),
]

FEATURED = (1, 11)
LEADERSHIP = [
    ('gateway', 'Enterprise LLM Gateway', 'Process & Community Owner',
     'Own the processes and user community around shared access to proprietary and open models, helping colleagues move from model access to practical AI solutions.',
     ['Process Ownership','Community Enablement','LLM Access']),
    ('people', 'E+H AI Community', 'Community Leadership',
     'Lead the community’s direction, connect AI practitioners, and turn shared experience into practical action through use-case showcases, technical exchanges, and collaboration across teams.',
     ['Community Leadership','Use-Case Sharing','Collaboration']),
    ('stage', 'AI Training & Enablement', 'Training & Technical Excellence',
     'Deliver training in basic and advanced prompting, agentic AI, and coding with AI, building practical capability, strengthening engineering practices, and fostering technical excellence across teams.',
     ['Prompting','Agentic AI','Coding with AI']),
    ('work', 'Enterprise AI Architecture & Advisory', 'Architecture & Adoption',
     'Advise teams on Snowflake AI and Azure AI feasibility, architecture choices, experimentation, implementation patterns, and production adoption.',
     ['Solution Architecture','Azure AI','Snowflake AI'])
]

EXTRA_CSS = """
.hero-grid{grid-template-columns:minmax(0,1.35fr) minmax(300px,.85fr);gap:48px}.hero-grid>*{min-width:0}
.hero h1{font-size:clamp(1.8rem,3.2vw,2.7rem);line-height:1.2;max-width:none;white-space:nowrap;margin-bottom:24px}
.portrait{width:100%;max-width:400px;margin:0;padding:18px;justify-self:end;background:var(--amber);border:1px solid var(--amber);border-radius:20px;box-shadow:none;isolation:isolate}.portrait::before{display:none}
.portrait img{width:100%;height:auto;aspect-ratio:auto;object-fit:contain;background:transparent;mix-blend-mode:normal;border-radius:0;clip-path:circle(44.5% at 49% 50%)}
.portrait figcaption{display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 12px;margin:0;padding:12px 4px 4px;font-size:.85rem;overflow-wrap:anywhere;color:var(--ink)}.portrait figcaption strong{color:var(--ink);font-weight:600}
.section-label{display:flex;align-items:center;gap:10px}.section-icon,.credential-symbol,.talk-icon{display:inline-flex;flex:0 0 auto;align-items:center;justify-content:center;background:var(--amber-light);color:var(--amber-dark);border-radius:10px}
.section-icon{width:34px;height:34px}.section-icon svg{width:19px;height:19px}.talk-icon{width:58px;height:58px;margin-bottom:20px;background:var(--blue);color:var(--canvas);border-radius:16px}.talk-icon svg{width:29px;height:29px}
.featured-talk{border:1px solid var(--line);background:var(--white)}.featured-talk .meta{margin-bottom:10px}.site-footer .section-icon{background:#385965;color:#E0B978}
.home-credentials{padding:44px 0}.credential{min-width:0}.credential>div{min-width:0}.credential h3{line-height:1.4}.credential img{flex:0 0 auto}.credential a{display:inline-block;margin-top:9px}.credential-symbol{width:50px;height:50px;background:var(--mist);color:var(--blue)}.credential-symbol svg{width:27px;height:27px}
.work-tagline{display:block;margin-top:20px;font-family:Inter,system-ui,sans-serif;font-size:clamp(1.1rem,2vw,1.5rem);font-weight:500;line-height:1.5;letter-spacing:-.02em;color:var(--blue)}
.stage-intro,.work-intro{max-width:760px;color:var(--body);margin-bottom:30px}.project-card{display:flex;flex-direction:column}.project-card h3{line-height:1.35}.project-card .card-footer{margin-top:auto;padding-top:16px}.project-category{margin-bottom:12px}
.project-media{position:relative;min-height:200px;margin:-27px -27px 24px;padding:24px 24px 88px;background:var(--mist);border-radius:var(--radius) var(--radius) 0 0;display:flex;align-items:center;justify-content:center;overflow:hidden}
.project-media img{width:100%;height:200px;object-fit:contain;background:var(--white)}.project-media.has-image{padding:0 0 64px}.project-banner{position:absolute;bottom:0;left:0;right:0;display:flex;align-items:center;justify-content:center;min-height:64px;padding:14px 18px;background:var(--amber);color:var(--ink);font-size:1.1rem;font-weight:650;line-height:1.3;letter-spacing:0;text-align:center}.project-media>svg{width:56px;height:56px;color:var(--blue)}
.project-detail{max-width:880px;margin:auto}.project-detail .lead{font-size:1.1rem;color:var(--body)}.project-detail h2{font-size:1.9rem;margin-top:36px}.project-gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:24px 0}.gallery-item{padding:10px;background:var(--white);border:1px solid var(--line);border-radius:12px;color:var(--blue);text-align:left}.gallery-item img{width:100%;height:220px;object-fit:contain}.gallery-item span{display:block;font-size:.8rem;margin-top:8px}
.workflow-panel{background:var(--mist);border:1px solid var(--line);padding:28px;border-radius:14px;margin:30px 0}.leadership-card .section-icon{width:44px;height:44px;margin-bottom:18px}.leadership-card .section-icon svg{width:25px;height:25px}
.media-dialog{width:min(1280px,calc(100% - 32px));height:92vh;max-width:none;max-height:96vh;padding:0;border:1px solid var(--line);border-radius:14px;background:var(--canvas);color:var(--ink);overflow:hidden}.media-dialog::backdrop{background:rgba(24,43,53,.75)}.media-dialog[open]{display:flex;flex-direction:column}.media-dialog:fullscreen{width:100%;height:100%;max-height:none;border-radius:0}.media-dialog.is-expanded{position:fixed;inset:0;margin:0;width:100vw;height:100dvh;max-width:none;max-height:none;border-radius:0}
.media-toolbar{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:12px 18px;border-bottom:1px solid var(--line);background:var(--white);flex-wrap:wrap}.media-toolbar h2{font-size:1rem;margin:0;letter-spacing:0}.media-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.media-actions button,.media-actions a{border:1px solid var(--line);border-radius:6px;background:var(--canvas);color:var(--blue);padding:7px 10px;font-size:.8rem;text-decoration:none;cursor:pointer}.media-body{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:auto}.media-body iframe{width:100%;height:100%;border:0;background:white}.media-body img{max-width:100%;max-height:100%;object-fit:contain}.media-status{font-size:.8rem;margin:0;padding:4px 18px;color:var(--body)}
@media(max-width:950px){.hero-grid{grid-template-columns:minmax(0,1.2fr) minmax(260px,.8fr);gap:30px}}
@media(max-width:760px){.hero-grid{grid-template-columns:minmax(0,1fr)}.hero h1{font-size:2rem;white-space:normal}.portrait{max-width:380px;justify-self:start;margin-top:12px}.home-credentials .section-heading{flex-wrap:wrap;gap:14px}.intro-bar{gap:12px}.intro-bar span{padding:6px 10px;background:var(--white);border:1px solid var(--line);border-radius:6px}.project-media{margin:-23px -23px 22px}.project-gallery{grid-template-columns:1fr}.media-dialog{width:calc(100% - 12px);height:95vh}.media-toolbar{padding:10px}.media-toolbar h2{font-size:.9rem}}

:root {
    --workflow-height: 75vh;   /* Height of inline workflow previews */
    --banner-height: 44px;     /* Try 48px, 56px, 72px */
    --banner-background: #294753;
    --banner-text: #F3F6F5;
}

/* Reserve space for the banner */
.project-media {
    padding-bottom: calc(var(--banner-height) + 24px);
    min-height: calc(var(--banner-height) + 136px);
}

.project-media.has-image {
    padding-bottom: var(--banner-height);
}

/* Banner appearance */
.project-banner {
    min-height: var(--banner-height);
    padding: 10px 18px;
    background: var(--banner-background);
    color: var(--banner-text);

    font-size: 1.0rem;
    font-weight: 650;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
}

.credential-media {
    flex:0 0 50px;
    min-width:0;
}
.credential-media.has-image {
    flex-basis:112px;
}
.credential-image-button {
    display:block;
    width:112px;
    padding:8px;
    border:1px solid var(--line);
    border-radius:9px;
    background:var(--white);
    color:var(--blue);
    text-align:center;
    cursor:pointer;
}
.credential-image-button img {
    width:100%;
    height:80px;
    object-fit:contain;
}
.credential-image-button span {
    display:block;
    margin-top:7px;
    font-size:.7rem;
    line-height:1.35;
}
.workflow-embed {
    border:1px solid var(--line);
    border-radius:14px;
    overflow:hidden;
    background:var(--white);
    margin:30px 0;
}
.workflow-toolbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    flex-wrap:wrap;
    padding:16px 20px;
    background:var(--mist);
}
.workflow-toolbar h2 {
    font-size:1.25rem;
    margin:0;
    letter-spacing:-.02em;
}
.workflow-controls {
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    align-items:center;
}
.workflow-controls button,.workflow-controls a {
    border:1px solid var(--line);
    background:var(--white);
    color:var(--blue);
    border-radius:6px;
    padding:7px 12px;
    font:inherit;
    font-size:.85rem;
    cursor:pointer;
    text-decoration:none;
}
.workflow-embed>iframe {
    display:block;
    width:100%;
    height:var(--workflow-height);
    min-height:520px;
    border:0;
    background:var(--white);
}
.workflow-embed:fullscreen,.workflow-embed.is-expanded {
    display:flex;
    flex-direction:column;
    width:100vw;
    height:100dvh;
    margin:0;
    border-radius:0;
    background:var(--white);
}
.workflow-embed.is-expanded {
    position:fixed;
    inset:0;
    z-index:100;
}
.workflow-embed:fullscreen>iframe,.workflow-embed.is-expanded>iframe {
    flex:1;
    min-height:0;
    height:0;
}
.has-expanded-workflow {
    overflow:hidden;
}
@media(max-width:760px) {
    .workflow-toolbar {
        padding:12px;
    }
    .workflow-embed>iframe {
        min-height:440px;
    }
    .credential-media.has-image {
        flex-basis:96px;
    }
    .credential-image-button {
        width:96px;
    }
}

/* Compact experience pages, skill explorer, and achievement galleries. */
.about-block-heading {margin-top:58px}
.experience-book {border:1px solid var(--line);border-radius:18px;background:var(--white);overflow:hidden}
.experience-top {display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 28px;border-bottom:1px solid var(--line);background:var(--mist)}
.experience-status {margin:0;font:500 .85rem/1.5 'JetBrains Mono',monospace;color:var(--blue)}
.experience-controls {display:flex;gap:8px}
.experience-controls button {border:1px solid var(--line);background:var(--white);color:var(--blue);padding:8px 14px;min-height:44px;border-radius:7px;font-size:.85rem;font-weight:600}
.experience-controls button:disabled {opacity:.4;cursor:default}
.experience-controls button:not(:disabled):hover {background:var(--amber-light);border-color:var(--amber)}
.experience-rail {display:grid;grid-auto-flow:column;grid-auto-columns:100%;overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;scroll-behavior:smooth;align-items:start;scrollbar-width:thin;scrollbar-color:var(--soft-blue) transparent;transition:height .2s ease}
.experience-page {min-width:0;padding:30px 34px 34px;scroll-snap-align:start;scroll-snap-stop:always}
.experience-page-top {display:flex;gap:14px;align-items:center;margin-bottom:22px}
.experience-page-top .eyebrow {margin:0;letter-spacing:.06em}
.experience-number {margin-left:auto;font:400 2.6rem/1 Georgia,serif;color:var(--soft-blue)}
.experience-page h3 {font-size:clamp(1.5rem,2.7vw,2.1rem);margin-bottom:10px}
.experience-company {font-weight:600;color:var(--amber-dark);margin-bottom:24px}
.experience-page ul {margin:0;padding-left:20px;color:var(--body);columns:2;column-gap:40px;font-size:.95rem}
.experience-page li {break-inside:avoid;margin:0 0 14px;padding-left:4px}
.experience-page li::marker {color:var(--amber-dark)}
.experience-jumps {display:flex;gap:8px;flex-wrap:wrap;padding:18px 28px;border-top:1px solid var(--line)}
.experience-jump {display:flex;align-items:center;gap:8px;text-align:left;padding:8px 11px;border:1px solid var(--line);background:var(--canvas);color:var(--body);border-radius:7px;font-size:.73rem;line-height:1.45;min-height:40px}
.experience-jump>span:first-child {font-family:'JetBrains Mono',monospace;color:var(--amber-dark)}
.experience-jump[aria-pressed=true] {background:var(--blue);border-color:var(--blue);color:var(--white)}
.experience-jump[aria-pressed=true]>span:first-child {color:#E0B978}
.skill-tabs {display:flex;flex-wrap:wrap;gap:9px;margin-bottom:18px}
.skill-tab {display:flex;flex:1 1 190px;align-items:center;gap:10px;min-height:56px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--white);color:var(--blue);font-size:.84rem;line-height:1.4;text-align:left}
.skill-tab svg {width:20px;height:20px;flex:0 0 20px}
.skill-tab small {margin-left:auto;opacity:.8;font:400 .68rem/1.5 'JetBrains Mono',monospace}
.skill-tab:hover {border-color:var(--blue)}
.skill-tab[aria-selected=true] {background:var(--blue);color:var(--white);border-color:var(--blue);box-shadow:inset 0 -3px 0 var(--amber)}
.skill-tab[aria-selected=true] svg {color:#E0B978}
.skill-panel {background:var(--white);border:1px solid var(--line);border-radius:16px;padding:30px;margin-top:12px;animation:skill-reveal .22s ease-out}
.skill-panel-heading {display:flex;gap:17px;align-items:flex-start;margin-bottom:26px}
.skill-panel-heading h3 {font-size:1.4rem;margin-bottom:9px}
.skill-panel-heading p {font-size:.92rem;color:var(--body);margin:0;max-width:700px}
.skill-panel-icon {display:flex;align-items:center;justify-content:center;flex:0 0 48px;width:48px;height:48px;border-radius:12px;background:var(--amber-light);color:var(--amber-dark)}
.skill-panel-icon svg {width:26px;height:26px}
.skill-items {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;list-style:none;padding:0;margin:0}
.skill-items li {display:flex;align-items:center;gap:10px;min-width:0;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:var(--canvas);color:var(--blue);font-size:.86rem;line-height:1.45;overflow-wrap:anywhere}
.skill-items li::before {content:'';flex:0 0 5px;width:5px;height:5px;border-radius:50%;background:var(--amber-dark)}
.achievement-card {display:flex;flex-direction:column;overflow:hidden}
.achievement-card .card-footer {margin-top:auto;padding-top:20px;flex-wrap:wrap}
.achievement-cover {display:block;margin:-27px -27px 26px;background:var(--canvas)}
.achievement-cover img {width:100%;height:210px;object-fit:contain}
.achievement-symbol {display:flex;align-items:center;justify-content:center;width:54px;height:54px;background:var(--amber-light);color:var(--amber-dark);border-radius:14px;margin-bottom:24px}
.achievement-symbol svg {width:28px;height:28px}
.achievement-links {display:flex;gap:20px;flex-wrap:wrap;margin-bottom:28px}
@keyframes skill-reveal {from {opacity:.6;transform:translateY(5px)} to {opacity:1;transform:none}}
@media(max-width:950px) {.skill-items {grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px) {
    .about-block-heading {margin-top:40px}
    .experience-top {padding:14px 18px}
    .experience-controls button {padding:8px 10px;font-size:.78rem}
    .experience-page {padding:24px 20px}
    .experience-page ul {columns:1;font-size:.9rem}
    .experience-page-top {gap:10px}
    .experience-page-top .eyebrow {font-size:.65rem}
    .experience-number {font-size:2rem}
    .experience-jumps {padding:14px 18px;flex-wrap:nowrap;overflow-x:auto}
    .experience-jump {flex:0 0 auto;max-width:190px}
    .skill-tab {flex-basis:140px;padding:11px;font-size:.76rem;gap:8px}
    .skill-panel {padding:22px 18px}
    .skill-panel-heading {gap:12px}
    .skill-panel-heading h3 {font-size:1.2rem}
    .skill-items {grid-template-columns:1fr}
    .achievement-cover {margin:-23px -23px 24px}
}
@media(prefers-reduced-motion:reduce) {
    .experience-rail {scroll-behavior:auto;transition:none}
    .skill-panel {animation:none}
}

.speaking-card {
    display: flex;
    flex-direction: column;
}

.speaking-card .talk-icon {
    margin-bottom: 18px;
}

.talk-thumbnails {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 20px;
}

.talk-thumbnail {
    width: 116px;
    padding: 7px;
    background: var(--canvas);
    border: 1px solid var(--line);
    border-radius: 9px;
    color: var(--blue);
    text-align: center;
}

.talk-thumbnail:hover {
    border-color: var(--amber);
}

.talk-thumbnail img {
    width: 100%;
    height: 84px;
    object-fit: contain;
}

.talk-thumbnail span {
    display: block;
    margin-top: 7px;
    font-size: .7rem;
}

.talk-links {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 18px;
    margin-top: auto;
    padding-top: 20px;
}

.talk-links a {
    font-size: .82rem;
    font-weight: 600;
}

.notes-grid > .card {
    background: #E7F0F7;
    border-top: 4px solid #3B637E;
}

.notes-grid > .card:nth-child(3n + 2) {
    background: #FAECD9;
    border-top-color: #B07529;
}

.notes-grid > .card:nth-child(3n + 3) {
    background: #E7EFE8;
    border-top-color: #60806C;
}

.notes-grid > .card .tag {
    background: var(--white);
}
"""

EXTRA_JS = r"""
(() => {
  // Image viewer: used by project galleries and credential images.
  const dialog = document.getElementById('project-media-dialog');
  const body = dialog.querySelector('[data-media-body]');
  const title = dialog.querySelector('[data-media-title]');
  const openLink = dialog.querySelector('[data-media-link]');
  const expand = dialog.querySelector('[data-media-expand]');

  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-project-media="image"]');
    if (!trigger) return;
    body.replaceChildren();
    title.textContent = trigger.dataset.title;
    openLink.href = trigger.dataset.src;
    const image = document.createElement('img');
    image.alt = trigger.dataset.title;
    image.src = trigger.dataset.src;
    body.append(image);
    dialog.showModal();
  });

  dialog.querySelector('[data-media-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    body.replaceChildren();
    dialog.classList.remove('is-expanded');
    expand.textContent = 'Full screen';
    if (document.fullscreenElement === dialog) document.exitFullscreen().catch(() => {});
  });

  function updateLabels() {
    expand.textContent = document.fullscreenElement === dialog || dialog.classList.contains('is-expanded') ? 'Restore' : 'Full screen';
    document.querySelectorAll('[data-inline-workflow]').forEach(section => {
      const expanded = document.fullscreenElement === section || section.classList.contains('is-expanded');
      const button = section.querySelector('[data-inline-expand]');
      button.textContent = expanded ? 'Restore' : 'Expand';
      button.setAttribute('aria-expanded', String(expanded));
    });
  }

  expand.addEventListener('click', async () => {
    if (document.fullscreenElement === dialog) await document.exitFullscreen().catch(() => {});
    else if (dialog.classList.contains('is-expanded')) dialog.classList.remove('is-expanded');
    else {
      try { await dialog.requestFullscreen(); }
      catch { dialog.classList.add('is-expanded'); }
    }
    updateLabels();
  });

  // Workflows are visible immediately in the project page itself.
  document.addEventListener('click', async event => {
    const replay = event.target.closest('[data-inline-replay]');
    if (replay) {
      const frame = replay.closest('[data-inline-workflow]').querySelector('iframe');
      frame.src = frame.src;
      return;
    }
    const toggle = event.target.closest('[data-inline-expand]');
    if (!toggle) return;
    const section = toggle.closest('[data-inline-workflow]');
    if (document.fullscreenElement === section) await document.exitFullscreen().catch(() => {});
    else if (section.classList.contains('is-expanded')) {
      section.classList.remove('is-expanded');
      document.body.classList.remove('has-expanded-workflow');
    } else {
      try { await section.requestFullscreen(); }
      catch {
        section.classList.add('is-expanded');
        document.body.classList.add('has-expanded-workflow');
      }
    }
    updateLabels();
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    document.querySelectorAll('[data-inline-workflow].is-expanded').forEach(section => section.classList.remove('is-expanded'));
    document.body.classList.remove('has-expanded-workflow');
    updateLabels();
  });
  document.addEventListener('fullscreenchange', updateLabels);
  // A manual carousel: no auto-advance, with native swipe/scroll as a fallback.
  document.querySelectorAll('[data-experience-book]').forEach(book => {
    const rail = book.querySelector('[data-experience-rail]');
    const pages = [...book.querySelectorAll('[data-experience-page]')];
    const jumps = [...book.querySelectorAll('[data-experience-jump]')];
    const prev = book.querySelector('[data-experience-prev]');
    const next = book.querySelector('[data-experience-next]');
    const status = book.querySelector('[data-experience-status]');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let index = 0;
    function fitHeight() {
      rail.style.height = `${pages[index].getBoundingClientRect().height + rail.offsetHeight - rail.clientHeight}px`;
    }
    function update() {
      index = Math.max(0, Math.min(pages.length - 1, Math.round(rail.scrollLeft / Math.max(1, rail.clientWidth))));
      prev.disabled = index === 0;
      next.disabled = index === pages.length - 1;
      status.textContent = `${index + 1} / ${pages.length}`;
      jumps.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
      // Keep off-screen pages out of keyboard and screen-reader navigation.
      pages.forEach((page, i) => { page.inert = i !== index; });
      fitHeight();
    }
    function go(target) {
      index = Math.max(0, Math.min(pages.length - 1, target));
      rail.scrollTo({left: index * rail.clientWidth, behavior: reduceMotion.matches ? 'instant' : 'smooth'});
    }
    prev.addEventListener('click', () => go(index - 1));
    next.addEventListener('click', () => go(index + 1));
    jumps.forEach(button => button.addEventListener('click', () => go(Number(button.dataset.experienceJump))));
    book.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      go(event.key === 'Home' ? 0 : event.key === 'End' ? pages.length - 1 : index + (event.key === 'ArrowRight' ? 1 : -1));
    });
    let scheduled = false;
    rail.addEventListener('scroll', () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(() => { update(); scheduled = false; });
    }, {passive: true});
    // Retain the current chapter when the viewport changes width.
    let lastWidth = rail.clientWidth;
    new ResizeObserver(() => {
      if (rail.clientWidth === lastWidth) return;
      lastWidth = rail.clientWidth;
      rail.scrollTo({left: index * rail.clientWidth, behavior: 'instant'});
      update();
    }).observe(rail);
    const pageSizes = new ResizeObserver(fitHeight);
    pages.forEach(page => pageSizes.observe(page));
    update();
  });

  // Accessible skill tabs: click, Tab, arrow keys, Home and End.
  document.querySelectorAll('[data-skills-explorer]').forEach(explorer => {
    const tabs = [...explorer.querySelectorAll('[data-skill-tab]')];
    const panels = [...explorer.querySelectorAll('[data-skill-panel]')];
    function select(index, focus = false) {
      tabs.forEach((tab, i) => {
        tab.setAttribute('aria-selected', String(i === index));
        tab.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      });
      if (focus) tabs[index].focus({preventScroll: true});
    }
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(i));
      tab.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight') target = (i + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') target = (i + tabs.length - 1) % tabs.length;
        else if (event.key === 'Home') target = 0;
        else if (event.key === 'End') target = tabs.length - 1;
        else return;
        event.preventDefault();
        select(target, true);
      });
    });
    select(0);
  });
})();
"""


def icon(kind):
    paths = {
        'ml': '<circle cx="5" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="12" r="2"/><path d="m7 6 10 5M7 18l10-5M5 7v10"/>',
        'code': '<path d="m8 5-7 7 7 7M16 5l7 7-7 7M14 3l-4 18"/>',
        'cloud': '<path d="M7 18a5 5 0 1 1 .7-10A7 7 0 0 1 21 11a3.5 3.5 0 0 1-1 7H7Z"/>',
        'spark': '<path d="m12 3 2.8 6.2L21 12l-6.2 2.8L12 21l-2.8-6.2L3 12l6.2-2.8L12 3Z"/>',
        'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
        'award': '<path d="M8 3h8v6a4 4 0 0 1-8 0V3ZM8 5H4v2a4 4 0 0 0 4 4M16 5h4v2a4 4 0 0 1-4 4M12 13v6M8 21h8M9 19h6"/>',
        'work': '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v3h4v-3"/>',
        'writing': '<path d="m16 3 5 5-12 12-6 1 1-6L16 3ZM13 6l5 5"/>',
        'notes': '<path d="M14 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-9M14 3v7h7L14 3ZM7 14h10M7 17h7"/>',
        'stage': '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/>',
        'credential': '<circle cx="12" cy="8" r="5"/><path d="m8 12-2 9 6-3 6 3-2-9"/>',
        'connect': '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5Z"/>',
        'gateway': '<circle cx="5" cy="12" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="M7 12h5M12 12V5h5M12 12v7h5"/>',
        'people': '<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6M18 15a5 5 0 0 1 3 4v2"/>'
    }
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'+paths.get(kind,paths['work'])+'</svg>'


def section_label(label, kind):
    return f'<div class="eyebrow section-label"><span class="section-icon">{icon(kind)}</span><span>{e(label)}</span></div>'


# Credential images: images/credentials/<filename below>.<extension>
# Supports PNG, JPG, JPEG, WEBP, AVIF, GIF and SVG.
# Labels/issuers/verification URLs are in content/profile.json, certifications.
# Optional image, full_image and image_label fields are supported there too.
CREDENTIAL_FILES = {
    "Google Certified Generative AI Leader": "google-genai-leader",
    "Azure Data Scientist": "azure-data-scientist",
    "Azure AI Engineer": "azure-ai-engineer",
    "IBM Advanced Data Science": "ibm-advanced-data-science",
    "IBM Data Science Professional": "ibm-data-science",
    "IBM Applied AI": "ibm-applied-ai",
    "TensorFlow Developer": "tensorflow-developer",
    "MLOps Specialization": "mlops-specialization",
    "ML Engineer with Azure": "azure-ml-engineer",
    "Maths for Machine Learning": "maths-for-ml",
    "Scrum Fundamentals": "scrum-fundamentals",
    "Python Programming Track": "python-programming",
}

def local_image(path):
    return path if path and (ROOT / path).is_file() else None

def credential_media(x):
    stem = CREDENTIAL_FILES.get(x["title"])
    folder = ROOT / "images" / "credentials"
    preview = None
    if stem and folder.is_dir():
        matches = sorted(
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.stem.lower() == stem.lower()
            and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"}
        )
        if matches:
            preview = matches[0].relative_to(ROOT).as_posix()
    # Keep existing credential images working until replacements are added.
    preview = preview or local_image(x.get("image"))
    full = local_image(x.get("full_image")) or preview
    return preview, full


def credential_card(x):
    preview, full = credential_media(x)
    image_label = x.get("image_label") or x["title"]
    if preview:
        content = (
            f'<img src="{e(asset_url(preview))}" alt="{e(image_label)}" loading="lazy" width="104" height="80">'
            "<span>View full image →</span>"
        )
        visual = media_button("image", full, image_label, content, "credential-image-button")
    else:
        visual = f'<span class="credential-symbol">{icon("credential")}</span>'
    label = "View credentials →" if "/users/" in x.get("url", "") else "View credential →"
    link = (
        f'<a href="{e(x["url"])}">{label}</a>'
        if x.get("url") and x.get("status") != "In Progress"
        else ""
    )
    status = "<p>In progress</p>" if x.get("status") == "In Progress" else ""
    return f"""<article class="credential"><div class="credential-media {'has-image' if preview else ''}">{visual}</div>
      <div><h3>{e(x['title'])}</h3><p>{e(x['issuer'])}</p>{status}{link}</div></article>"""


def asset_url(path):
    return url(quote(path, safe='/'))


def project_images(p):
    folder = ROOT / 'images' / 'projects' / p['slug']
    extensions = {'.png','.jpg','.jpeg','.webp','.avif','.gif','.svg'}
    images = sorted((x for x in folder.iterdir() if x.is_file() and x.suffix.lower() in extensions),
                    key=lambda x: (x.stem.lower()!='cover',x.name.lower())) if folder.is_dir() else []
    # Prefer the new project folder; otherwise reuse any existing legacy files.
    if not images:
        images = [ROOT/x for x in p['legacy'] if (ROOT/x).is_file()]
    return [x.relative_to(ROOT).as_posix() for x in images]


def workflow_path(p):
    path = 'assets/workflows/'+p['slug']+'/index.html'
    return path if p['workflow'] and (ROOT/path).is_file() else None


def project_path(p):
    return '/work/'+p['slug']+'/'


def project_card(p, filterable=False):
    images = project_images(p)
    visual = f'<img src="{e(asset_url(images[0]))}" alt="{e(p["title"])} preview" loading="lazy">' if images else icon('gateway' if p['workflow'] else 'work')
    search = ' '.join([p['title'],p['description'],p['category'],*p['tags']]).lower()
    attrs = f'data-content-card data-search="{e(search)}" data-tags="{e(json.dumps([p["category"]]))}"' if filterable else ''
    summary = p['description'] if len(p['description'])<=195 else p['description'][:192].rsplit(' ',1)[0]+'…'
    return f'''<article class="card project-card" {attrs}>
      <div class="project-media {'has-image' if images else ''}">{visual}<span class="project-banner">{e(p['banner'])}</span></div>
      <div class="meta project-category">{e(p['category'])}</div>
      <h3><a href="{e(url(project_path(p)))}">{e(p['title'])}</a></h3>
      <p>{e(summary)}</p>{tags(p['tags'][:5])}
      <div class="card-footer">{a(project_path(p),'Explore project →')}</div></article>'''


def project_filters(entries):
    options = ''.join(f'<option value="{e(c)}">{e(c)}</option>' for c in sorted({p['category'] for p in entries}))
    return f'''<div class="search-tools"><label>Search<input type="search" data-search placeholder="Search projects, skills, or topics"></label>
      <label>Category<select data-topic><option value="">All categories</option>{options}</select></label>
      <span class="count" data-count aria-live="polite">{len(entries)} entries</span></div>'''


def media_button(kind, path, title, label, cls='button'):
    return f'<button class="{cls}" type="button" data-project-media="{kind}" data-src="{e(asset_url(path))}" data-title="{e(title)}">{label}</button>'


def media_dialog():
    return """<dialog class="media-dialog" id="project-media-dialog" aria-labelledby="project-media-title">
      <div class="media-toolbar"><h2 id="project-media-title" data-media-title>Project preview</h2><div class="media-actions">
      <button type="button" data-media-expand>Full screen</button>
      <a data-media-link target="_blank" rel="noopener">Open separately →</a><button type="button" data-media-close>Close</button></div></div>
      <div class="media-body" data-media-body></div></dialog>"""


def build_project_page(p):
    images = project_images(p)
    workflow = workflow_path(p)
    body = f"""<div class="container"><header class="article-header"><div class="breadcrumbs">{a('/work/', '← All work', '')}</div>
      {section_label(p['banner'], 'gateway' if p['workflow'] else 'work')}<h1>{e(p['title'])}</h1>
      <div class="meta">{e(p['category'])}</div>{tags(p['tags'])}</header>
      <section class="project-detail"><h2>Overview</h2><p class="lead">{e(p['description'])}</p></section>"""
    if workflow:
        body += f"""<section class="workflow-embed" aria-labelledby="workflow-heading" data-inline-workflow>
          <div class="workflow-toolbar"><h2 id="workflow-heading">Workflow &amp; architecture</h2>
          <div class="workflow-controls"><button type="button" data-inline-replay>Replay</button>
          <button type="button" data-inline-expand aria-expanded="false">Expand</button>
          <a href="{e(asset_url(workflow))}" target="_blank" rel="noopener">Open separately →</a></div></div>
          <iframe src="{e(asset_url(workflow))}" title="{e(p['title'])} — interactive workflow" loading="eager" allowfullscreen></iframe>
          </section>"""
    body += '<section class="project-detail page-tail">'
    if p["slug"] == "social-media-generator":
        body += "<h2>Memory that connects the dots</h2><p>Connects external sources and the team’s publishing history over time, giving agents a reusable memory of relevant information, relationships, and past content.</p>"
    if images:
        body += '<h2>Project gallery</h2><div class="project-gallery">'
        for i, path in enumerate(images, 1):
            label = f'{p["title"]} - image {i}'
            content = f'<img src="{e(asset_url(path))}" alt="{e(label)}" loading="lazy"><span>Expand image {i} →</span>'
            body += media_button("image", path, label, content, "gallery-item")
        body += "</div>"
    body += f'<div class="actions">{a("/work/", "← Back to all work")}</div></section></div>'
    write_page(project_path(p), p["title"], p["description"], body, "Work")


def leadership_cards():
    return ''.join(f'<article class="card leadership-card"><span class="section-icon">{icon(kind)}</span><div class="meta">{e(role)}</div><h3>{e(title)}</h3><p>{e(description)}</p>{tags(skills)}</article>'
                   for kind,title,role,description,skills in LEADERSHIP)

# About-page presentation. Keep editing your original experience/skills in
# content/profile.json; these additions are merged without replacing them.
SKILL_CATEGORIES = {
    'architecture': (
        'Applied AI & Architecture', 'gateway', 'Designing AI solutions, agentic workflows, and responsible enterprise systems.'),
    'engineering': (
        'Engineering & Integration', 'code','Building production systems and connecting AI to enterprise data and processes.'),
    'platforms': (
        'Cloud & AI Platforms', 'cloud','Platforms and tools for developing, deploying, and operating AI solutions.'),
    'ml': (
        'Data Science & ML', 'ml','Modeling, experimentation, forecasting, and explainable machine learning.'),
    'leadership': (
        'Leadership & Enablement', 'people', 'Technical advisory, product direction, communication, and AI enablement.'
    ),
}

# Retain the additional skills requested earlier.
SKILL_ADDITIONS = {
    'architecture': ['Agentic Harnesses','Agentic Architecture',],
    'leadership': ['Agile','Scrum','Community Leadership','AI Training & Enablement',],
}

# Achievement images: images/achievements/<slug>/cover.png, 02.png, 03.png, ...
# JPG/JPEG/WEBP/AVIF/GIF/SVG work too. The whole folder becomes a gallery.
# Optional profile fields: slug, images: [{path, caption}], or a single image.
ACHIEVEMENT_SLUGS = {
    'BaselHack 2024 Winner': 'baselhack-2024',
    'BaselHack 2025 Runner-Up': 'baselhack-2025',
    'Coursera Instructor': 'coursera-instructor',
    'Invited Speaker': 'invited-speaker',
}


def experience_book(entries):
    if not entries:
        return ''
    pages = []
    jumps = []
    for i, entry in enumerate(entries):
        title, company = entry['title'], entry['company']
        bullets = ''.join(f'<li>{e(item)}</li>' for item in entry.get('items', []))
        pages.append(f'''<article class="experience-page" id="experience-page-{i + 1}"
          data-experience-page role="group" aria-roledescription="slide" aria-label="{i + 1} of {len(entries)}">
          <div class="experience-page-top"><span class="section-icon">{icon('work')}</span>
          <div class="eyebrow">{e(entry['date'])}</div><span class="experience-number" aria-hidden="true">{i + 1:02d}</span></div>
          <h3>{e(title)}</h3><p class="experience-company">{e(company)}</p><ul>{bullets}</ul></article>''')
        jumps.append(f'''<button type="button" class="experience-jump" data-experience-jump="{i}"
          aria-controls="experience-page-{i + 1}" aria-label="Show {e(title)} at {e(company)}"
          aria-pressed="{'true' if i == 0 else 'false'}"><span aria-hidden="true">{i + 1:02d}</span><span>{e(company)}</span></button>''')
    return f'''<div class="experience-book" data-experience-book role="region"
      aria-roledescription="carousel" aria-label="Experience and education">
      <div class="experience-top"><p class="experience-status" data-experience-status aria-live="polite" aria-atomic="true">1 / {len(entries)}</p>
      <div class="experience-controls"><button type="button" data-experience-prev aria-label="Previous experience" disabled>← Previous</button>
      <button type="button" data-experience-next aria-label="Next experience">Next →</button></div></div>
      <div class="experience-rail" data-experience-rail tabindex="0" aria-label="Experience pages; use left and right arrow keys">{''.join(pages)}</div>
      <div class="experience-jumps" aria-label="Jump to an experience">{''.join(jumps)}</div></div>'''


def skills_explorer():
    groups = []
    for entry in PROFILE.get('skills', []):
        groups.append({**entry, 'items': list(entry.get('items', []))})
    for category, additions in SKILL_ADDITIONS.items():
        group = next((x for x in groups if x['category'] == category), None)
        if group is None:
            group = {'category': category, 'items': []}
            groups.append(group)
        existing = {item.casefold() for item in group['items']}
        for item in additions:
            if item.casefold() not in existing:
                group['items'].append(item)
                existing.add(item.casefold())
    if not groups:
        return ''
    tabs, panels = [], []
    for i, group in enumerate(groups):
        category = group['category']
        default = (category.replace('-', ' ').replace('_', ' ').title(), 'work', '')
        label, symbol, description = SKILL_CATEGORIES.get(category, default)
        label = group.get('label') or label
        description = group.get('description') or description
        tabs.append(f'''<button type="button" class="skill-tab" id="skill-tab-{i}" role="tab"
          data-skill-tab aria-controls="skill-panel-{i}" aria-selected="{'true' if i == 0 else 'false'}"
          tabindex="{0 if i == 0 else -1}">{icon(symbol)}<span>{e(label)}</span><small>{len(group['items'])}</small></button>''')
        items = ''.join(f'<li>{e(item)}</li>' for item in group['items'])
        panels.append(f'''<section class="skill-panel" id="skill-panel-{i}" role="tabpanel"
          data-skill-panel aria-labelledby="skill-tab-{i}" tabindex="0">
          <div class="skill-panel-heading"><span class="skill-panel-icon">{icon(symbol)}</span>
          <div><h3>{e(label)}</h3><p>{e(description)}</p></div></div><ul class="skill-items">{items}</ul></section>''')
    return f'''<div class="skills-explorer" data-skills-explorer><div class="skill-tabs" role="tablist"
      aria-label="Skill categories">{''.join(tabs)}</div><div class="skill-panels">{''.join(panels)}</div></div>'''


def achievement_entries():
    # Remove the old publication card while retaining other user-supplied entries.
    entries = [dict(x) for x in PROFILE.get('achievements', [])
               if not ('ieee' in x['title'].casefold() and 'publication' in x['title'].casefold())]
    if not any('basel' in x['title'].casefold() and '2025' in x['title'] and 'runner' in x['title'].casefold() for x in entries):
        winner_index = next((i for i, x in enumerate(entries) if 'basel' in x['title'].casefold() and '2024' in x['title']), -1)
        entries.insert(winner_index + 1, {
            'title': 'BaselHack 2025 Runner-Up',
            'description': 'Runner-up at BaselHack 2025.',
            'links': [],
        })
    used = set()
    for entry in entries:
        slug = entry.get('slug') or ACHIEVEMENT_SLUGS.get(entry['title'])
        slug = slug or re.sub(r'[^a-z0-9]+', '-', entry['title'].casefold()).strip('-')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in used:
            raise ValueError(f'Use a unique lowercase achievement slug for {entry["title"]}')
        used.add(slug)
        entry['slug'] = slug
    return entries


def achievement_images(entry):
    extensions = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg'}
    folder = ROOT / 'images' / 'achievements' / entry['slug']
    paths = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in extensions),
                   key=lambda p: (p.stem.casefold() != 'cover', p.name.casefold())) if folder.is_dir() else []
    # Explicit captions/order take precedence; include other discovered images too.
    entries = [{'path': item} if isinstance(item, str) else dict(item) for item in entry.get('images', [])]
    entries += [{'path': p.relative_to(ROOT).as_posix()} for p in paths]
    if entry.get('image'):
        entries.insert(0, {'path': entry['image']})
    images, seen = [], set()
    for image in entries:
        path = local_image(image.get('path'))
        if path and path not in seen:
            seen.add(path)
            image['path'] = path
            image['caption'] = image.get('caption') or f'{entry["title"]} — image {len(images) + 1}'
            images.append(image)
    return images


def achievement_path(entry):
    return '/about/achievements/' + entry['slug'] + '/'


def achievement_card(entry):
    path = achievement_path(entry)
    images = achievement_images(entry)

    symbols = {
        'baselhack-2024': 'award',          # Trophy
        'baselhack-2025': 'credential',     # Medal
        'coursera-instructor': 'people',   # Teaching / people
        'invited-speaker': 'stage',        # Microphone
    }

    symbol = symbols.get(entry['slug'], 'award')
    visual = (
        f'<span class="achievement-symbol">'
        f'{icon(symbol)}</span>'
    )

    count = (
        f'<span class="meta">{len(images)} '
        f'{"image" if len(images) == 1 else "images"}</span>'
        if images else ''
    )

    return f'''<article class="card achievement-card">
      {visual}
      <h3><a href="{e(url(path))}">{e(entry['title'])}</a></h3>
      <p>{e(entry['description'])}</p>
      <div class="card-footer">
        {a(path, 'Explore achievement →')}{count}
      </div>
    </article>'''


def build_achievement_page(entry):
    images = achievement_images(entry)
    body = f'''<div class="container"><header class="article-header"><div class="breadcrumbs">{a('/about/#achievements', '← All achievements', '')}</div>
      {section_label('Highlights', 'award')}<h1>{e(entry['title'])}</h1><p class="lead">{e(entry['description'])}</p></header>
      <section class="project-detail page-tail" aria-label="Achievement details">'''
    if entry.get('links'):
        body += '<div class="achievement-links">' + ''.join(f'<a class="text-link" href="{e(link["url"])}">{e(link["label"])} →</a>' for link in entry['links']) + '</div>'
    if images:
        body += '<h2>Moments &amp; highlights</h2><div class="project-gallery achievement-gallery">'
        for image in images:
            content = f'<img src="{e(asset_url(image["path"]))}" alt="{e(image["caption"])}" loading="lazy"><span>{e(image["caption"])} · Expand →</span>'
            body += media_button('image', image['path'], image['caption'], content, 'gallery-item')
        body += '</div>'
    body += f'<div class="actions">{a("/about/#achievements", "← Back to achievements")}</div></section></div>'
    write_page(achievement_path(entry), entry['title'], entry['description'], body, 'About')



def footer():
    return f'''<footer class="site-footer" id="contact"><div class="container">
      <div class="footer-top"><div>{section_label('Connect', 'connect')}<h2>Let's talk.</h2>
      <p>Have a project in mind? Get in touch for collaboration, enterprise AI consultation and training, or speaking engagements.</p></div>
      <a class="button" href="{e(CONFIG['linkedin'])}">Get in touch <span aria-hidden="true">→</span></a></div>
      <div class="footer-links"><a href="{e(CONFIG['linkedin'])}">LinkedIn →</a><a href="{e(CONFIG['github'])}">GitHub →</a><a href="{e(CONFIG['medium'])}">Medium →</a>{a('/feed.xml','RSS feed','')}</div>
      <div class="footer-bottom"><span>© {date.today().year} {e(CONFIG['name'])}</span><span>Applied AI Scientist</span></div></div></footer>'''

def layout(title, description, body, path, active, article=False):
    nav = ''.join(f'<a href="{e(url(p))}"'+(' aria-current="page"' if label == active else '')+f'>{label}</a>' for label,p in NAV)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · {e(CONFIG['name'])}</title><meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(absolute(path))}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:url" content="{e(absolute(path))}">
<meta name="theme-color" content="#F3F6F5"><link rel="icon" type="image/svg+xml" href="{e(url('/assets/favicon.svg'))}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700;750&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{e(url('/assets/css/main.css'))}"><link rel="alternate" type="application/rss+xml" title="{e(CONFIG['name'])} - Writing & Notes" href="{e(url('/feed.xml'))}"><style>{EXTRA_CSS}</style><script defer src="{e(url('/assets/js/main.js'))}"></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner">
<a class="brand" href="{e(url('/'))}">Muhammad Saad<span>.</span></a><button class="menu-toggle" data-menu-toggle aria-controls="navigation" aria-expanded="false" type="button">Menu</button><nav class="nav-links" id="navigation" aria-label="Main navigation" data-navigation>{nav}</nav></div></header>
<main id="main">{body}</main>{footer()}{media_dialog()}<script>{EXTRA_JS}</script></body></html>'''

def write_page(path, title, description, body, active, article=False):
    dest = OUT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(layout(title,description,body,path,active,article), encoding='utf-8')
    PAGES.append(path)

def intro(kicker, title, description):
    return f'<div class="container"><header class="page-intro">{section_label(kicker, "work")}<h1>{title}</h1><p class="lead">{description}</p></header></div>'

def load_content(kind, drafts=False):
    entries=[]
    for path in sorted((ROOT / 'content' / kind).glob('*.md')):
        raw=path.read_text(encoding='utf-8-sig')
        if not raw.startswith('---\n'): raise ValueError(f'{path}: expected YAML front matter')
        _,header,body=raw.split('---',2)
        data=yaml.safe_load(header)
        for key in ['title','date','slug','description']:
            if not data.get(key): raise ValueError(f'{path}: missing {key}')
        if not isinstance(data.get('draft',False),bool): raise ValueError(f'{path}: draft must be true or false')
        data['draft']=data.get('draft',False)
        if data['draft'] and not drafts: continue
        data['date']=date.fromisoformat(str(data['date']))
        if data['date']>date.today() and not drafts: continue
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',data['slug']): raise ValueError(f'{path}: use a lowercase hyphenated slug')
        data['tags']=data.get('tags',[])
        if not isinstance(data['tags'],list): raise ValueError(f'{path}: tags must be a list')
        data['kind']=kind
        data['path']=('/writing/' if kind=='articles' else '/notes/')+data['slug']+'/'
        data['href']=data.get('external_url') or url(data['path'])
        if data.get('external_url') and not data['external_url'].startswith('https://'): raise ValueError(f'{path}: external_url must use HTTPS')
        md=markdown.Markdown(extensions=['fenced_code','tables','toc','attr_list'])
        data['html']=md.convert(body.strip())
        if not data.get('external_url') and not body.strip(): raise ValueError(f'{path}: add content before publishing')
        # Keep Markdown asset URLs valid when a project repository uses base_path.
        if BASE: data['html']=re.sub(r'(src|href)="/(?!/)',lambda m:m.group(1)+'="'+BASE+'/',data['html'])
        data['toc']=md.toc
        data['words']=len(re.findall(r'\w+',body))
        entries.append(data)
    if len({x['slug'] for x in entries})!=len(entries): raise ValueError(f'Duplicate {kind} slug')
    return sorted(entries,key=lambda x:x['date'],reverse=True)

def entry_card(x, row=False):
    source=x.get('source','Article' if x['kind']=='articles' else 'Note')
    arrow='→'
    metadata=f'{nice_date(x["date"])} · {e(source)}'
    search=e(' '.join([x['title'],x['description'],*x['tags']]).lower())
    attrs=f'data-content-card data-search="{search}" data-tags="{e(json.dumps(x["tags"]))}"'
    if row:
        return f'<article class="article-row" {attrs}><div class="meta">{metadata}</div><div><h3><a href="{e(x["href"])}">{e(x["title"])}</a></h3><p>{e(x["description"])}</p>{tags(x["tags"])}</div><a class="row-arrow" href="{e(x["href"])}" aria-label="Read {e(x["title"])}">{arrow}</a></article>'
    return f'<article class="card" {attrs}><div class="meta">{metadata}</div><h3><a href="{e(x["href"])}">{e(x["title"])}</a></h3><p>{e(x["description"])}</p>{tags(x["tags"])}<div class="card-footer"><a class="text-link" href="{e(x["href"])}">Read {"on Medium" if x.get("external_url") else "more"} {arrow}</a></div></article>'

def filters(entries):
    topics=sorted({tag for x in entries for tag in x['tags']})
    options=''.join(f'<option value="{e(t)}">{e(t)}</option>' for t in topics)
    return f'<div class="search-tools"><label>Search<input type="search" data-search placeholder="Search titles, topics, and summaries"></label><label>Topic<select data-topic><option value="">All topics</option>{options}</select></label><span class="count" data-count aria-live="polite">{len(entries)} entries</span></div>'

def speaking_card(t):
    thumbnails = []

    for i, item in enumerate(t.get('images', [])[:3], 1):
        image = {'path': item} if isinstance(item, str) else item
        path = local_image(image.get('path'))
        if not path:
            continue

        caption = image.get('caption') or f'{t["title"]} — photo {i}'
        content = (
            f'<img src="{e(asset_url(path))}" '
            f'alt="{e(caption)}" loading="lazy">'
            '<span>Expand photo →</span>'
        )
        thumbnails.append(
            media_button(
                'image', path, caption, content, 'talk-thumbnail'
            )
        )

    photos = (
        '<div class="talk-thumbnails">'
        + ''.join(thumbnails)
        + '</div>'
        if thumbnails else ''
    )

    links = ''.join(
        f'<a href="{e(link["url"])}" target="_blank" '
        f'rel="noopener noreferrer">{e(link["label"])} ↗</a>'
        for link in t.get('links', [])
        if link.get('url')
    )
    resources = f'<div class="talk-links">{links}</div>' if links else ''

    return f'''<article class="card speaking-card">
      <span class="talk-icon">{icon('stage')}</span>
      <div class="eyebrow">{e(t['type'])}</div>
      <h3>{e(t['title'])}</h3>
      <p>{e(t['topic'])}</p>
      <div class="meta">{e(t.get('location', ''))}</div>
      {photos}
      {resources}
    </article>'''

def build(drafts=False):
    PAGES.clear()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    for folder in ['assets','images','pdf']:
        if (ROOT/folder).exists(): shutil.copytree(ROOT/folder,OUT/folder)
    (OUT/'.nojekyll').write_text('', encoding='utf-8')
    articles=load_content('articles',drafts)
    notes=load_content('notes',drafts)
    featured = [next(p for p in PROJECTS if p['number']==number) for number in FEATURED]
    remaining = [p for p in PROJECTS if p['number'] not in FEATURED]
    latest_articles = ''.join(entry_card(x) for x in articles[:4]) or '<p>Articles are on their way.</p>'
    latest_notes = ''.join(entry_card(x) for x in notes[:1]) if notes else f'<div class="info-panel"><h3>More conversations on LinkedIn</h3><p>Follow my latest posts and join the discussion.</p><a href="{e(CONFIG["linkedin"])}">Find me on LinkedIn →</a></div>'
    featured_talks = ''.join(f'<article class="info-panel featured-talk"><span class="talk-icon">{icon("stage")}</span><div class="meta">{e(t["type"])}</div><h3>{e(t["title"])}</h3><p>{e(t["topic"])}</p><div class="meta">{e(t["location"])}</div>{a("/speaking/","Explore the talks →")}</article>' for t in PROFILE['speaking'][:2])
    home = f'''<section class="hero"><div class="container"><div class="hero-grid"><div>
      <div class="eyebrow">Applied AI Scientist · Endress+Hauser</div><h1>Building AI. Sharing what I learn.</h1>
      {''.join(f'<p class="intro">{e(p)}</p>' for p in BIO)}<div class="actions">{a('/work/','Explore my work →','button')}{a('/writing/','Read my writing')}</div></div>
      <figure class="portrait"><img src="{e(url('/images/saad.PNG'))}" alt="Muhammad Saad Uddin" width="371" height="376"><figcaption><strong>Applied AI Scientist</strong><span>Germany</span></figcaption></figure></div>
      <div class="intro-bar"><span>Enterprise AI &amp; Agentic Workflows</span><span>AI Safety</span><span>Speaker &amp; Trainer</span><span>Explainable AI</span><span>Writer &amp; Poet</span></div></div></section>
      <section class="section home-credentials"><div class="container"><div class="section-heading"><div>{section_label('Credentials','credential')}<h2>A foundation for the work.</h2></div>{a('/about/#credentials','All credentials →')}</div><div class="credentials">{''.join(credential_card(x) for x in PROFILE['certifications'][:3])}</div></div></section>
      <section class="section"><div class="container"><div class="section-heading"><div>{section_label('In practice','work')}<h2>Selected work</h2></div>{a('/work/','All projects →')}</div>
      <div class="cards two">{''.join(project_card(p) for p in featured)}</div></div></section>
      <section class="section soft"><div class="container"><div class="section-heading"><div>{section_label('Writing','writing')}<h2>Ideas in depth</h2></div>{a('/writing/','All articles →')}</div><div class="cards two">{latest_articles}</div></div></section>
      <section class="section"><div class="container split"><div>{section_label('Notes','notes')}<h2>Short thoughts.<br>Room to explore.</h2><p>Observations, questions, and practical lessons about AI and engineering.</p>{a('/notes/','Browse notes →')}</div><div>{latest_notes}</div></div></section>
      <section class="section soft"><div class="container"><div class="section-heading"><div>{section_label('On stage','stage')}<h2>Sharing experience,<br>starting conversations.</h2></div>{a('/speaking/','All talks & workshops →')}</div><p class="stage-intro">Talks and training on enterprise AI, explainability, and multi-agent workflows.</p><div class="cards two">{featured_talks}</div></div></section>'''
    write_page('/','Applied AI, writing & ideas','Enterprise AI, explainability, multi-agent workflows, writing, and training by Muhammad Saad Uddin.',home,'Home')

    work = intro('Work','Architecting intelligence, end to end.<span class="work-tagline">Models that learn. Agents that act. Systems that deliver.</span>',
                 'Hands-on work across machine learning, data science, and agentic AI. Each project was built to move from experimentation to real impact.')
    work += f'''<section class="section"><div class="container"><div class="section-heading"><div>{section_label('Enterprise AI in practice','gateway')}<h2>Featured projects</h2></div></div><div class="cards two">{''.join(project_card(p) for p in featured)}</div></div></section>
      <section class="section soft" id="projects"><div class="container"><div class="section-heading"><div>{section_label('Explore the collection','work')}<h2>More projects</h2></div></div>
      {project_filters(remaining)}<div class="cards">{''.join(project_card(p,True) for p in remaining)}</div><p class="no-results" data-no-results hidden>No matching projects. Try another search or category.</p></div></section>
'''
    write_page('/work/','Work','Enterprise AI projects, machine learning, data science, and applied AI applications.',work,'Work')

    platforms = intro(
        'Platforms & enablement',
        'Helping people put AI to work.',
        'Shared model access, community leadership, practical training, '
        'and enterprise AI architecture.'
    )
    platforms += f'''<section class="section"><div class="container">
      <div class="cards two">{leadership_cards()}</div>
      </div></section>'''
    write_page(
        '/platforms/',
        'Platforms, Community & Training',
        'LLM Gateway process and community ownership, E+H AI Community '
        'leadership, AI training, and enterprise AI architecture.',
        platforms,
        'Platforms'
    )
    for p in PROJECTS:
        build_project_page(p)

    for kind,title,lead,entries in [('articles','Writing','Longer explorations of AI systems, agent safety, and the engineering decisions that matter.',articles),('notes','Notes','Short observations, ideas in progress, and lessons from working with AI.',notes)]:
        path='/writing/' if kind=='articles' else '/notes/'
        content=intro('Ideas & experience',title,lead)+'<section class="section"><div class="container">'
        if entries:
            is_notes = kind == 'notes'
            layout_class = 'cards notes-grid' if is_notes else 'article-list'

            content += filters(entries)
            content += f'<div class="{layout_class}">'
            content += ''.join(entry_card(x, row=not is_notes) for x in entries)
            content += '</div>'
            content += (
                '<p class="no-results" data-no-results hidden>'
                'No matching entries. Try another search or topic.</p>'
            )
        else:
            empty_title = 'Articles are on their way.' if kind == 'articles' else 'Notes are on their way.'
            content+=f'<div class="empty-state"><h2>{empty_title}</h2><p>For now, you can find my shorter posts and conversations on LinkedIn.</p><a class="text-link" href="{e(CONFIG["linkedin"])}">Read my LinkedIn posts →</a></div>'
        content+='</div></section>'
        write_page(path,title,lead,content,title)
        for x in entries:
            if x.get('external_url'): continue
            draft='<div class="draft-label">Draft preview</div>' if x['draft'] else ''
            original=f'<p><a href="{e(x["source_url"])}">Join the original discussion →</a></p>' if x.get('source_url') else ''
            article=f'<div class="container"><header class="article-header"><div class="breadcrumbs">{a(path,"← "+title,"")}</div>{draft}<div class="meta">{nice_date(x["date"])} · {max(1,round(x["words"]/220))} min read</div><h1>{e(x["title"])}</h1><p class="lead">{e(x["description"])}</p>{tags(x["tags"])}</header><div class="article-layout"><article class="prose">{x["html"]}{original}</article><aside class="toc-panel" aria-label="Table of contents"><strong>On this page</strong>{x["toc"]}</aside></div></div>'
            write_page(x['path'],x['title'],x['description'],article,title,True)

    speaking=intro('Speaking & workshops','Ideas worth discussing.','Talks on practical LLM applications, enterprise AI, and human oversight in agentic workflows.')+'<section class="section"><div class="container"><div class="cards two">'
    speaking += ''.join(speaking_card(x) for x in PROFILE['speaking'])
    speaking+='</div></div></section>'
    write_page('/speaking/','Speaking','Conference talks, workshops, and speaking engagements.',speaking,'Speaking')

    about=intro('About','A little about me.','Applied AI Scientist, writer, speaker, and trainer.')+'<section class="section"><div class="container"><div class="split page-tail"><div>'+''.join(f'<p>{e(p)}</p>' for p in (PROFILE['about'] or BIO))+f'<div class="actions"><a class="button" href="{e(url("/pdf/Muhammad%27s_Resume.pdf"))}">Download résumé ↓</a></div></div><div class="info-panel"><h3>Based in Germany</h3><p>English — C1<br>Deutsch — B2</p><h3>Find me online</h3><a href="{e(CONFIG["linkedin"])}">LinkedIn →</a><a href="{e(CONFIG["github"])}">GitHub →</a><a href="{e(CONFIG["medium"])}">Medium →</a></div></div>'
    about += '<div class="section-heading" id="experience"><div>' + section_label('Journey', 'work') + '<h2>Experience &amp; education</h2></div></div>'
    about += experience_book(PROFILE['experience'])
    about += '<div class="section-heading about-block-heading" id="skills"><div>' + section_label('Capabilities', 'spark') + '<h2>Skills &amp; expertise</h2></div></div>'
    about += skills_explorer()
    about += '</div></section><section class="section soft"><div class="container"><div class="section-heading" id="achievements"><div>' + section_label('Milestones', 'award') + '<h2>Achievements</h2></div></div><div class="cards two">'
    achievements = achievement_entries()
    about += ''.join(achievement_card(entry) for entry in achievements)
    about += '</div></div></section><section class="section"><div class="container"><div class="section-heading" id="credentials"><h2>Credentials</h2></div><div class="credentials">'
    about += ''.join(credential_card(x) for x in PROFILE['certifications'])
    about += '</div></div></section>'
    for entry in achievements:
        build_achievement_page(entry)
    write_page('/about/','About','Experience, skills, speaking, and credentials of Muhammad Saad Uddin.',about,'About')

    notfound=intro('404','This page wandered off.','You can find the latest work, articles, and notes from the homepage.')+f'<div class="container page-tail">{a("/","Back to home →","button")}</div>'
    (OUT/'404.html').write_text(layout('Page not found','Page not found.',notfound,'/404.html',''), encoding='utf-8')
    sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for path in PAGES: ET.SubElement(ET.SubElement(sitemap,'url'),'loc').text=absolute(path)
    ET.ElementTree(sitemap).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+absolute('/sitemap.xml')+'\n', encoding='utf-8')
    rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
    for key,val in [('title',CONFIG['name']+' - Writing & Notes'),('link',absolute('/')),('description','Articles and short thoughts on applied AI.')]: ET.SubElement(channel,key).text=val
    for x in sorted(articles+notes,key=lambda x:x['date'],reverse=True):
        if x['draft']:continue
        item=ET.SubElement(channel,'item')
        for key,val in [('title',x['title']),('link',x.get('external_url') or absolute(x['path'])),('guid',x.get('external_url') or absolute(x['path'])),('description',x['description']),('pubDate',datetime.combine(x['date'],datetime.min.time(),timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))]: ET.SubElement(item,key).text=val
    ET.ElementTree(rss).write(OUT/'feed.xml',encoding='utf-8',xml_declaration=True)
    print(f'Built {len(PAGES)} pages, {len(articles)} articles, {len(notes)} notes → {OUT}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--drafts',action='store_true');args=parser.parse_args();build(args.drafts)
