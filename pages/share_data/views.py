"""Views for the Share Data page.

The metadata standards table uses `DataTableMixin` so it is rendered
with the reusable data table component for consistent styling.
"""

from typing import Any

from django.utils.safestring import mark_safe

from core.mixins import DataTableMixin
from utils.html import safe_link
from utils.views import BaseTemplateView

METADATA_TABLE_ID = "metadata-standards"
METADATA_TABLE_LABEL = "Metadata standards by data type"
METADATA_HEADERS: list[str] = ["Data Type", "Standards", "Description"]

# Each row is [Data Type, Standard, Description].
# safe_link() builds the HTML links for the template.
# mark_safe() marks the text as safe for HTML rendering.
METADATA_ROWS: list[list[str]] = [
    # ── Genomics (4 rows) ────────────────────────────────────────────
    [
        "Genomics",
        safe_link(
            (
                "https://genomicsstandardsconsortium.github.io/mixs/",
                "MIxS (Minimum Information about any 'x' Sequence)",
            )
        ),
        mark_safe(
            "Developed by "
            + safe_link(("https://www.gensc.org/", "Genomic Standards Consortium"))
            + "; used for describing sequences from different environments"
            " (e.g., host-associated, environmental)."
        ),
    ],
    [
        "Genomics",
        safe_link(
            (
                "https://zenodo.org/records/5706412",
                "MINSEQE (Minimum Information about a High-Throughput Nucleotide"
                " Sequencing Experiment)",
            )
        ),
        mark_safe(
            "Recommended by "
            + safe_link(("https://www.fged.org/projects/minseqe/", "FGED"))
            + " for RNA-seq and other sequencing metadata."
        ),
    ],
    [
        "Genomics",
        safe_link(("https://www.ebi.ac.uk/ena/browser/checklists", "ENA Checklists")),
        mark_safe(
            "Specific checklists for submission to "
            + safe_link(("https://www.ebi.ac.uk/ena/browser/home", "European Nucleotide Archive"))
            + " (e.g., pathogen, human, metagenome)."
        ),
    ],
    [
        "Genomics",
        safe_link(
            ("https://isa-specs.readthedocs.io/en/latest/isatab.html", "ISA-Tab"),
            ("https://isa-specs.readthedocs.io/en/latest/isajson.html", "ISA-JSON"),
        ),
        "Framework for describing experimental metadata, often used with"
        " bioinformatics tools and databases.",
    ],
    # ── Proteomics (3 rows) ──────────────────────────────────────────
    [
        "Proteomics",
        safe_link(
            (
                "https://www.psidev.info/miape",
                "MIAPE (Minimum Information About a Proteomics Experiment)",
            )
        ),
        mark_safe(
            "Developed by "
            + safe_link(
                (
                    "https://www.psidev.info/about-the-hupo-proteomics-standards-initiative-psi",
                    "HUPO-PSI",
                )
            )
            + "; covers mass spectrometry, sample processing, informatics."
        ),
    ],
    [
        "Proteomics",
        safe_link(
            ("https://github.com/HUPO-PSI/miXML/wiki", "PSI-MI XML"),
            ("https://psicquic.github.io/MITAB28Format.html", "MITAB"),
        ),
        mark_safe(
            safe_link(("https://psicquic.github.io/", "For molecular interaction"))
            + " data formats (used in interaction databases)."
        ),
    ],
    [
        "Proteomics",
        safe_link(
            ("https://sbeams.systemsbiology.net/tmp/mzML1.0.0.html", "mzML"),
            ("https://www.psidev.info/mzidentml", "mzIdentML"),
            ("https://www.psidev.info/mztab-specifications", "mzTab"),
        ),
        "Standard formats for raw data, identifications, vocabulary and"
        " quantification results in the field of mass spectrometry-based"
        " proteomics.",
    ],
    # ── Imaging (3 rows) ─────────────────────────────────────────────
    [
        "Imaging",
        safe_link(
            (
                "https://docs.openmicroscopy.org/ome-model/5.6.3"
                "/ome-tiff/specification.html#ome-xml-metadata",
                "OME-TIFF / OME-XML",
            )
        ),
        mark_safe(
            "Developed by "
            + safe_link(("https://www.openmicroscopy.org/", "Open Microscopy Environment"))
            + "; widely used for storing microscopy images and associated metadata."
        ),
    ],
    [
        "Imaging",
        safe_link(
            (
                "https://www.nature.com/articles/s41592-021-01166-8",
                "REMBI (Recommended Metadata for Biological Images)",
            )
        ),
        "Designed to enable reproducibility and data reuse for imaging datasets.",
    ],
    [
        "Imaging",
        safe_link(
            (
                "https://www.dicomstandard.org/current",
                "DICOM (Digital Imaging and Communications in Medicine)",
            )
        ),
        "Standard for handling, storing, and transmitting medical imaging"
        " information (e.g., CT, MRI).",
    ],
    # ── Bioassays / Experimental Data (3 rows) ───────────────────────
    [
        "Bioassays / Experimental Data",
        safe_link(
            (
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC5031183/",
                "MIACA (Minimum Information About a Cellular Assay)",
            )
        ),
        "For reporting cellular assays, including experimental context and protocols.",
    ],
    [
        "Bioassays / Experimental Data",
        safe_link(
            (
                "https://www.nature.com/articles/nrd3503",
                "MIABE (Minimum Information About a Bioactive Entity)",
            )
        ),
        "For small molecule screening and bioactivity reporting.",
    ],
    [
        "Bioassays / Experimental Data",
        safe_link(("http://bioassayontology.org/bioassayontology/", "BAO (BioAssay Ontology)")),
        "Ontology that enables uniform annotation of bioassays and protocols.",
    ],
    # ── Clinical & Health Data (5 rows) ──────────────────────────────
    [
        "Clinical & Health Data",
        mark_safe(
            safe_link(("https://www.cdisc.org/standards/foundational", "CDISC standards"))
            + " (e.g., "
            + safe_link(("https://learnstore.cdisc.org/catalog?pagename=SDTM", "SDTM"))
            + ", ADaM, SEND)"
        ),
        "Industry standards for clinical trial data exchange and analysis.",
    ],
    [
        "Clinical & Health Data",
        safe_link(
            (
                "https://confluence.hl7.org/spaces/FHIR/overview",
                "HL7 / FHIR (Fast Healthcare Interoperability Resources)",
            )
        ),
        "Widely adopted in EHR systems for structured health data.",
    ],
    [
        "Clinical & Health Data",
        safe_link(
            ("https://loinc.org/", "LOINC"),
            ("https://www.snomed.org/", "SNOMED CT"),
            ("https://icd.who.int/browse10/2019/en", "ICD-10"),
        ),
        "Controlled vocabularies for lab tests, symptoms, diagnoses.",
    ],
    [
        "Clinical & Health Data",
        safe_link(
            (
                "https://physionet.org/news/post/mimic-derived-datasets-models",
                "MIMIC-IV Metadata Guidelines",
            )
        ),
        "For structured ICU/clinical datasets in open research.",
    ],
    [
        "Clinical & Health Data",
        safe_link(
            ("https://www.dublincore.org/", "Dublin Core"),
            ("https://docs.dataportal.se/dcat/sv/", "DCAT-AP-SE"),
        ),
        "Metadata cataloging for health data in national repositories.",
    ],
    # ── Omics Imaging (3 rows) ───────────────────────────────────────
    [
        "Omics Imaging",
        mark_safe(
            safe_link(("https://db.cngb.org/stomics/mosta/", "STOMIC"))
            + " (Spatial Transcriptomics Open Metadata and Image Convention)"
        ),
        "A proposed standard for organizing spatial omics data.",
    ],
    [
        "Omics Imaging",
        safe_link(
            ("https://isa-specs.readthedocs.io/en/latest/isatab.html", "ISA-Tab"),
            ("https://docs.openmicroscopy.org/ome-model/5.6.3/ome-xml/", "OME-XML"),
        ),
        "For integrating omics and imaging data.",
    ],
    [
        "Omics Imaging",
        safe_link(("https://hupo.org/B/D-HPP", "HUPO-B/D Standards")),
        "For multimodal single-cell data and proteogenomics metadata.",
    ],
    # ── Metabolomics Data (2 rows) ───────────────────────────────────
    [
        "Metabolomics Data",
        safe_link(
            ("https://isa-specs.readthedocs.io/en/latest/isatab.html", "ISA-Tab"),
            ("https://isa-specs.readthedocs.io/en/latest/isajson.html", "ISA-JSON"),
        ),
        "Describes experimental design, sample preparation, and data files.",
    ],
    [
        "Metabolomics Data",
        safe_link(
            (
                "https://github.com/MSI-Metabolomics-Standards-Initiative/CIMR",
                "Metabolomics Standards Initiative (MSI)",
            )
        ),
        "Offers domain-specific guidelines for metadata and reporting.",
    ],
]


class ShareData(DataTableMixin, BaseTemplateView):
    """Render the Share Data page with an interactive metadata standards table."""

    template_name = "share_data/index.html"
    title = "Share Data"

    # Show up to 30 rows on the page
    per_page_default = 30

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add the metadata standards table context."""
        context = super().get_context_data(**kwargs)
        context["metadata_table"] = self.get_table_context(
            self.request,
            METADATA_ROWS,
            METADATA_HEADERS,
            self.request.path,
            table_id=METADATA_TABLE_ID,
            table_label=METADATA_TABLE_LABEL,
            show_controls=False,
        )
        return context
