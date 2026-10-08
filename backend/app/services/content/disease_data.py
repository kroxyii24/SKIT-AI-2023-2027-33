"""
Disease Awareness Module.

Design decision: disease info is stored as STRUCTURED data (not free-text RAG
chunks) because this content needs consistent, predictable sections on every
disease page (Overview, Symptoms, Prevention, etc.) for the frontend to render
reliably. The RAG assistant can still cite/reference this content, but the
Disease Explorer page itself reads directly from this structured store, not
via LLM generation — reduces both latency and hallucination risk for content
users browse directly.
"""
from dataclasses import dataclass, field


@dataclass
class DiseaseInfo:
    slug: str
    name: str
    category: str  # communicable | non_communicable | mental_health | maternal | child | elderly
    overview: str
    symptoms: list[str]
    risk_factors: list[str]
    preventive_measures: list[str]
    government_initiatives: list[str]
    when_to_consult_doctor: str
    emergency_signs: list[str]
    trusted_references: list[dict] = field(default_factory=list)  # [{publisher, url}]


# Seed content — a small starting set; full corpus built out via Admin Portal
# ingestion in later milestones. This demonstrates the schema with real,
# publicly-known public health information (not diagnostic, purely educational).
SEED_DISEASES: list[DiseaseInfo] = [
    DiseaseInfo(
        slug="dengue",
        name="Dengue Fever",
        category="communicable",
        overview=(
            "Dengue is a mosquito-borne viral infection common across India, especially "
            "during and after the monsoon season. It spreads through the bite of infected "
            "Aedes mosquitoes."
        ),
        symptoms=["High fever", "Severe headache", "Pain behind the eyes", "Joint and muscle pain", "Skin rash", "Nausea"],
        risk_factors=["Living in or traveling to areas with standing water", "Monsoon season", "Previous dengue infection (increases severity risk)"],
        preventive_measures=["Eliminate standing water around homes", "Use mosquito nets and repellents", "Wear full-sleeved clothing", "Community fogging drives"],
        government_initiatives=["National Vector Borne Disease Control Programme (NVBDCP)"],
        when_to_consult_doctor="If fever persists beyond 2 days or is accompanied by severe symptoms, consult a doctor immediately.",
        emergency_signs=["Severe abdominal pain", "Persistent vomiting", "Bleeding gums or nose", "Difficulty breathing", "Extreme fatigue or restlessness"],
        trusted_references=[{"publisher": "WHO", "url": "https://www.who.int/health-topics/dengue-and-severe-dengue"}],
    ),
    DiseaseInfo(
        slug="type-2-diabetes",
        name="Type 2 Diabetes",
        category="non_communicable",
        overview="A chronic condition affecting how the body processes blood sugar, increasingly common in urban and rural India due to lifestyle changes.",
        symptoms=["Increased thirst", "Frequent urination", "Unexplained fatigue", "Blurred vision", "Slow-healing wounds"],
        risk_factors=["Family history", "Sedentary lifestyle", "Being overweight", "Poor diet"],
        preventive_measures=["Regular physical activity", "Balanced diet with less refined sugar", "Routine blood sugar screening after age 40"],
        government_initiatives=["National Programme for Prevention and Control of Cancer, Diabetes, CVD and Stroke (NPCDCS)"],
        when_to_consult_doctor="If you notice persistent symptoms above, or have risk factors and haven't been screened recently.",
        emergency_signs=["Confusion or difficulty waking", "Rapid breathing", "Fruity-smelling breath", "Loss of consciousness"],
        trusted_references=[{"publisher": "ICMR", "url": "https://main.icmr.nic.in"}],
    ),
]
