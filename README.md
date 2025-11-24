# Swedish Pathogens Portal

***WIP repository for Swedish Pathogens Portal 2.0***

At this time, the source code for the Swedish Pathogens Portal and more information about it can be found in the [pathogens-portal repository](https://github.com/ScilifelabDataCentre/pathogens-portal).

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
├── Dockerfile                # Instructions (for docker) on how the Docker image should be built
├── compose.yaml              # Definition of Docker Compose services for local development
├── manage.py                 # Django command-line entry point (runserver, migrate, etc.)
├── pyproject.toml            # Project configuration and dependency declarations (used by uv)
├── uv.lock                   # Locked, exact dependency versions for reproducible installs
├── .env.example              # Example environment variables for local development
├── .python-version           # Python version hint for uv / pyenv / other version managers
├── prod-entrypoint.sh        # Script run when the app starts in production (migrations, start server)
└── README.md                 # This file, project documentation
```

## Contributing

You should have `git` and `docker` installed before running the following steps.

### Clone the repository

Open a terminal window, go to the directory where you want to clone the repository and run

```bash
git clone git@github.com:ScilifelabDataCentre/swedish-pathogens-portal.git
```

**NOTE:** The following instructions assume you are in the project's root

### Create `.env` file

We need a `.env` file for the application, for local development we can just make a copy of `.env.example`

```bash
cp .env.example .env
```

### Start the application

To start the application, run the below command.

```bash
docker compose up
```

If the command ran successfully, open a browser and visit `http://localhost:8000`.

### Running tests

***WIP, this is a placeholder and may need to be edited as tests are added.***

Run the test suite with:

```bash
docker compose exec web python manage.py test
```

If you are running the project locally without Docker:

```bash
uv run python manage.py test
```

### To clear old container/images

If you need to reset your Docker environment and start fresh, you can remove the containers and images:

```bash
docker compose down --rmi
```

### Run migrations

To test pages that pull data from the database, Django migrations need to be run:

```bash
docker compose exec web python manage.py migrate
```

### Make migrations

For new apps and models, you may need to create migration files first.

```bash
docker compose exec web python manage.py makemigrations
```

### Creating new app

To create a new app (section), first create a directory with the desired app/section name.

```bash
docker compose exec web mkdir pages/<app_name>
```

Then use Django's utility command to create an app and the required files

```bash
docker compose exec web python manage.py startapp <app_name> pages/<app_name>
```

After creating the app, the following steps should be completed

- Add `pages.<app_name>` to `core/settings/base.py` *installed_apps* list
- Rename app name to `pages.<app_name>` in `pages/<app_name>/app.py`
- Create `pages/<app_name>/urls.py` file for the app's urls
- Then include the app's URLs in `core/urls.py` (like other apps)
- If needed, create `templates/<app_name>` directory within the app directory for templates
- If needed, create `static/<app_name>` directory within the app directory for static files

### Modifying dependencies with UV

While developing, you can add or remove a dependency by running:

```bash
docker compose exec web uv <add/remove> <package_name>
```

To add or remove a development dependency:

```bash
docker compose exec web uv <add/remove> --group dev <package_name>
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
