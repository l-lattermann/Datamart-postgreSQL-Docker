# Airbnb Data Mart – PostgreSQL Database Project

This repository contains a fully containerized PostgreSQL data mart implementing an Airbnb-style booking platform. It was developed as part of the IU International University course **Project: Build a Data Mart in SQL**.

The project demonstrates the complete development workflow of a relational database system, including schema design, automated deployment, realistic data generation, testing, and reproducible execution.

## Features

- 21 normalized relational database tables
- PostgreSQL-based schema with primary keys, foreign keys, constraints, indexes, enums, and cascading rules
- Docker-based deployment
- Automated environment setup and teardown
- Python-based seed data generator
- Configurable dummy data generation
- Automated SQL execution
- Unit and integration tests using Pytest
- Business workflow validation across multiple entities
- Reproducible local development environment

## Project Structure

```
.
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt            # Python dependencies
├── example.env                 # Example configuration
├── scripts
│   ├── setup.sh                # Complete environment setup
│   ├── teardown.sh             # Remove environment
│   └── check_db_connection.py
├── src
│   ├── config.py
│   ├── main.py
│   ├── db
│   │   ├── connection.py
│   │   ├── gen_seed_data.py
│   │   ├── run_sql_files.py
│   │   ├── sql_repo.py
│   │   ├── data_lists.py
│   │   └── utils
│   ├── sql
│   │   ├── 01_schema.sql
│   │   └── 02_seed.sql
│   └── utils
└── tests
    ├── integration
    │   └── test_business_logic.py
    └── unit
        ├── test_connection.py
        └── test_gen_seed_data.py
```

---

# Database Overview

The implemented database models the complete booking workflow of an Airbnb-like platform.

Supported functionality includes:

- User account management
- Host and guest profiles
- Address management
- Accommodation management
- Amenities
- Accommodation images
- Booking calendar
- Reservations
- Payments
- Credit cards
- PayPal accounts
- Reviews
- Review images
- Messaging
- Notifications
- Host payouts

The schema follows normalization principles to minimize redundancy while maintaining referential integrity.

---

# Requirements

- macOS or Linux
- Docker
- Colima (macOS)
- Homebrew (macOS)
- Python 3.11+
- Git

---

# Installation

## Clone the repository

```bash
git clone https://github.com/l-lattermann/Datamart-postgreSQL-Docker.git

cd Datamart-postgreSQL-Docker-AWS
```

## Setup the complete environment

```bash
./scripts/setup.sh
```

The setup script automatically

- installs missing dependencies
- starts Colima
- launches the PostgreSQL container
- creates the Python virtual environment
- installs all Python dependencies
- creates the database schema
- generates dummy data
- verifies the database connection

---

# Generate Seed Data

The seed generator can be executed independently.

```bash
python -m src.db.gen_seed_data
```

Generated entities include:

- Accounts
- Addresses
- Hosts
- Guests
- Accommodations
- Amenities
- Accommodation images
- Booking calendar
- Bookings
- Payment methods
- Credit cards
- PayPal accounts
- Reviews
- Review images
- Messages
- Notifications
- Host payouts

Generation parameters can be adjusted centrally in the project configuration.

---

# Running Tests

Execute all tests:

```bash
pytest
```

Execute only unit tests:

```bash
pytest tests/unit
```

Execute integration tests:

```bash
pytest tests/integration
```

The test suite validates:

- Database connectivity
- Schema creation
- Data generation
- Constraints
- Foreign keys
- Business workflows
- Booking process
- Payment workflow
- Reviews
- Messaging
- Notifications
- Payout processing

---

# Teardown

Remove the complete environment:

```bash
./scripts/teardown.sh
```

This removes

- Docker containers
- Docker volumes
- Colima virtual machine

allowing a completely clean recreation of the environment.

---

# Technologies

- PostgreSQL
- Docker
- Colima
- Python
- SQL
- Pytest

---

# Repository Status

This project is feature complete for the university assignment and serves as a reference implementation of a normalized relational database system with automated deployment, data generation, and testing.