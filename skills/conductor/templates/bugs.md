---
module: "{{MODULE_NAME}}"
---

# {{MODULE_NAME}} — Bug Register

> Live-behavior defects: things that are BUILT but not WORKING right in real use — found by walkthroughs, diagnosis agents, or the owner. Distinct from `debt.md` (owed process items). Only the Conductor writes this file.
> A bug closes ONLY on verified-fixed evidence (a live re-walk of the broken flow), never on a merged PR alone.

| ID | What's wrong (plain words) | Found by / where / date | Phase | Diagnosis | Fix | Status |
|---|---|---|---|---|---|---|
| B1 | {{PLAIN_SYMPTOM}} | {{WHO_WHERE_DATE}} | {{NN}} | {{CONFIRMED_CAUSE or "diagnosing"}} | {{PR or —}} | {{found / diagnosing / fix-building / fixed-unverified / fixed-verified}} |
