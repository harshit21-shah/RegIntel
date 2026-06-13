# Deploy RegIntel on AWS (beginner guide)

This guide gets RegIntel **live on AWS in ~30–60 minutes** using **one EC2 server** and Docker — the same stack you run locally, but on a public IP you can put on a resume.

> **Not this guide:** full ECS Fargate + Terraform (production path). Do EC2 first, then graduate to `infra/terraform/` when you're comfortable.

---

## What you'll need

| Item | Why |
|------|-----|
| [AWS account](https://aws.amazon.com/free/) | Hosting |
| Credit card | AWS verifies identity (free tier covers small EC2 for 12 months) |
| [Groq API key](https://console.groq.com) (free) | Powers Query / agents |
| GitHub repo with this code | EC2 clones it |
| ~$30–60/month if left running 24/7 | `t3.large` EC2 (stop instance when not demoing to save money) |

You do **not** need Terraform or AWS CLI on your laptop for this path (AWS Console is enough).

---

## Step 1 — Push code to GitHub

If the project isn't on GitHub yet:

```powershell
cd "d:\AI Engineer\RegIntel"
git init
git add .
git commit -m "chore: initial commit for AWS deploy"
gh repo create RegIntel --private --source=. --push
```

Note your repo URL, e.g. `https://github.com/YOUR_USERNAME/RegIntel.git`.

---

## Step 2 — Create an EC2 instance (AWS Console)

1. Sign in to [AWS Console](https://console.aws.amazon.com/) → region **US East (N. Virginia) / us-east-1**
2. Search **EC2** → **Launch instance**
3. Settings:

| Setting | Value |
|---------|--------|
| Name | `regintel-demo` |
| AMI | **Amazon Linux 2023** |
| Instance type | **t3.large** (2 vCPU, 8 GB — Neo4j + Qdrant need RAM) |
| Key pair | **Create new** → download `.pem` file → keep it safe |
| Storage | 30 GB gp3 |

4. **Network settings** → Edit:

| Rule | Port | Source |
|------|------|--------|
| SSH | 22 | **My IP** (important — don't use 0.0.0.0/0 for SSH) |
| Custom TCP | 3000 | 0.0.0.0/0 (web UI) |
| Custom TCP | 8000 | 0.0.0.0/0 (API docs — optional) |

5. **Launch instance**
6. Copy the **Public IPv4 address** (e.g. `54.123.45.67`)

---

## Step 3 — Connect via SSH

### Windows (PowerShell)

```powershell
# Fix key permissions (first time only)
icacls "C:\Users\YOU\Downloads\regintel-demo.pem" /inheritance:r
icacls "C:\Users\YOU\Downloads\regintel-demo.pem" /grant:r "$($env:USERNAME):(R)"

ssh -i "C:\Users\YOU\Downloads\regintel-demo.pem" ec2-user@YOUR_PUBLIC_IP
```

> Amazon Linux user is `ec2-user`. Ubuntu AMI uses `ubuntu@`.

---

## Step 4 — Install and start RegIntel on the server

On the EC2 shell:

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/RegIntel.git
cd RegIntel

# Create env file
cp .env.aws.example .env
nano .env   # set GROQ_API_KEY, JWT_SECRET_KEY, fix APP_BASE_URL if needed
```

In `.env`, set at minimum:

```env
APP_BASE_URL=http://YOUR_PUBLIC_IP:3000
CORS_ORIGINS=http://YOUR_PUBLIC_IP:3000
JWT_SECRET_KEY=paste-a-long-random-string-here
GROQ_API_KEY=gsk_...
POSTGRES_PASSWORD=choose-a-strong-password
NEO4J_PASSWORD=choose-a-strong-password
```

Then:

```bash
# Install Docker (Amazon Linux)
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
newgrp docker

# Build and start (10–15 min first time)
docker compose -f docker-compose.aws.yml up -d --build

# Seed database + embed corpus (5–10 min)
docker compose -f docker-compose.aws.yml --profile bootstrap run --rm bootstrap
```

---

## Step 5 — Open the app

| URL | Purpose |
|-----|---------|
| `http://YOUR_PUBLIC_IP:3000` | Web app |
| `http://YOUR_PUBLIC_IP:8000/docs` | API Swagger |
| `http://YOUR_PUBLIC_IP:8000/healthz` | Health check |

**Login:** `admin@regintel.dev` / `RegIntel-Demo-2025!`

### What's seeded (the demo story)

The bootstrap seeds a complete **Title 21 food-labeling** vertical so the full flow
is visible immediately — no need to trigger anything first:

- **Change event** — 21 CFR 101.9: added-sugars now a mandatory Nutrition Facts line (compliance by Jan 1, 2026).
- **3 client profiles** — Acme Foods (frozen specialty), Coastal Catch Seafood, Harvest Valley Dairy.
- **Verified brief** — a citation-backed compliance brief for Acme Foods on the dashboard.

Demo walkthrough (≈60s):

1. **Dashboard** → the seeded brief + change appear.
2. **Changes** → open the 101.9 change → run triage → live multi-hop graph traversal surfaces the affected food manufacturers with their hop path.
3. **Briefs** → open the Acme Foods brief → every obligation links back to a verbatim 21 CFR clause citation.
4. **Query** → ask *What is the FDA?* or *added sugars labeling* for live citation-backed retrieval.

---

## Step 6 — Verify it's healthy

On EC2:

```bash
curl -s http://localhost:8000/healthz
curl -s http://localhost:8000/readyz | head -c 500
docker compose -f docker-compose.aws.yml ps
```

All services should be `running` / `healthy`.

---

## Useful commands

```bash
# Logs
docker compose -f docker-compose.aws.yml logs -f api
docker compose -f docker-compose.aws.yml logs -f web

# Restart after .env change
docker compose -f docker-compose.aws.yml up -d --build

# Stop everything (save money)
docker compose -f docker-compose.aws.yml down

# Stop EC2 instance in AWS Console when not using it
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Can't SSH | Security group must allow port 22 from **your** IP |
| Can't open :3000 | Security group must allow port 3000 from 0.0.0.0/0 |
| Login fails | Check `docker compose logs api` — API must be up |
| Query LOW_CONFIDENCE | Re-run bootstrap embed step |
| Out of memory | Use `t3.large` or bigger; check `docker stats` |
| CORS error in browser | `CORS_ORIGINS` must exactly match `http://IP:3000` |

---

## Cost-saving tips

- **Stop** the EC2 instance when not demoing (you only pay storage ~$3/mo)
- Don't leave a `t3.large` running 24/7 unless you need it
- Set a [billing alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) at $20

---

## Resume line (after deploy)

> Deployed RegIntel on **AWS EC2** (Docker Compose): FastAPI, Neo4j, Qdrant, Postgres, Next.js — public demo at `http://x.x.x.x:3000`

---

## Next level (when ready)

1. **Domain + HTTPS** — Route 53 + Application Load Balancer + ACM certificate
2. **Managed databases** — RDS Postgres, Neo4j Aura, Qdrant Cloud
3. **ECS Fargate** — use `infra/terraform/` + GitHub Actions `build.yml` / `deploy-staging.yml`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for the production topology.

---

## Quick checklist

- [ ] GitHub repo pushed
- [ ] EC2 launched (t3.large, ports 22/3000/8000)
- [ ] SSH works
- [ ] `.env` has GROQ_API_KEY + JWT_SECRET_KEY + APP_BASE_URL
- [ ] `docker compose -f docker-compose.aws.yml up -d --build`
- [ ] Bootstrap finished
- [ ] Login + query works in browser
