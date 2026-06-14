# Deploy RegIntel free on Oracle Cloud (Always Free)

This gets RegIntel **live 24/7 for $0** on Oracle Cloud's **Always Free** ARM VM
(up to 4 OCPU / 24 GB RAM — plenty for Neo4j + Qdrant + the embedding model).
Same Docker Compose stack as local, just on a free public server you can put on a resume.

> Why Oracle and not AWS free tier? AWS free tier is `t2.micro` (1 GB RAM) — RegIntel
> needs ~6–8 GB and would crash. Oracle's Always Free ARM gives you 24 GB for free, forever.

---

## What you'll need

| Item | Why |
|------|-----|
| [Oracle Cloud account](https://www.oracle.com/cloud/free/) | Hosting (free tier; card needed for identity check, not charged) |
| [Groq API key](https://console.groq.com) (free) | Powers Query / agents |
| GitHub repo with this code | The server clones it |
| An SSH key pair | To log into the server |

**Two Oracle gotchas this guide handles for you:**
1. **ARM "out of capacity"** — the free ARM shape is popular and sometimes unavailable. Retry, or switch Availability Domain / region.
2. **Two firewalls** — Oracle blocks ports at *both* the cloud Security List *and* inside the OS (iptables). You must open ports in **both** or the site won't load.

---

## Step 1 — Create the SSH key (on your Windows laptop)

```powershell
# Creates regintel-key (private) and regintel-key.pub (public)
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\regintel-key" -N '""'
# Show the PUBLIC key — copy this whole line for Step 2
Get-Content "$env:USERPROFILE\.ssh\regintel-key.pub"
```

Keep the private key (`regintel-key`, no `.pub`) safe — never share it.

---

## Step 2 — Create the free VM (Oracle Console)

1. Sign in → **Menu → Compute → Instances → Create instance**
2. **Name:** `regintel-demo`
3. **Image and shape → Edit:**
   - **Image:** Canonical **Ubuntu 22.04** (pick the **aarch64 / ARM** build)
   - **Shape → Ampere → `VM.Standard.A1.Flex`** → set **4 OCPUs, 24 GB** (all free-tier)
   - *If you get "Out of capacity":* lower to **2 OCPU / 12 GB**, change the **Availability Domain** dropdown, or try a different home region. Retry — capacity frees up.
4. **Add SSH keys → Paste public keys** → paste the `regintel-key.pub` line from Step 1
5. **Networking:** leave defaults (it creates a VCN). Make sure **"Assign a public IPv4 address"** is on.
6. **Create.** When it's `RUNNING`, copy the **Public IP address**.

---

## Step 3 — Open ports at the cloud layer (Security List)

1. On the instance page → click the **subnet** link → click the **Default Security List**
2. **Add Ingress Rules** (Source CIDR `0.0.0.0/0`, IP Protocol TCP), one per port:

| Port | Purpose |
|------|---------|
| 3000 | Web app |
| 8000 | API (optional) |

(Port 22 for SSH is already open by default.)

---

## Step 4 — Connect via SSH

```powershell
ssh -i "$env:USERPROFILE\.ssh\regintel-key" ubuntu@YOUR_PUBLIC_IP
```

> Ubuntu's user is `ubuntu`. If you chose an Oracle Linux image it's `opc`.

---

## Step 5 — Open ports inside the OS (the gotcha)

Oracle's Ubuntu image blocks all inbound ports except 22 with iptables. Open 3000/8000:

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save
```

---

## Step 6 — Install Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
newgrp docker   # apply group without re-login
```

---

## Step 7 — Clone, configure, launch

```bash
git clone https://github.com/harshit21-shah/RegIntel.git
cd RegIntel
cp .env.aws.example .env
nano .env
```

In `.env`, set at minimum (replace `YOUR_PUBLIC_IP`):

```env
APP_BASE_URL=http://YOUR_PUBLIC_IP:3000
CORS_ORIGINS=http://YOUR_PUBLIC_IP:3000
JWT_SECRET_KEY=paste-your-generated-secret
GROQ_API_KEY=gsk_...
POSTGRES_PASSWORD=choose-a-strong-password
NEO4J_PASSWORD=choose-a-strong-password
```

Save (`Ctrl+O`, `Enter`, `Ctrl+X`), then:

```bash
# Build + start the stack (first build ~10–15 min on ARM)
docker compose -f docker-compose.aws.yml up -d --build

# Seed the demo (Title 21 vertical) + embed corpus (~5–10 min)
docker compose -f docker-compose.aws.yml --profile bootstrap run --rm bootstrap
```

---

## Step 8 — Open your live demo

| URL | What |
|-----|------|
| `http://YOUR_PUBLIC_IP:3000` | Web app |
| `http://YOUR_PUBLIC_IP:8000/docs` | API Swagger |

**Login:** `admin@regintel.dev` / `RegIntel-Demo-2025!`

The dashboard shows the seeded **Title 21 added-sugars** change + verified brief.
Walkthrough: Dashboard → Changes (run triage → graph hop-path) → Briefs (citations) → Query.

---

## Verify / operate

```bash
docker compose -f docker-compose.aws.yml ps          # all running/healthy?
docker compose -f docker-compose.aws.yml logs -f api  # API logs
docker compose -f docker-compose.aws.yml logs -f web  # web logs
docker compose -f docker-compose.aws.yml up -d --build # restart after .env change
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Page won't load on :3000 | Opened the port in **both** Security List (Step 3) **and** iptables (Step 5)? |
| "Out of capacity" creating VM | Lower to 2 OCPU/12 GB, switch Availability Domain, or retry later |
| Can't SSH | Used the private key (no `.pub`) and user `ubuntu`? Port 22 open? |
| Login fails | `docker compose ... logs api` — API must be healthy |
| Query LOW_CONFIDENCE | Re-run the bootstrap step (embeds the corpus) |
| Out of memory | Give the VM more OCPU/RAM (free tier allows up to 4/24) |

---

## Resume line (after deploy)

> Deployed a GraphRAG regulatory-intelligence platform (FastAPI, Neo4j, Qdrant, Postgres,
> Next.js) on a free-tier ARM cloud VM via Docker Compose — public demo at `http://x.x.x.x:3000`.
