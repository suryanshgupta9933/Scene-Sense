# Scene-Sense

A local, privacy-first visual search engine that lets you upload images, store CLIP embeddings, and search them using natural language. The backend is built with FastAPI + PostgreSQL + pgvector, and the frontend is powered by a modern React interface.

### Demo Video

https://github.com/<your-username>/<your-repo>/assets/<asset-id>

## Features

* Upload images and store them efficiently on local storage
* Automatic CLIP embedding generation using a remote or local inference server
* Natural‑language semantic search over your entire image library
* Automatic TTL expiry for uploaded files
* Fully local: your files never leave your machine or home network
* Supports large external storage volumes (e.g., /mnt/FourTB)

## System Architecture

Scene‑Sense is split into three components:

### 1. **Frontend (React / Vite)**

* Provides UI for uploading images, browsing, and searching
* Communicates with the backend through REST endpoints
* Configurable API base URL via `.env`

### 2. **Backend (FastAPI)**

Responsible for:

* File uploads
* Generating storage paths
* Storing metadata (filename, path, user, expiry)
* CLIP embedding generation through remote inference server
* Semantic search via pgvector
* Managing TTL deletion background tasks

### 3. **Storage Layer**

* Controlled by the environment variable `STORAGE_PATH`
* Example: `/mnt/FourTB/Scene-Sense-Storage/`

The backend **never stores files inside the repo**; everything goes into the configured storage directory.

## Project Layout

```
Scene-Sense/
├── backend
│   ├── api
│   │   ├── routes_admin.py
│   │   ├── routes_auth.py
│   │   ├── routes_cleanup.py
│   │   ├── routes_search.py
│   │   └── routes_upload.py
│   ├── config.py
│   ├── core
│   │   ├── auth.py
│   │   ├── job_queue.py
│   │   ├── security.py
│   │   └── settings.py
│   ├── db
│   │   ├── init_db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── session.py
│   ├── logs
│   ├── main.py
│   ├── ml
│   │   ├── embeddings_clip.py
│   │   └── utils.py
│   ├── requirements.txt
│   ├── storage
│   │   ├── cleanup.py
│   │   ├── local_store.py
│   │   ├── logger.py
│   └── utils
│       ├── file_hash.py
│       └── time_utils.py
├── docker-compose.yml
├── Dockerfile.app
├── Dockerfile.routes
├── frontend
│   ├── package.json
│   ├── package-lock.json
│   ├── public
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   └── src
│       ├── api
│       │   └── auth.js
│       ├── api.js
│       ├── App.css
│       ├── App.jsx
│       ├── App.test.js
│       ├── assets
│       │   └── bg.jpg
│       ├── components
│       │   ├── LoginForm.jsx
│       │   ├── SignupForm.jsx
│       │   ├── UserDashboard.css
│       │   └── UserDashboard.jsx
│       ├── contexts
│       │   └── AuthContext.jsx
│       ├── index.css
│       ├── index.js
│       ├── logo.svg
│       ├── reportWebVitals.js
│       └── setupTests.js
├── LICENSE
├── README.md
└── requirements.txt
```


## Environment Configuration

Create `backend/.env`:

```
DATABASE_URL=postgresql://scenesense:supersecurepassword@192.168.0.75:5432/scenesense_db
JWT_SECRET=your_secret
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

STORAGE_PATH=/mnt/FourTB/Scene-Sense-Storage/storage

CLIP_SERVER_URL=http://192.168.0.75:9000
CLIP_MODEL=openai/clip-vit-base-patch32
CLIP_EMBED_DIM=512
```

## Database Setup

This project uses **PostgreSQL + pgvector**.

### Install pgvector

```
psql -d scenesense_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Run migrations or let SQLAlchemy auto‑create tables

Backend creates tables automatically if missing.


## Running the Backend

```
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8020
```

## Running the Frontend

```
cd frontend
npm install
HOST=0.0.0.0 npm start
```


## Storage Behavior

Scene‑Sense stores files like this on `192.168.0.75`:

```
/mnt/FourTB/Scene-Sense-Storage/storage/
   └── <uuid>/
         └── filename.png
```

A record is inserted into PostgreSQL:

```
id, filename, filepath, embedding, created_at, expires_at
```

## Search Flow

1. User enters text
2. Backend sends it to CLIP inference server → obtains embedding
3. Embedding is compared against stored vectors using `pgvector <->` distance
4. Results returned ordered by semantic relevance

---

## Troubleshooting

### Files going to the wrong directory

Check:

* `.env` value of `STORAGE_PATH`
* No trailing slashes issues
* Backend was restarted after changing env

### pgvector error: `type "vector" does not exist`

Run:

```
CREATE EXTENSION vector;
```


## Future Improvements

* Admin Dashboard (currently only partial and available through backend)
* Multi‑user accounts & roles
* Folder‑level organization & tagging
* Video embedding support

---

## License

MIT
