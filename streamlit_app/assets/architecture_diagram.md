# FreeMobilaChat - Architecture Complète

## Diagramme d'Architecture du Système

```mermaid
graph TB
    subgraph "1. CAPTURE DES DONNÉES"
        A[Twitter/X API] -->|Streaming tweets @Free| B[Tweet Collector]
        B -->|Stockage brut| C[(Base de Données<br/>Tweets Bruts)]
    end
    
    subgraph "2. SYSTÈME DE CLASSIFICATION - DÉVELOPPÉ"
        C -->|Extraction| D[Nettoyage & Preprocessing]
        D -->|Tweets nettoyés| E[Classification Engine]
        
        E -->|Multi-modèles| E1[BERT Classifier]
        E -->|Multi-modèles| E2[Mistral LLM]
        E -->|Multi-modèles| E3[Rule-Based Classifier]
        
        E1 & E2 & E3 -->|Résultats| F[Agrégateur de Scores]
        F -->|Classification finale| G{Est une<br/>Réclamation?}
    end
    
    subgraph "3. GÉNÉRATION DE RÉPONSES"
        G -->|OUI| H[Générateur de Réponse]
        H -->|LLM| I[Template Personnalisé]
        I -->|Contient lien| J[Publication Commentaire<br/>avec Lien Chatbot]
        J -->|API Twitter| A
    end
    
    subgraph "4. CHATBOT CONVERSATIONNEL - À DÉVELOPPER"
        J -->|Client clique| K[Interface Chatbot Web]
        K -->|Dialogue| L[Chatbot Engine]
        
        L -->|Demande info| M{Infos complètes?<br/>Nom, Prénom,<br/>Problème}
        M -->|NON| K
        M -->|OUI| N[Création Ticket<br/>Automatique]
    end
    
    subgraph "5. BASE DE CONNAISSANCES"
        O[(Knowledge Base)]
        O -->|FAQ Free| O1[FAQ Officielle]
        O -->|Assistant| O2[Assistant Free]
        O -->|Procédures| O3[Procédures Internes]
        
        O1 & O2 & O3 -->|RAG| L
    end
    
    subgraph "6. RÉSOLUTION INTELLIGENTE"
        N -->|Ticket créé| P[Tentative de Résolution<br/>par Bot]
        P -->|Recherche KB| O
        P -->|Dialogue assisté| L
        
        P -->|Solution trouvée| Q{Problème<br/>Résolu?}
        Q -->|OUI| R[Clôture Automatique<br/>du Ticket]
        Q -->|NON après N essais| S[Escalade vers<br/>Agent Humain]
    end
    
    subgraph "7. INTERFACE INTERNE DE GESTION"
        N & R & S -->|Historique| T[(Base de Données<br/>Tickets)]
        T -->|Lecture| U[Interface Agents]
        
        U -->|Vue tickets| U1[Liste Tickets]
        U -->|Historique| U2[Détails Conversation]
        U -->|Action| U3[Reprise Manuelle]
        
        S -->|Notification| U
        U3 -->|Résolution| R
    end
    
    subgraph "8. TABLEAU DE BORD KPIs"
        T -->|Analytics| V[Dashboard KPIs]
        
        V -->|Métrique 1| V1[Taux de Résolution<br/>Automatique]
        V -->|Métrique 2| V2[Délai Moyen<br/>de Réponse]
        V -->|Métrique 3| V3[Taux d'Escalade<br/>Agent Humain]
        V -->|Métrique 4| V4[Satisfaction Client]
        V -->|Métrique 5| V5[Volume Tweets<br/>par Thème]
        
        V1 & V2 & V3 & V4 & V5 -->|Visualisations| W[Rapports & Alertes]
    end
    
    subgraph "9. STOCKAGE & MONITORING"
        X[(Data Warehouse)]
        C & T -->|ETL| X
        X -->|BI| V
        
        Y[Monitoring System]
        E & L & P -->|Logs| Y
        Y -->|Alertes| Z[Notifications Ops]
    end
    
    G -->|NON| AA[Archivage Tweet<br/>Non-Réclamation]
    AA -->|Statistiques| V
    
    style E fill:#1E3A5F,stroke:#2E86DE,color:#fff
    style L fill:#1E3A5F,stroke:#2E86DE,color:#fff
    style V fill:#10AC84,stroke:#0FB870,color:#fff
    style G fill:#F39C12,stroke:#E67E22,color:#fff
    style Q fill:#F39C12,stroke:#E67E22,color:#fff
    style M fill:#F39C12,stroke:#E67E22,color:#fff
```

## Flux de Données Détaillé

```mermaid
sequenceDiagram
    participant TW as Twitter/X
    participant COL as Collecteur
    participant CLS as Classificateur
    participant GEN as Générateur
    participant BOT as Chatbot
    participant KB as Knowledge Base
    participant TKT as Système Tickets
    participant AGT as Agent Humain
    participant KPI as Dashboard KPIs
    
    TW->>COL: Stream tweets @Free
    COL->>CLS: Tweet brut
    CLS->>CLS: Nettoyage + Classification
    
    alt Tweet = Réclamation
        CLS->>GEN: Tweet identifié comme réclamation
        GEN->>GEN: Génération réponse personnalisée
        GEN->>TW: Publication commentaire + lien chatbot
        
        TW->>BOT: Client clique sur lien
        BOT->>BOT: Demande Nom, Prénom, Problème
        
        loop Collecte informations
            BOT->>BOT: Validation données
        end
        
        BOT->>TKT: Création ticket automatique
        
        loop Tentatives de résolution
            BOT->>KB: Recherche solution
            KB->>BOT: Réponse KB
            BOT->>BOT: Proposition solution
            
            alt Solution acceptée
                BOT->>TKT: Clôture ticket (résolu)
                TKT->>KPI: Mise à jour métriques
            else Solution refusée
                BOT->>BOT: Nouvelle tentative
            end
        end
        
        alt Échec après N essais
            BOT->>TKT: Escalade ticket
            TKT->>AGT: Notification agent
            AGT->>AGT: Prise en charge manuelle
            AGT->>TKT: Résolution + clôture
            TKT->>KPI: Mise à jour métriques
        end
    else Tweet = Non-réclamation
        CLS->>TKT: Archivage statistique
        TKT->>KPI: Mise à jour volume
    end
    
    KPI->>KPI: Calcul KPIs en temps réel
```

## Architecture Technique par Composant

```mermaid
graph LR
    subgraph "BACKEND SERVICES"
        direction TB
        A1[FastAPI Server]
        A2[Celery Workers]
        A3[Redis Queue]
        A4[PostgreSQL]
        A5[MongoDB]
    end
    
    subgraph "ML MODELS"
        direction TB
        B1[BERT Fine-tuned]
        B2[Mistral 7B]
        B3[Rule Engine]
        B4[LLM Response Gen]
    end
    
    subgraph "FRONTEND"
        direction TB
        C1[Streamlit Dashboard]
        C2[Chatbot Web UI]
        C3[Agent Interface]
    end
    
    subgraph "EXTERNAL APIs"
        direction TB
        D1[Twitter API v2]
        D2[OpenAI API]
        D3[Hugging Face]
    end
    
    subgraph "STORAGE"
        direction TB
        E1[S3 Storage]
        E2[Vector DB]
        E3[Cache Redis]
    end
    
    C1 & C2 & C3 --> A1
    A1 --> A2
    A2 --> A3
    A2 --> B1 & B2 & B3 & B4
    A1 --> A4 & A5
    B4 --> D2
    A1 --> D1
    B1 & B2 --> D3
    A2 --> E1 & E2 & E3
    
    style B1 fill:#E74C3C,stroke:#C0392B,color:#fff
    style B2 fill:#E74C3C,stroke:#C0392B,color:#fff
    style B4 fill:#E74C3C,stroke:#C0392B,color:#fff
    style C1 fill:#3498DB,stroke:#2980B9,color:#fff
    style C2 fill:#3498DB,stroke:#2980B9,color:#fff
```

## Légende des Composants

### 🟦 Développé (Production Ready)
- **Système de Classification**: BERT + Mistral + Rules
- **Dashboard Streamlit**: Interface d'analyse et visualisation
- **Preprocessing Pipeline**: Nettoyage et normalisation des tweets
- **KPI Analytics**: Calcul et affichage des métriques

### 🟨 En Développement
- **Tweet Collector**: Capture automatique via Twitter API
- **Response Generator**: Génération de réponses personnalisées

### 🟥 À Développer
- **Chatbot Conversationnel**: Interface de dialogue client
- **Knowledge Base Integration**: Connexion FAQ/Assistant Free
- **Ticket Management System**: Création et suivi des tickets
- **Agent Interface**: Interface pour agents humains
- **Escalation Logic**: Logique de transfert automatique

## Métriques KPIs Principales

| KPI | Description | Objectif |
|-----|-------------|----------|
| **Taux de Classification** | % tweets correctement classifiés | > 90% |
| **Précision Réclamations** | Precision sur détection réclamations | > 85% |
| **Taux Résolution Auto** | % tickets résolus par bot | > 60% |
| **Délai Moyen Réponse** | Temps moyen première réponse | < 5 min |
| **Taux Escalade** | % tickets transmis agents | < 30% |
| **Satisfaction Client** | Score satisfaction post-résolution | > 4/5 |
| **Temps Résolution** | Durée moyenne clôture ticket | < 2h |

## Technologies Utilisées

### Classification (Actuel)
- **ML Frameworks**: PyTorch, Transformers, Scikit-learn
- **Models**: BERT (CamemBERT), Mistral 7B
- **Frontend**: Streamlit 1.28.1
- **Viz**: Plotly, Pandas
- **Storage**: CSV, JSON (academic version)

### Production (Futur)
- **Backend**: FastAPI, Celery
- **Database**: PostgreSQL (tickets), MongoDB (tweets)
- **Cache**: Redis
- **ML Serving**: Hugging Face Inference API
- **Deployment**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana
- **APIs**: Twitter API v2, OpenAI API

## Workflow de Déploiement

```mermaid
graph LR
    A[Code Push GitHub] --> B[CI/CD Pipeline]
    B --> C{Tests Pass?}
    C -->|OUI| D[Build Docker Image]
    C -->|NON| E[Notification Erreur]
    D --> F[Deploy Staging]
    F --> G{Validation?}
    G -->|OUI| H[Deploy Production]
    G -->|NON| I[Rollback]
    H --> J[Monitoring Actif]
    J --> K[Alertes si Anomalie]
    
    style C fill:#F39C12,stroke:#E67E22,color:#fff
    style G fill:#F39C12,stroke:#E67E22,color:#fff
    style H fill:#10AC84,stroke:#0FB870,color:#fff
```

## Évolutivité et Performance

### Scalabilité Horizontale
- **Tweet Collector**: Multi-threading pour capture en temps réel
- **Classification**: Batch processing parallèle
- **Chatbot**: Load balancing sur plusieurs instances
- **Database**: Sharding pour haute volumétrie

### Optimisations
- **Cache Redis**: Réponses fréquentes pré-calculées
- **Vector Database**: Recherche sémantique rapide dans KB
- **Model Serving**: Quantization + ONNX Runtime
- **CDN**: Assets statiques chatbot

---

**Version**: 1.0  
**Date**: 2024-01-10  
**Auteur**: FreeMobilaChat Team  
**Statut**: Architecture de Référence
