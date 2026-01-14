# AI Legislation Dashboard Starter Kit
## With Federal Preemption Risk Analysis

This kit contains everything you need to build an interactive dashboard for tracking state AI legislation—now updated to include analysis of which laws are at risk from the December 2025 Executive Order on federal AI preemption.

---

## Files Included

### Data Files

| File | Description |
|------|-------------|
| `ai_legislation_with_eo_risk.csv` | **USE THIS ONE** - Full dataset with EO risk analysis fields |
| `ai_legislation_clean.csv` | Basic cleaned dataset (no EO analysis) |

### Prompt Files

| File | Description |
|------|-------------|
| `CLAUDE_CODE_PROMPT_WITH_EO.md` | **RECOMMENDED** - Detailed prompt including Federal Preemption tab |
| `QUICK_START_PROMPT_WITH_EO.md` | Shorter version with EO analysis |
| `CLAUDE_CODE_PROMPT.md` | Original prompt (no EO analysis) |
| `QUICK_START_PROMPT.md` | Original short version (no EO analysis) |

### Support Files

| File | Description |
|------|-------------|
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## Quick Start

### Option A: Full Dashboard with EO Risk Analysis (Recommended)

1. Open Claude Code (claude.ai/code)
2. Upload `ai_legislation_with_eo_risk.csv`
3. Copy/paste contents of `CLAUDE_CODE_PROMPT_WITH_EO.md`
4. Follow the build steps

### Option B: Basic Dashboard (No EO Analysis)

1. Open Claude Code
2. Upload `ai_legislation_clean.csv`
3. Copy/paste contents of `CLAUDE_CODE_PROMPT.md`

---

## Executive Order Context

On **December 11, 2025**, the Trump administration signed "Ensuring a National Policy Framework for Artificial Intelligence" which:

**Targets state laws with:**
- Nondiscrimination requirements (e.g., algorithmic bias rules)
- Disclosure/notice requirements
- Impact assessment mandates

**Creates enforcement mechanisms:**
- AI Litigation Task Force (DOJ) to sue states
- Commerce Dept evaluation of "onerous" laws
- Funding restrictions (BEAD broadband funds)
- FCC/FTC preemption proceedings

**Explicitly names Colorado SB205** as an example of problematic state regulation.

**Protects (carves out):**
- Child safety laws
- Government procurement rules
- Data center/infrastructure regulations

### New Data Fields for EO Analysis

The `ai_legislation_with_eo_risk.csv` file includes these additional columns:

```
EO_Risk_Level          - High Risk / Moderate Risk / Low Risk (passed bills)
                         Pending - High/Some/Low Exposure (pending bills)
EO_Risk_Count          - Number of targeted categories (0-3)
EO_Targeted_*          - Flags for each targeted category
EO_Protected_*         - Flags for each protected category
EO_Has_Protection      - Whether bill falls under any carve-out
EO_State_Named         - Whether state is named in EO (Colorado)
State_Total_Risk_Points - Aggregate risk score for the state
```

---

## Dashboard Features

### Basic Version
- State activity overview + US map
- Year-over-year trends
- State comparisons
- Policy category analysis
- Searchable bill explorer

### With EO Analysis (adds)
- Federal Preemption Risk tab
- State risk ranking visualization
- Targeted vs Protected category comparison
- High-risk bills table
- Colorado spotlight section
- Risk-level color coding throughout

---

## Tips for Working with Claude Code

1. **Upload the CSV first** before pasting the prompt

2. **Build incrementally** - The prompts tell the agent to build one tab at a time. Say "continue" or "next step" after each works.

3. **If you get errors** - Paste the full error message and ask "How do I fix this?"

4. **To test locally** - After Claude Code generates the files:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

5. **To deploy** - Push to GitHub and connect to [Streamlit Cloud](https://share.streamlit.io) (free)

---

## Customization Ideas

Once the basic dashboard works, you might ask the agent to add:

- "Add a toggle to show/hide pending bills"
- "Create a download button for the filtered data"
- "Add a timeline showing EO deadlines (Jan 10, Mar 11, 2026)"
- "Let me compare any two states side by side"
- "Add a dark mode option"

---

## Risk Classification Methodology

The EO risk levels are **automatically classified** using rule-based category mapping—not manual review of individual bills against the Executive Order text.

### How It Works

1. **Source Data**: Bill categories come from LegiScan's legislative tracking system
2. **Category Mapping**: Each bill's categories are checked against the EO's explicitly targeted and protected areas
3. **Risk Scoring**: Bills are flagged and scored based on matches

### Targeted Categories (from EO Language)

The Executive Order explicitly targets state laws with:

| Category | Description |
|----------|-------------|
| **Nondiscrimination** | Algorithmic bias rules, anti-discrimination requirements |
| **General Notice/Disclosure** | Disclosure and transparency mandates |
| **Impact Assessments** | Required assessments before AI deployment |

### Risk Level Calculation

```
EO_Risk_Count = Number of targeted categories present (0-3)

For PASSED bills (Status = 4):
  High Risk     = 2+ targeted categories
  Moderate Risk = 1 targeted category
  Low Risk      = 0 targeted categories

For PENDING bills (Status = 1, 2, or 3):
  Pending - High Exposure = 2+ targeted categories
  Pending - Some Exposure = 1 targeted category
  Pending - Low Exposure  = 0 targeted categories
```

### Protected Categories (EO Carve-outs)

The EO explicitly protects certain types of state laws:

| Category | Description |
|----------|-------------|
| **Child Safety** | Laws protecting minors from AI harms |
| **Government Procurement** | Rules for state/local AI purchasing |
| **Data Center/Infrastructure** | Regulations on AI physical infrastructure |

Bills matching these categories are flagged with `EO_Has_Protection = 1`.

### Limitations

- Classification accuracy depends on how well LegiScan's category labels align with the EO's actual scope
- Some bills may be miscategorized if their categories don't fully capture their regulatory approach
- The EO's enforcement is subject to legal interpretation—this is a preliminary risk assessment, not legal advice

---

## Data Sources

- **Legislation data**: LegiScan (via your tracked dataset)
- **EO risk classification**: Automated category mapping to EO language (see methodology above)
- **Executive Order**: "Ensuring a National Policy Framework for Artificial Intelligence" (Dec 11, 2025)

---

## Questions?

If the coding agent gets stuck:
1. Try breaking the request into smaller pieces
2. Ask it to "start fresh with just data loading"
3. Paste any error messages directly

Good luck with your dashboard!
