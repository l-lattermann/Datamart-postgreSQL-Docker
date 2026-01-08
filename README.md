# Airbnb Data Mart – Database Project (Still in Development)

This project implements a fully containerized SQL-based data mart for an Airbnb-style booking platform, developed as part of the IU “Project Build a Data Mart in SQL” course.  
The goal is to create a normalized, scalable, and testable relational database that models the Airbnb use case: users, hosts, apartments, bookings, payments, reviews, and supporting domain entities.

This repository includes:
- A complete ERM-based schema (20+ entities)
- Normalized SQL tables with constraints, indexes, and functions
- Containerized PostgreSQL environment using Docker + Colima
- Automated data seeding (dummy data generation)
- Python tooling for schema introspection, seed generation, and tests
- Full pytest setup with mocked unit tests
- Documentation and SQL scripts for all IU phases


## 1. Use Case Overview (Airbnb Scenario)

The database models the core Airbnb business logic:

- Hosts list apartments or rooms, upload pictures, manage prices and availability.
- Guests browse listings, make bookings, leave ratings, maintain profiles.
- Airbnb processes payments: guests pay Airbnb; hosts receive payouts after check-in.
- Both parties maintain reviews and trust-related information.
- Payments include credit cards and PayPal.

Core system goals:
- Store user profiles (hosts & guests)
- Store accommodations, pictures, availability
- Handle bookings with normalized relations
- Manage payments & payment methods
- Support reporting & analytics
- Maintain normalization and referential integrity



## 4. Setup & Execution

**IMPORTANT:** Execute steps in the correct order.
### 0. Install homebrew

Install homebrew from the official website:
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### Clone Repository

Clone the project locally:
```zsh
git clone https://github.com/l-lattermann/Datamart-postgreSQL-Docker-AWS.git
cd Datamart-postgreSQL-Docker-AWS
```

### 1. Start Database (Docker + Colima)
Run:
```zsh
./scripts/docker_setup.sh
```
This downloads all required dependencies via homebrew and boots the PostgreSQL container and exposes the database locally.

### 2. Apply Schema and SQL Files
Execute:
```zsh
python -m src.db.gen_seed_data
```

This generates:
- Accounts  
- Hosts & guests  
- Apartments  
- Bookings  
- Payment methods  
- Credit cards  
- PayPal IDs  
- Reviews  
- All dependent domain entities  

## 5. Testing
Run the full suite:
```zsh
pytest
```
Tests include:
- Connection tests  
- Schema introspection  

## 6. Notes & Development Status
This project is still in active development.  
Some modules, test cases, random data generators, and SQL validation routines are work in progress.  
Expect continuous improvements to structure, naming, and validation logic.

## 7. To Be Continued…
More documentation, diagrams, automated checks, and additional seed data helpers will be added soon.