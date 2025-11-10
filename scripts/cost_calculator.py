"""
Calculateur de Coûts et Ressources - FreeMobilaChat
=====================================================

Outil d'estimation des coûts et ressources nécessaires
pour les différentes phases du projet.

Fonctionnalités:
- Estimation coûts personnel par rôle
- Calcul coûts infrastructure (serveurs, GPU, stockage)
- Estimation coûts APIs cloud (LLM providers)
- Projection budget par phase
- Export rapports Excel/CSV
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json

import pandas as pd


@dataclass
class PersonnelCost:
    """Coût du personnel par rôle"""
    role: str
    daily_rate: float  # Taux journalier en euros
    days: int  # Nombre de jours travaillés
    
    @property
    def total_cost(self) -> float:
        return self.daily_rate * self.days


@dataclass
class InfrastructureCost:
    """Coût infrastructure"""
    item: str
    unit_cost: float  # Coût unitaire (€/mois ou €/heure)
    quantity: int
    duration_months: float
    cost_type: str  # "monthly" ou "hourly"
    
    @property
    def total_cost(self) -> float:
        if self.cost_type == "monthly":
            return self.unit_cost * self.quantity * self.duration_months
        else:  # hourly
            hours = self.duration_months * 730  # ~730h par mois
            return self.unit_cost * self.quantity * hours


@dataclass
class APICost:
    """Coût APIs cloud"""
    provider: str
    cost_per_1k_tokens: float
    estimated_tokens: int
    
    @property
    def total_cost(self) -> float:
        return (self.estimated_tokens / 1000) * self.cost_per_1k_tokens


class CostCalculator:
    """
    Calculateur de coûts complet pour projet FreeMobilaChat
    
    Estime les coûts pour chaque phase du projet:
    - Phase 1: Exploration (2-3 semaines)
    - Phase 2: Données (3-4 semaines)
    - Phase 3: Développement (6-8 semaines)
    - Phase 4: Documentation (2-3 semaines)
    - Phase 5: Déploiement (2 semaines)
    """
    
    # Taux journaliers moyens (France, 2025)
    RATES = {
        "data_scientist": 450,
        "ml_engineer": 500,
        "fullstack_dev": 400,
        "qa_engineer": 350,
        "devops": 450,
        "annotator": 150,
        "supervisor": 600
    }
    
    # Coûts infrastructure mensuels
    INFRA_COSTS = {
        "server_cpu_16c_32gb": 150,
        "gpu_rtx3090": 200,
        "storage_100gb": 10,
        "bandwidth_1tb": 50
    }
    
    # Coûts APIs LLM (€ par 1M tokens)
    API_COSTS = {
        "openai_gpt4": 30.0,
        "anthropic_claude": 24.0,
        "mistral_api": 6.0
    }
    
    def __init__(self):
        self.personnel_costs: List[PersonnelCost] = []
        self.infra_costs: List[InfrastructureCost] = []
        self.api_costs: List[APICost] = []
    
    def estimate_phase1_exploration(self) -> Dict[str, float]:
        """
        Phase 1: Exploration et Cadrage (2-3 semaines)
        
        Équipe:
        - 1 Data Scientist (temps partiel 50%)
        - 1 Superviseur académique (10%)
        
        Returns:
            Dictionnaire avec coûts détaillés
        """
        # Personnel
        ds = PersonnelCost("Data Scientist", self.RATES["data_scientist"], 7.5)
        sup = PersonnelCost("Superviseur", self.RATES["supervisor"], 1.5)
        
        self.personnel_costs.extend([ds, sup])
        
        # Infrastructure (utilisation université - gratuit)
        # Pas de coûts infrastructure pour phase académique
        
        return {
            "personnel": ds.total_cost + sup.total_cost,
            "infrastructure": 0,
            "apis": 0,
            "total": ds.total_cost + sup.total_cost
        }
    
    def estimate_phase2_data(self) -> Dict[str, float]:
        """
        Phase 2: Préparation Données (3-4 semaines)
        
        Équipe:
        - 1 Data Scientist (temps plein)
        - 2 Annotateurs (2 semaines chacun)
        
        Infrastructure:
        - Serveur CPU (1 mois)
        - Stockage 50GB (1 mois)
        
        Returns:
            Dictionnaire avec coûts détaillés
        """
        # Personnel
        ds = PersonnelCost("Data Scientist", self.RATES["data_scientist"], 20)
        ann1 = PersonnelCost("Annotateur 1", self.RATES["annotator"], 10)
        ann2 = PersonnelCost("Annotateur 2", self.RATES["annotator"], 10)
        
        self.personnel_costs.extend([ds, ann1, ann2])
        
        # Infrastructure (si non universitaire)
        server = InfrastructureCost("Serveur CPU", self.INFRA_COSTS["server_cpu_16c_32gb"], 1, 1, "monthly")
        storage = InfrastructureCost("Stockage", self.INFRA_COSTS["storage_100gb"], 1, 1, "monthly")
        
        # Pour projet académique, infra gratuite (université)
        infra_cost = 0  # server.total_cost + storage.total_cost si production
        
        personnel_total = sum([c.total_cost for c in [ds, ann1, ann2]])
        
        return {
            "personnel": personnel_total,
            "infrastructure": infra_cost,
            "apis": 0,
            "total": personnel_total + infra_cost
        }
    
    def estimate_phase3_development(self) -> Dict[str, float]:
        """
        Phase 3: Développement (6-8 semaines)
        
        Équipe:
        - 1 Data Scientist / ML Engineer (temps plein)
        - 1 Développeur Full-Stack (50%)
        - 1 QA Engineer (25%)
        
        Infrastructure:
        - GPU RTX 3090 (2 mois cloud ou local)
        - Serveur CPU (2 mois)
        - Stockage 100GB (2 mois)
        
        APIs:
        - Tests OpenAI/Anthropic (~500k tokens)
        
        Returns:
            Dictionnaire avec coûts détaillés
        """
        # Personnel
        ml_eng = PersonnelCost("ML Engineer", self.RATES["ml_engineer"], 40)
        dev = PersonnelCost("Full-Stack Dev", self.RATES["fullstack_dev"], 20)
        qa = PersonnelCost("QA Engineer", self.RATES["qa_engineer"], 10)
        
        self.personnel_costs.extend([ml_eng, dev, qa])
        
        # Infrastructure (si cloud payant)
        gpu = InfrastructureCost("GPU RTX 3090", 200, 1, 2, "monthly")  # Cloud GPU
        server = InfrastructureCost("Serveur CPU", self.INFRA_COSTS["server_cpu_16c_32gb"], 1, 2, "monthly")
        storage = InfrastructureCost("Stockage", self.INFRA_COSTS["storage_100gb"], 1, 2, "monthly")
        
        # Pour académique: GPU local (0€) ou cloud (400€)
        infra_cost = 400  # GPU cloud uniquement
        
        # APIs (tests LLM cloud)
        api_openai = APICost("OpenAI GPT-4", self.API_COSTS["openai_gpt4"] / 1000, 300000)
        api_claude = APICost("Anthropic Claude", self.API_COSTS["anthropic_claude"] / 1000, 200000)
        
        self.api_costs.extend([api_openai, api_claude])
        
        api_total = api_openai.total_cost + api_claude.total_cost
        personnel_total = sum([c.total_cost for c in [ml_eng, dev, qa]])
        
        return {
            "personnel": personnel_total,
            "infrastructure": infra_cost,
            "apis": api_total,
            "total": personnel_total + infra_cost + api_total
        }
    
    def estimate_phase4_documentation(self) -> Dict[str, float]:
        """
        Phase 4: Documentation Académique (2-3 semaines)
        
        Équipe:
        - 1 Data Scientist (rédaction personnelle)
        
        Returns:
            Dictionnaire avec coûts détaillés
        """
        # Personnel (travail personnel étudiant - pas facturé)
        # Mais pour estimation coût réel:
        ds = PersonnelCost("Data Scientist", self.RATES["data_scientist"], 12)
        
        # Pas de coûts infrastructure ou APIs
        
        return {
            "personnel": 0,  # Travail personnel non facturé
            "infrastructure": 0,
            "apis": 0,
            "total": 0
        }
    
    def estimate_phase5_deployment(self) -> Dict[str, float]:
        """
        Phase 5: Déploiement Production (2 semaines)
        
        Équipe:
        - 1 DevOps / ML Engineer (50%)
        
        Infrastructure:
        - Streamlit Cloud (gratuit tier)
        - GitHub Actions (gratuit tier)
        
        Returns:
            Dictionnaire avec coûts détaillés
        """
        # Personnel
        devops = PersonnelCost("DevOps", self.RATES["devops"], 5)
        
        # Infrastructure (tier gratuit)
        infra_cost = 0  # Streamlit Cloud + GitHub Actions gratuit
        
        return {
            "personnel": 0,  # Déploiement personnel
            "infrastructure": infra_cost,
            "apis": 0,
            "total": infra_cost
        }
    
    def calculate_total_budget(self) -> pd.DataFrame:
        """
        Calcule le budget total pour toutes les phases
        
        Returns:
            DataFrame pandas avec breakdown par phase
        """
        phases = {
            "Phase 1: Exploration": self.estimate_phase1_exploration(),
            "Phase 2: Données": self.estimate_phase2_data(),
            "Phase 3: Développement": self.estimate_phase3_development(),
            "Phase 4: Documentation": self.estimate_phase4_documentation(),
            "Phase 5: Déploiement": self.estimate_phase5_deployment()
        }
        
        df = pd.DataFrame.from_dict(phases, orient='index')
        df['phase'] = df.index
        
        # Ajouter ligne totaux
        totals = df[['personnel', 'infrastructure', 'apis', 'total']].sum()
        totals_row = pd.DataFrame([{
            'phase': 'TOTAL',
            'personnel': totals['personnel'],
            'infrastructure': totals['infrastructure'],
            'apis': totals['apis'],
            'total': totals['total']
        }])
        
        df = pd.concat([df, totals_row], ignore_index=True)
        
        return df
    
    def generate_report(self) -> str:
        """
        Génère un rapport de coûts formaté
        
        Returns:
            Rapport texte formaté
        """
        df = self.calculate_total_budget()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║        ESTIMATION BUDGÉTAIRE - FREEMOBILACHAT                ║
║                  Master Data Science & IA                     ║
╚══════════════════════════════════════════════════════════════╝

Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""
        
        for _, row in df.iterrows():
            if row['phase'] == 'TOTAL':
                report += "\n" + "═" * 64 + "\n"
            
            report += f"""
{row['phase']}
  Personnel:        {row['personnel']:>10,.2f} €
  Infrastructure:   {row['infrastructure']:>10,.2f} €
  APIs Cloud:       {row['apis']:>10,.2f} €
  ──────────────────────────────
  TOTAL:            {row['total']:>10,.2f} €
"""
        
        report += "\n" + "═" * 64 + "\n"
        report += f"""
NOTES:
- Budget académique optimisé (infrastructures universitaires gratuites)
- Personnel Phase 4-5 = travail personnel non facturé
- Budget production réel serait ~25,000-35,000€
- Tier gratuit utilisé: Streamlit Cloud, GitHub Actions, Ollama local

RECOMMANDATIONS:
✓ Utiliser infrastructures universitaires (0€)
✓ Ollama local plutôt que APIs cloud (-200€)
✓ Streamlit Cloud gratuit pour déploiement (0€)
✓ Budget étudiant réaliste: 2,500-3,500€ (annotation + tests APIs)
"""
        
        return report
    
    def export_to_excel(self, filepath: str = "budget_freemobilachat.xlsx"):
        """
        Exporte le budget vers Excel
        
        Args:
            filepath: Chemin du fichier Excel
        """
        df = self.calculate_total_budget()
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Budget Global', index=False)
            
            # Feuille détails personnel
            if self.personnel_costs:
                personnel_df = pd.DataFrame([
                    {
                        'Rôle': c.role,
                        'Taux journalier (€)': c.daily_rate,
                        'Jours': c.days,
                        'Coût total (€)': c.total_cost
                    }
                    for c in self.personnel_costs
                ])
                personnel_df.to_excel(writer, sheet_name='Personnel', index=False)
            
            # Feuille détails APIs
            if self.api_costs:
                api_df = pd.DataFrame([
                    {
                        'Provider': c.provider,
                        'Coût/1k tokens (€)': c.cost_per_1k_tokens,
                        'Tokens estimés': c.estimated_tokens,
                        'Coût total (€)': c.total_cost
                    }
                    for c in self.api_costs
                ])
                api_df.to_excel(writer, sheet_name='APIs Cloud', index=False)
        
        print(f"✓ Budget exporté: {filepath}")
    
    def export_to_json(self, filepath: str = "budget_freemobilachat.json"):
        """
        Exporte le budget vers JSON
        
        Args:
            filepath: Chemin du fichier JSON
        """
        budget = {
            "project": "FreeMobilaChat",
            "generated_at": datetime.now().isoformat(),
            "phases": {},
            "total": {}
        }
        
        phases = {
            "phase1_exploration": self.estimate_phase1_exploration(),
            "phase2_data": self.estimate_phase2_data(),
            "phase3_development": self.estimate_phase3_development(),
            "phase4_documentation": self.estimate_phase4_documentation(),
            "phase5_deployment": self.estimate_phase5_deployment()
        }
        
        budget["phases"] = phases
        budget["total"] = {
            "personnel": sum(p["personnel"] for p in phases.values()),
            "infrastructure": sum(p["infrastructure"] for p in phases.values()),
            "apis": sum(p["apis"] for p in phases.values()),
            "total": sum(p["total"] for p in phases.values())
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(budget, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Budget exporté: {filepath}")


def main():
    """Fonction principale pour test et génération rapport"""
    calculator = CostCalculator()
    
    # Générer rapport console
    print(calculator.generate_report())
    
    # Exporter vers Excel et JSON
    calculator.export_to_excel("scripts/budget_freemobilachat.xlsx")
    calculator.export_to_json("scripts/budget_freemobilachat.json")
    
    # Afficher DataFrame
    print("\n📊 TABLEAU RÉCAPITULATIF:")
    df = calculator.calculate_total_budget()
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
