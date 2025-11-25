# Swedish Pathogens Portal

***WIP repository for Swedish Pathogens Portal 2.0***

The Swedish Pathogens Portal is being rebuilt as a Django-based web application.

The source code for the current (live) Swedish Pathogens Portal can be found in the [pathogens-portal repository](https://github.com/ScilifelabDataCentre/pathogens-portal).

## Technology Stack

- **Backend**: Django
- **Database**: PostgreSQL
- **Template Engine**: Django templates
- **CSS Framework**: TailwindCSS
- **JavaScript**: htmx
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- uv (for local development)
- git

## Setup

### 1. Clone the repository

Open a terminal window, go to the directory where you want to clone the repository and run

```bash
git clone git@github.com:ScilifelabDataCentre/swedish-pathogens-portal.git
```

**NOTE:** The sections below assume you are in the project's root

### 2. Create a `.env` file

For local development, you can copy `.env.example`

```bash
cp .env.example .env
```

### 3. Start the application

```bash
docker compose up
```

After the application starts, open `http://localhost:8000` in your browser.

## Development / Contributing

### Running tests (WIP)

***This section will be updated as tests are added***

```bash
docker compose exec web python manage.py test
```

If you are running the project locally without Docker:

```bash
uv run python manage.py test
```

### Running migrations

To apply database changes, run Django migrations:

```bash
docker compose exec web python manage.py migrate
```

### Making migrations

For new apps and models, you may need to create migration files first.

```bash
docker compose exec web python manage.py makemigrations
```

### Modifying dependencies (uv)

While developing, you can add or remove a dependency by running:

```bash
docker compose exec web uv <add/remove> <package_name>
```

To add or remove a development dependency:

```bash
docker compose exec web uv <add/remove> --group dev <package_name>
```

### Creating a new app

To create a new app (section), first create a directory with the desired app/section name.

```bash
docker compose exec web mkdir pages/<app_name>
```

Then use Django's utility command to create an app and the required files.

```bash
docker compose exec web python manage.py startapp <app_name> pages/<app_name>
```

After creating the app, complete the following steps:

- Add `pages.<app_name>` to `core/settings/base.py` *installed_apps* list
- Rename the app name to `pages.<app_name>` in `pages/<app_name>/app.py`
- Create a `pages/<app_name>/urls.py` file for the app's URLs
- Include the app's URLs in `core/urls.py` (like other apps)
- If needed, create `templates/<app_name>` directory within the app directory for templates
- If needed, create `static/<app_name>` directory within the app directory for static files

### Clearing old containers/images

If you need to reset your Docker environment and start fresh, you can remove the containers and images:

```bash
docker compose down --rmi
```

## Project structure

```text
swedish-pathogens-portal/
├── core/                     # Django project configuration (settings, root URLs, WSGI/ASGI, etc.)
├── pages/                    # Django apps that implement the site’s public-facing pages
├── utils/                    # Shared helper code used across the project
├── doc/
│   └── architecture/
│       └── decisions/        # Architecture Decision Records (ADRs)
├── .github/                  # GitHub workflows and repository configuration
├── .adr-dir                  # ADR tool configuration/metadata
├── Dockerfile                # Instructions for how the Docker image is built
├── compose.yaml              # Definition of Docker Compose services for local development
├── manage.py                 # Django command-line entry point (runserver, migrate, etc.)
├── pyproject.toml            # Project configuration and dependency declarations (used by uv)
├── uv.lock                   # Locked, exact dependency versions for reproducible installs
├── .env.example              # Example environment variables for local development
├── .python-version           # Python version hint for uv / pyenv / other version managers
├── prod-entrypoint.sh        # Script run when the app starts in production (migrations, start server)
└── README.md                 # This file, project documentation
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
