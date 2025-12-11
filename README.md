All Dockerfiles and application logic are stored here.  
Configuration, Kubernetes manifests, and deployment files have been moved  
to a separate repository as required.

## Application Overview

This project consists of three main services: a frontend, a backend, and a broadcaster.

### Frontend (Flask)
The frontend is a simple Flask web application that:
- Displays the list of todos retrieved from the backend
- Allows users to create new todos and update their status
- Serves an image that is cached locally and refreshed when outdated
- Communicates with the backend through environment-configured URLs

It uses server-side rendering (Jinja templates) and handles form submissions for creating and updating todos.

---

### Backend (Flask + PostgreSQL + NATS)
The backend provides a REST API for managing todos.  
Core features include:
- Storing todos in a PostgreSQL database
- Validating content length
- Updating the "done" status of todos
- Exposing health endpoints for Kubernetes probes
- Publishing events to NATS whenever a todo is created or updated

The backend runs an asynchronous event loop in a background thread so it can publish messages to NATS while still handling HTTP requests synchronously.

---

### Broadcaster (Python + NATS + Webhooks)
The broadcaster subscribes to the `todo.events` topic in NATS and:
- Receives todo events from the backend
- Formats them into readable messages
- Sends them to an external webhook (e.g. Discord, Slack, API endpoint)
- Supports a "log_only" mode for staging environments

It is designed so that only one replica processes each message (via a NATS queue group).

---

Together, these services form a small event-driven TODO system where actions in the backend trigger real-time notifications through the broadcaster.
