import pytest


@pytest.fixture
def sample_health_text():
    return (
        "Dengue is a mosquito-borne viral disease. "
        "It spreads through the bite of infected Aedes mosquitoes. "
        "Symptoms may include high fever, headache, and joint pain. "
        "Drink adequate fluids and seek medical advice if symptoms worsen. "
        "Avoid mosquito bites by using protective clothing and mosquito nets. "
        "Remove stagnant water around your home to prevent mosquito breeding. "
        "Severe abdominal pain or persistent vomiting requires urgent medical attention."
    )
