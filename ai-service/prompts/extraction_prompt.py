"""
NEXUS PM AI Service – Prompt Templates
All Gemini prompt templates are defined here as module-level string constants.
"""

# ── 1. DPR / Field-Report Extraction ─────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expert construction project controls engineer.
Extract ALL activity events mentioned in the following Daily Progress Report (DPR) or field report text.

Discipline context: {discipline}
Project context:
{project_context}

Report text:
\"\"\"
{report_text}
\"\"\"

Return ONLY a valid JSON array (no markdown, no explanation). Each element must contain exactly these keys:
{{
  "activity_name": "<descriptive name of the activity>",
  "discipline": "<one of: Civil, Piping, Electrical, Mechanical, Instrumentation, Structural, General>",
  "extracted_start": "<date in YYYY-MM-DD or empty string>",
  "extracted_finish": "<date in YYYY-MM-DD or empty string>",
  "progress_pct": <float 0-100>,
  "quantity_done": <float, units depends on discipline, 0 if not mentioned>,
  "location_tag": "<area/location string or empty>",
  "supervisor_name": "<name or empty>",
  "extraction_confidence": <float 0.0-1.0, how confident you are in this extraction>
}}

If a field is not mentioned in the text, use sensible defaults (empty string or 0).
Be thorough – extract every distinct activity mentioned.
"""

# ── 2. Excel Column Interpretation ───────────────────────────────────────────

EXCEL_INTERPRETATION_PROMPT = """You are an expert construction project controls engineer.
The following table is extracted from an Excel progress report for discipline: {discipline}.

{table_text}

Identify the most relevant columns (activity name, start date, finish date, progress %, quantity, location, supervisor).
Then extract all activity rows as a JSON array. Each element must have exactly these keys:
{{
  "activity_name": "<name>",
  "discipline": "<discipline>",
  "extracted_start": "<YYYY-MM-DD or empty>",
  "extracted_finish": "<YYYY-MM-DD or empty>",
  "progress_pct": <float 0-100>,
  "quantity_done": <float>,
  "location_tag": "<string or empty>",
  "supervisor_name": "<string or empty>",
  "extraction_confidence": <float 0.0-1.0>
}}

Return ONLY the JSON array. No markdown fences, no explanation.
"""

# ── 3. Delay / Forecast Narrative ────────────────────────────────────────────

FORECAST_NARRATIVE_PROMPT = """You are a senior construction project manager writing an executive summary.

Project forecast data:
- Schedule Performance Index (SPI): {spi}
- Elapsed duration: {elapsed_pct}% of planned duration
- Discipline productivity notes: {productivity_notes}
- Predicted delay: {delay_days} days
- Predicted finish date: {predicted_finish}
- Key risk factors: {risk_factors}

Write a concise, professional 3-4 sentence narrative explaining:
1. Why the project is on track or delayed (reference the SPI and productivity)
2. The predicted finish date and delay magnitude
3. The top risk factor and its impact
4. One actionable recommendation

Write in formal project management style. Do NOT use bullet points. Do NOT use markdown.
Return ONLY the narrative text.
"""

# ── 4. RAG / Institutional Memory Synthesis ───────────────────────────────────

RAG_SYNTHESIS_PROMPT = """You are an expert construction project manager with deep knowledge of EPC projects.
A project engineer has asked the following question:

Question: {question}

Additional context from the current project:
{context}

The following are relevant records from our institutional memory database (past projects):
{retrieved_records}

Using the institutional memory records and your expertise, provide a concise, accurate, and actionable answer.
- Reference specific records where relevant (mention project codes)
- Provide benchmarks and productivity rates from past projects
- Highlight lessons learned
- Suggest best practices

Return a plain-text answer (no markdown, no bullet formatting). Be specific and data-driven.
Limit your answer to 250 words.
"""
