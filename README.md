# Badelha: Swap & Sell Platform (MVP)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Baddelha (بَدِّلها) is an innovative Swap & Sell platform designed to revive the culture of bartering. This repository contains the complete Backend MVP, engineered as a Modular Monolith using FastAPI and PostgreSQL. It features a robust Swap Engine for matching items, secure JWT authentication, and real-time live chat capabilities powered by WebSockets to facilitate seamless user negotiations. Fully Dockerized and covered by a comprehensive pytest suite.

## Completed MVP Steps

Based on the original project idea, the backend environment has been fully configured and functionally developed:

- **Project Setup & Architecture:** strictly modular monolith structure (`users`, `items`, `swaps`, `chat`, `admin`) scaling with FastAPI, SQLAlchemy, and Alembic.
- **Users & Auth Module:** Secure JWT-based authentications, user registration, profile management, and a user-to-user rating and review system.
- **Items & Comments Module:** Full CRUD for items and associated comments. Advanced filtering querying by `city`, `category`, and `transaction_type` with **local file upload handling** for item images mapped to an interactive static file host (`/uploads`).
- **Swap Engine Module:** Built the core business logic allowing users to submit swap offers, and letting item owners securely accept or reject these proposals.
- **Real-time Chat Module:** WebSockets initialized for live instant messaging conditionally unlocking once a swap is accepted, mapping persistence asynchronously back into an SQL history table.
- **Admin Dashboard Module:** Setup admin-secured endpoints protecting generalized systemic statistic tracking and action flags to ban rogue users globally.

## Tech Stack

- **Framework:** FastAPI (Python 3.x)
- **Database:** PostgreSQL (with Docker) / SQLite (Fallback)
- **Cache & Services:** Redis (with Docker)
- **ORM:** SQLAlchemy coupled with Alembic for dynamic database migrations
- **Authentication:** Passlib (Bcrypt) & Python-JOSE (Valid JWT implementation)
- **Real-time Connections:** WebSockets

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.x](https://www.python.org/downloads/) (if running manually)

### Environment Configuration

Before starting the project, you need to configure your environment variables.
Copy the provided `.env.example` file to `.env`:

```bash
cp .env.example .env
```

_(Feel free to adjust the variables inside `.env` to match your local setup)._

---

### Method 1: Running with Docker Compose (Recommended)

The easiest way to get the entire stack (API, PostgreSQL, Redis) up and running is via Docker Compose.

1. **Build and start the containers:**

   ```bash
   docker compose up -d --build
   ```

2. **Verify services are running:**

   ```bash
   docker ps
   ```

3. **Interact via the Swagger UI:**
   Open your browser and navigate to the automated API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

4. **To stop the services:**
   ```bash
   docker compose down
   ```

---

### Method 2: Manual Local Setup

If you prefer to run the FastAPI application manually outside of Docker, follow these steps:

1. **Start the backing services (PostgreSQL & Redis) via Docker:**

   ```bash
   docker compose up -d db redis
   ```

2. **Activate the local Virtual Environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows use: .venv\Scripts\activate
   ```

3. **Install all necessary Python Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations to scaffold SQL tables:**
   _(Ensure PYTHONPATH is bound properly on Linux platforms)_

   ```bash
   export PYTHONPATH=$PWD
   alembic upgrade head
   ```

5. **Launch the ASGI Server via Uvicorn:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Testing

To run the full test suite inside the isolated Docker environment, use the following `docker compose` command:

```bash
docker compose --profile test run --rm api-test
```

You can also pass arguments directly to `pytest`, for example, to see verbose output or run a specific file:

```bash
docker compose --profile test run --rm api-test -v tests/api/test_users.py
```

_Note: Make sure your `.env` contains testing configurations like `TEST_DATABASE_URL` pointing to the `db` service._

---

## Live API Endpoints Structure

_(Retrieved actively from FastAPI routes mapping)_

### Generic App Routes

- `GET /` : Health check/root endpoint.

### Users & Authentication (`/users`)

- `POST /users/register` : Register a new user account.
- `POST /users/login` : Authenticate identity and fetch an active Bearer JWT Token.
- `GET /users/profile` : Output authorized user profile schemas.
- `PUT /users/profile` : Allow users to actively change profiles/password combinations.
- `POST /users/review` : Allow users to leave integer ratings & text reviews on other profiles.

### Items & Interactive Comments (`/items`)

- `POST /items/` : Broadcast a product/item availability.
- `POST /items/{item_id}/image` : Multipart file upload endpoint mapping images locally to the `.uploads/` directory.
- `GET /items/` : Returns a list of all publicly listed products featuring pagination and URL queries filtering (category, city, transaction_type).
- `GET /items/{item_id}` : Gather item specificity and deeply nested SQL properties (Including nested active comments).
- `PUT /items/{item_id}` : Update listed descriptions, titles, pricing, etc.
- `DELETE /items/{item_id}` : Strip item out of persistence contexts completely.
- `GET /items/{item_id}/comments` : Find localized product discussions.
- `POST /items/{item_id}/comments` : Generate a localized comment pointing to an item.
- `PUT /items/{item_id}/comments/{comment_id}` : Edit a published comment.
- `DELETE /items/{item_id}/comments/{comment_id}` : Remove a localized comment payload.

### The Swap Engine (`/swaps`)

- `POST /swaps/request` : Connect a mutually interested Item A corresponding against Item B pushing state to `"Pending"`.
- `PUT /swaps/{swap_id}/accept` : Acknowledge targeted intent pushing state sequentially to `"Accepted"` which actively invokes the initiation of `ChatRooms`.
- `PUT /swaps/{swap_id}/reject` : Decline swap intent securely.
- `GET /swaps/my-requests` : Read inbound vs outbound active queries linked directly mapping onto active User ID dependencies.

### Websocket & Chat Engine (`/chat`)

- `WS /ws/chat/{room_id}` : Persistent asynchronous dual-way TCP socket transferring chat contexts real-time across connected authenticated accounts.
- `GET /chat/history/{room_id}` : Fetch historical messages serialized by accurate synchronized datetimes.

### Admin Tools & Dashboards (`/admin`)

- `GET /admin/stats` : Returns cumulative platform statistics containing User metric numbers, items generated, and aggregated trade conversions.
- `PUT /admin/users/{user_id}/ban` : Forces the `is_active` parameter boolean to swap offline rendering accounts inaccessible platform-wide.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
