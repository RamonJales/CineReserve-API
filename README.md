# CineReserve-API
The CineReserve API is a high-performance, scalable RESTful backend designed to manage the complexities of modern cinema operations
# CineReserve API

The CineReserve API is a high-performance, scalable RESTful backend designed to manage the complexities of modern cinema operations (specifically designed for *Cinépolis Natal*). Built with Python, Django REST Framework, PostgreSQL, and Redis, it handles high-concurrency ticket reservations with temporary distributed locks.

## Technologies Used
* **Language:** Python 3.12
* **Framework:** Django 5 & Django REST Framework (DRF)
* **Database:** PostgreSQL 16
* **Cache & Locks:** Redis 7
* **Task Queue:** Celery *(Upcoming)*
* **Containerization:** Docker & Docker Compose
* **Dependency Management:** Poetry
* **CI/CD:** GitHub Actions (Ruff, Pytest, Coverage)

---

## How to Run the Project (Locally)

This project uses Docker to provide a seamless "plug-and-play" experience. You do not need to install Python, PostgreSQL, or Redis on your local machine—Docker handles everything.

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/) installed and running.
* [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Step 1: Clone the repository
```bash
$ git clone [https://github.com/your-username/cine-reserve-api.git](https://github.com/your-username/cine-reserve-api.git)

$ cd cine-reserve-api
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory. You can copy the following configurations:
Snippet de código

```
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
POSTGRES_DB=cinereserve
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgres://postgres:postgres@db:5432/cinereserve
REDIS_URL=redis://redis:6379/0
```

### Step 3: Build and Run the Containers

Start the API, Database, and Redis cache in detached mode:

```bash
$ docker-compose up --build -d
```

### Step 4: Run Database Migrations

Apply the initial migrations to construct the PostgreSQL schema:

```bash
docker-compose exec web python manage.py migrate
```

### Step 5: Create a Superuser (Optional but recommended)

Create an admin account to access the Django Admin panel:

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 6: Access the API

- Base API URL: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

### Running Tests

To run the automated test suite (Pytest) and check coverage inside the container:

```bash
docker-compose exec web pytest --cov
```

### Code Quality (Linting & Formatting)

We use ruff to maintain strict code quality:

```bash
$ docker-compose exec web ruff check .
$ docker-compose exec web ruff format .
```
