# URL Shortener System Design

**Project Link:** [View Project](https://github.com/QweciKuranchie/URL-Shortener-System-Design.git)

**Author:** Richard Nuhu  
**Email:** nuhurichard47@gmail.com

---

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_kqswhxb2)

## Project Overview

### What we're building and why

In this project, I'm building A URL shortener, so that I can converts long URLs into short codes and redirects users to the same destination using the short URL generated.

## Setting Up the Environment

### Environment setup goals

In this step, I'm setting up the project folder, IDE, and install Docker Desktop  so that I can start to work on the project.

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_qj4lc3tb)

### The three core services

The three services are. Python Flask API, Postgres Database and Redis.The first accept long URLs and retun a short code.The second stores the long URLs. The third provides caching for fast lookups.

## Designing the System Architecture

### Architecture design goals

In this step, I'm creating the infrastructure files so that I can define how the services are built, connected, and started.

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_pnungqem)

### Services defined in docker-compose.yml

The three services are Flask API (named web in the compose file), the PostgreSQL database (named db), and the Redis cache (named redis). Each one handles the python API Server, postgres database for storing URL mapping permenatly and redis cahe for fast lookups respectively.

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_ymp8agg2)

### Infrastructure file deep dive

I chose Dockerfile Its role is a recipe for building a container image. It starts from a slim Python 3.12 base image, installs the packages from requirements.txt, copies  the application code into the image, and runs app.py when the container starts.

## Building the URL Shortener Logic

### Application logic goals

In this step, I'm writing the Python file (app.py) so that I can convert long URLs into short codes, and redirecting the short codes back to the original URL. 

### The URL shortening flow

When a long URL hits /shorten, the app first grabs the long URL and stores the URL to the database then the database assigns an auto-incrementing ID, encodes it, caches it, the and finally returns a short URL.

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_seusouy2)

### Handling redirect lookups

When someone visits a short URL, the app first checks redis if it's cached and If that misses, it falls back to the database if it's found it then caches for next time and if it's not found it return an error.

## Launching and Verifying the System

### Launch goals

In this step, I'm starting my DockerFile so that I can confirm the Flask API responds to a health check and verify PostgreSQL and Redis are connected through their logs.

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_3w4aoken)

### Health endpoint response

When I ran curl http://localhost:5000/health I saw {"status":"healthy"}

## Testing and Observing the System

### Testing goals

In this step, I'm testing the URL shortening and URL redirection so that I can observe the HTTP status code and caching layer in real time.

### Redis cache flush behavior

After flushing Redis, the app had to query the postgres database instead of skipping the database.

## Implementing Rate Limiting with Redis

![Image](https://nextwork.ai/richard-nuhu/uploads/02a35a5b-1d8b-43ee-9982-6ceef44145e5_i71om2um)

### Why Redis excels at rate limiting

In this project extension, Redis is better for rate limiting because Redis INCR is atomic, meaning it is thread-safe even under concurrent requests. Redis also supports key expiration (TTL), so you can increment a counter per IP and auto-reset it every 60 seconds without any cleanup jobs.

## Reflections and Key Takeaways

### Tools and concepts learned

The key tools I used include Docker containers (web, db, redis) running locally, Docker volume (postgres_data) storing your database on disk, Docker images cached locally (approximately 500MB total disk space), Key concepts I learnt include building a multi-service distributed system with a Python API, PostgreSQL database, and Redis cache that shortens URLs and redirects users, apply the cache-aside pattern and explain 301 vs 302 redirect trade-offs the way interviewers expect, use Docker Compose to orchestrate containers with health checks, networking, and startup dependencies.

### Time and challenges

This project took me approximately 3 hours. The most challenging part was The YAML file Indentation, it was challenging because a single accidental tab character or two missing spaces under depends_on entirely shifts the structural context. Because of this, parsers generate generic scanner errors (like mapping values are not allowed) that don't tell you what is wrong, only where the parser gave up.
The Takeaway: Mastering orchestration requires learning to treat configuration files with the exact same syntactic precision as python or bash scripts.

### Final thoughts

I did this project today to learn how to design, build and run a multi-service distributed system(a website, a database, and a fast memory cache) together in small, safe packages called containers using Docker Compose, making sure they start up in the right order and can talk to each other without crashing. Another skill I want to learn is  cloud deployment, which means taking these containers off my computer and putting them onto a cloud service like AWS so anyone in the world can open and use my website.

---
