from django.db import migrations
from django.utils import timezone


def seed_projects(apps, schema_editor):
    PlpProject = apps.get_model("plp", "PlpProject")

    projects = [
        {
            "title": "Multi-disease serology",
            "slug": "multi-disease-serology",
            "category": "plp1",
            "summary": "High-throughput serology platform expanding to multi-disease surveillance.",
            "content": (
                "High-throughput serology analysis is important for evaluating the serostatus and potential "
                "immunity of the population. The workflow developed at KTH and SciLifeLab now scales beyond "
                "SARS-CoV-2 to cover hundreds of antigens across respiratory and other infectious diseases. "
                "The platform can analyse thousands of samples and adapts quickly to new pathogens."
            ),
            "external_url": "https://www.pathogens.se/resources/serology/",
        },
        {
            "title": "Genomic Pandemic Preparedness Portfolio (G3P)",
            "slug": "genomic-pandemic-preparedness-portfolio",
            "category": "plp1",
            "summary": "Nationwide genomics portfolio for outbreak detection and surveillance.",
            "content": (
                "G3P builds sequencing-based preparedness with harmonised laboratory assays, bioinformatics "
                "workflows, and data visualisation to detect emerging pathogens and track antimicrobial resistance. "
                "The program connects Clinical Genomics nodes, Genomic Medicine Centers, and clinical microbiology "
                "labs to enable rapid national coverage and point-of-care support."
            ),
            "external_url": "https://www.pathogens.se/resources/g3p/",
        },
        {
            "title": "Rapid establishment of comprehensive laboratory pandemic preparedness – RAPID-SEQ",
            "slug": "rapid-seq",
            "category": "plp1",
            "summary": "Large-scale sequencing and metagenomics pipeline for rapid pathogen surveillance.",
            "content": (
                "RAPID-SEQ leverages collaboration between Karolinska University Laboratory, SciLifeLab, and "
                "Genomic Medicine Sweden to deliver high-capacity whole-genome sequencing of SARS-CoV-2 and "
                "metagenomic diagnostics. The project supports rapid variant tracking, neutralisation studies, and "
                "publishes open bioinformatics workflows for national use."
            ),
            "external_url": "https://www.pathogens.se/resources/rapid-seq/",
        },
        {
            "title": "BSL3 Biomedicum-SciLifeLab Collaborative Platform",
            "slug": "bsl3-biomedicum",
            "category": "plp1",
            "summary": "State-of-the-art BSL3 facility and Swedish BSL3 network for pandemic research.",
            "content": (
                "The Biomedicum BSL3 platform provides RG3 pathogen handling, high-throughput screening, and "
                "aerosol research capabilities, supporting rapid responses to new outbreaks. It anchors a Swedish "
                "BSL3 network that shares methods, equipment, and expertise to cut response times in future pandemics."
            ),
            "external_url": "https://www.pathogens.se/resources/bsl3/",
        },
        {
            "title": "Pandemic preparedness against antimicrobial resistance through wastewater monitoring",
            "slug": "amr-wastewater-monitoring",
            "category": "plp2",
            "summary": "Wastewater-based surveillance to detect antimicrobial resistance threats early.",
            "content": (
                "This project develops wastewater monitoring to track antimicrobial resistance at population scale. "
                "By combining metagenomics with modelling, the platform aims to provide early warning signals for "
                "clinically relevant resistance trends and to guide interventions before outbreaks escalate."
            ),
            "external_url": "https://www.pathogens.se/resources/amr_wastewater/",
        },
    ]

    for project in projects:
        PlpProject.objects.get_or_create(
            slug=project["slug"],
            defaults={
                "title": project["title"],
                "category": project["category"],
                "summary": project["summary"],
                "content": project["content"],
                "external_url": project["external_url"],
                "created_at": timezone.now(),
                "is_active": True,
            },
        )


def remove_projects(apps, schema_editor):
    PlpProject = apps.get_model("plp", "PlpProject")
    slugs = [
        "multi-disease-serology",
        "genomic-pandemic-preparedness-portfolio",
        "rapid-seq",
        "bsl3-biomedicum",
        "amr-wastewater-monitoring",
    ]
    PlpProject.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("plp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_projects, remove_projects),
    ]



