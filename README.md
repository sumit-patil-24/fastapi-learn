# fastapi-learn

## This checkpoint contains the containerization of application and docker hygine

By the end of this checkpoint, you will understand:
    - “What files should and should not go inside a Docker image, and why.”

This protects you from:
    - leaking secrets
    - bloated images
    - slow pipelines

## 1️⃣ Add .dockerignore:
Create a file named .dockerignore with:
```
__pycache__/
*.pyc
.env
.venv/
venv/
.git
.gitignore
README.md
```

Why this matters:
    - Docker sends build context → smaller is faster
    - .git should never be inside images
    - .env must never leak

