CREATE CONSTRAINT clause_id_unique IF NOT EXISTS FOR (c:Clause) REQUIRE c.clause_id IS UNIQUE;
CREATE CONSTRAINT regulation_id_unique IF NOT EXISTS FOR (r:Regulation) REQUIRE r.regulation_id IS UNIQUE;
CREATE CONSTRAINT client_id_unique IF NOT EXISTS FOR (cp:ClientProfile) REQUIRE cp.client_id IS UNIQUE;
CREATE CONSTRAINT naics_unique IF NOT EXISTS FOR (bc:BusinessCategory) REQUIRE bc.naics_code IS UNIQUE;
CREATE INDEX clause_effective_date IF NOT EXISTS FOR (c:Clause) ON (c.effective_date);
