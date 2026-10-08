"""
Government Health Services module — same structured-data pattern as
disease_data.py, for the same reasons: predictable rendering, low latency,
no hallucination risk on eligibility/procedural information where accuracy
really matters (getting this wrong could cost someone a benefit they're
entitled to).
"""
from dataclasses import dataclass, field


@dataclass
class GovtScheme:
    slug: str
    name: str
    overview: str
    eligibility: list[str]
    benefits: list[str]
    how_to_apply: list[str]
    official_links: list[dict] = field(default_factory=list)


SEED_SCHEMES: list[GovtScheme] = [
    GovtScheme(
        slug="ayushman-bharat-pmjay",
        name="Ayushman Bharat - PM-JAY",
        overview=(
            "A national health insurance scheme providing coverage up to Rs. 5 lakh per "
            "family per year for secondary and tertiary hospital care, aimed at low-income "
            "and vulnerable families."
        ),
        eligibility=["Families identified per SECC 2011 deprivation criteria", "No cap on family size or age"],
        benefits=["Cashless hospitalization up to Rs. 5 lakh/year per family", "Covers pre- and post-hospitalization expenses", "Portable across India"],
        how_to_apply=["Check eligibility on the PM-JAY website or app", "Visit nearest Ayushman Bharat Kendra or empanelled hospital with ID proof"],
        official_links=[{"label": "PM-JAY Official Site", "url": "https://pmjay.gov.in"}],
    ),
    GovtScheme(
        slug="janaushadhi",
        name="Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
        overview="A scheme providing quality generic medicines at affordable prices through dedicated Jan Aushadhi Kendras.",
        eligibility=["Available to all citizens — no application needed to use the stores"],
        benefits=["Generic medicines at 50-90% lower cost than branded equivalents"],
        how_to_apply=["Visit any Jan Aushadhi Kendra directly with a doctor's prescription"],
        official_links=[{"label": "Janaushadhi Official Site", "url": "https://janaushadhi.gov.in"}],
    ),
    GovtScheme(
        slug="esanjeevani",
        name="eSanjeevani",
        overview="India's national telemedicine service enabling free doctor consultations from home via video call.",
        eligibility=["Available to all Indian citizens with internet access"],
        benefits=["Free doctor consultation", "Avoids travel for minor ailments", "Available in multiple languages"],
        how_to_apply=["Register on the eSanjeevani portal or app with basic details", "Book a slot and consult via video call"],
        official_links=[{"label": "eSanjeevani Official Site", "url": "https://esanjeevani.mohfw.gov.in"}],
    ),
]
