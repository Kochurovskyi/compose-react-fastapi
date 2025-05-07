# Fibonacci Calculator Application

A multi-container application for calculating Fibonacci numbers. This project demonstrates a full-stack application with multiple services working together through Docker containerization.

## Architecture

The application consists of multiple services:

- **Client**: React frontend
- **Server**: FastAPI backend
- **Worker**: Python process for calculating Fibonacci numbers
- **Redis**: In-memory database for storing calculation results
- **PostgreSQL**: Persistent database for storing submitted indices
- **Nginx**: Web server for routing requests between client and server
- **AWS**: deployment infrastructure (Beanstalk, RDS)
- **CI/CD**: GitHub Actions for continuous integration and deployment to AWS

## Features

- Calculate Fibonacci numbers for a given index
- View previously calculated values
- Store calculation history in a persistent database
- Real-time calculation updates using Redis pub/sub

## Technologies Used

- **Frontend**: React.js, React Router
- **Backend**: FastAPI (Python)
- **Databases**: PostgreSQL, Redis
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone this repository
2. Navigate to the project root directory
3. Run the application using Docker Compose:
4. 
```bash
docker-compose up