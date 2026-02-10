"""Views for dashboards index page."""

from utils.views import BaseTemplateView


class ExternalDashboards(BaseTemplateView):
    """Index page for External Dashboard.

    WIP: currently a simple templateview but will be updated later
    """

    template_name = "dashboards/external_dashboards.html"
    title = "Data dashboards"

    # This is a temporary workaround for the MVP, the following dict
    # might be removed and the info will be fetched from DB.
    extra_context = {
        # a list of EXTERNAL dashboards
        "external_dashboards": [
            {
                "name": "SvarmIT: interactive resistance monitoring",
                "image": "dashboards/thumbnails/external/sva_logo.png",
                "url": "https://www.sva.se/djurhaelsa/antibiotika/oevervakning/svarmit-interaktivt-resistensoevervakningsverktyg/",
                "description": (
                    "Interactive visualisation to show the occurrence of resistance "
                    "among different types of bacteria from animals."
                ),
            },
            {
                "name": "Avian Influenza: infection status with map",
                "image": "dashboards/thumbnails/external/sva_logo.png",
                "url": "https://www.sva.se/djurhaelsa/djursjukdomar-a-oe/sjukdomar/faagelinfluensa/faagelinfluensa-smittlaege-med-karta/",
                "description": (
                    "The transmission of avian influenza is variable "
                    "and is continuously monitored by sampling domestic birds that "
                    "are reported to have symptoms that may indicate avian influenza."
                ),
            },
            {
                "name": "Campylobacter in broiler chickens",
                "image": "dashboards/thumbnails/external/sva_logo.png",
                "url": "https://svastatichosting.z6.web.core.windows.net/maps/campy_graph/barchart.html",
                "description": ("Surveillance dedicated to monitor campylobacter in chickens."),
            },
            {
                "name": "Covid-19 – Confirmed cases in Sweden",
                "image": "dashboards/thumbnails/external/fohm_logo.png",
                "url": "https://www.folkhalsomyndigheten.se/fall-covid-19/",
                "description": (
                    "Shows an up-to-date interactive visualisation "
                    "of the number of confirmed COVID-19 cases in Sweden over time "
                    "(with options to compare by region and other filters)."
                ),
            },
            {
                "name": "Covid-19 – Tested with PCR ",
                "image": "dashboards/thumbnails/external/fohm_logo.png",
                "url": "https://www.folkhalsomyndigheten.se/PCR-covid-19/",
                "description": (
                    "Visualisation of weekly PCR testing statistics for COVID-19 in Sweden, "
                    "including the number of individuals tested, PCR tests conducted, "
                    "and related breakdowns by age, region and other variables."
                ),
            },
            {
                "name": "Covid-19 – Vaccinations ",
                "image": "dashboards/thumbnails/external/fohm_logo.png",
                "url": "https://www.folkhalsomyndigheten.se/vaccination-covid-19/",
                "description": (
                    "COVID-19 vaccination coverage in Sweden, showing numbers and "
                    "proportions of vaccinated individuals over time, broken down by age group,  "
                    "region, and dose type, using data from the national vaccinations database."
                ),
            },
            {
                "name": "Influenza – Confirmed cases in Sweden",
                "image": "dashboards/thumbnails/external/fohm_logo.png",
                "url": "https://www.folkhalsomyndigheten.se/faktablad/fall-influensa/",
                "description": (
                    "Laboratory confirmed influenza cases in Sweden over time, with options "
                    "to explore trends by region, age group and calendar week based on data  "
                    "from the national health data system."
                ),
            },
            {
                "name": "RS virus infection – Confirmed cases in Sweden",
                "image": "dashboards/thumbnails/external/fohm_logo.png",
                "url": "https://www.folkhalsomyndigheten.se/faktablad/fall-RS-virus/",
                "description": (
                    "Shows the statistics of the number of confirmed RS‑virus "
                    "(respiratory syncytial virus) cases in Sweden over time, allowing "
                    "exploration by region, age group and other filters using "
                    "national surveillance data."
                ),
            },
            {
                "name": "Real-time tracking of influenza A/H5N1 virus evolution",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/avian-flu/h5n1/ha/2y?c=country&f_country=Sweden",
                "description": (
                    "Phylogenetic visualisation of avian influenza A (H5N1) hemagglutinin (HA) "
                    "gene sequences from the past two years, highlighting the genetic "
                    "relationships and temporal evolution of strains with a filter "
                    "showing sequences from Sweden in the global context."
                ),
            },
            {
                "name": "Real-time tracking of influenza A/H3N2 evolution",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/seasonal-flu/h3n2/ha/2y?c=country&f_country=Sweden",
                "description": (
                    "Phylogenetic visualisation of the hemagglutinin (HA) "
                    "gene of seasonal influenza A (H3N2) viruses over the past "
                    "2 years, with sequences from Sweden highlighted. "
                ),
            },
            {
                "name": "Genomic epidemiology of SARS-CoV-2",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/ncov/open/global/6m?c=country&f_country=Sweden",
                "description": (
                    "Phylogenetic and temporal visualisation of global SARS-CoV-2 "
                    "genomic data over the past six months, with sequences from Sweden "
                    "highlighted to help explore how Swedish data relate to worldwide "
                    "SARS-CoV-2 diversity and spread. "
                ),
            },
            {
                "name": "SARS-CoV-2 phylogeny",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/groups/neherlab/ncov/sweden?c=clade_membership&f_country=Sweden&p=grid&r=division",
                "description": (
                    "Genomic surveillance visualisation showing the phylogenetic relationships and "
                    "clade membership of SARS-CoV-2 sequences from Sweden, allowing exploration of "
                    "how different viral lineages are distributed across Swedish regions and over "
                    "time in the context of the global pandemic."
                ),
            },
            {
                "name": "Real-time tracking of measles N450 virus evolution",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/measles/N450?c=country&f_country=Sweden",
                "description": (
                    "Phylogenetic visualisation of measles N450 virus sequences, "
                    "showing measles viruses from Sweden enabling exploration of transmission "
                    "patterns and lineage diversity. "
                ),
            },
            {
                "name": "Real-time tracking of Mycobacterium tuberculosis full genome evolution",
                "image": "dashboards/thumbnails/external/nextstrain_logo.png",
                "url": "https://nextstrain.org/tb/global?f_country=Sweden",
                "description": (
                    "Mycobacterium tuberculosis genomic data, with Swedish isolates highlighted "
                    "to help explore their evolutionary relationships, lineages and distribution "
                    "in the context of worldwide TB diversity. "
                ),
            },
        ],
    }
