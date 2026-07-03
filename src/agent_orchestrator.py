import os
import json
import sys
from crewai import Agent, Task, Crew, Process, LLM

INPUT_JSON = os.path.join("data", "analyzed", "rolling_anomalies.json")
OUTPUT_DIR = os.path.join("data", "agentic_analysis_of_rolling_anomalies")
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "risk_committee_report.md")

def run_agentic_risk_committee():
    """Orchestrates a CrewAI multi-agent workflow to analyze clustered financial anomalies using Gemini."""
    print("🤖 Initializing Agentic AI Risk Committee Layer...")

    if "GEMINI_API_KEY" not in os.environ:
        print("❌ Orchestrator Aborted: GEMINI_API_KEY environmental variable not detected.")
        sys.exit(1)

    if not os.path.exists(INPUT_JSON):
        print(f"⚠️ Risk Ledger not found at {INPUT_JSON}. Skipping orchestrator run.")
        return

    with open(INPUT_JSON, "r") as f:
        anomalies_data = json.load(f)

    if not anomalies_data:
        print("🕊️ Market Environment Status: Nominal. No active rolling anomalies detected.")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_REPORT, "w") as f:
            f.write("# MANTRA Risk Committee Briefing\n\n**Status:** NOMINAL\n\nNo systemic rolling anomaly clusters detected during this tracking interval.")
        return

    print(f"📈 Loaded {len(anomalies_data)} macro anomaly shock events for executive evaluation...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash", 
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.10
    )

    # Agent 1: De Analist (Nu volledig gefocust op macro-clusters in plaats van losse minuten)
    quant_analyst = Agent(
        role="Senior Quantitative Risk Analyst",
        goal="Deconstruct clustered market shock events into cross-asset risk profiles.",
        backstory=(
            "You are an elite quantitative analyst. The data engineering team has already "
            "grouped consecutive minutely anomalies into aggregated 'Macro Shock Events' to filter noise. "
            "Your job is to evaluate each unique Event ID. Look at the total duration, the peak telemetry timestamp, "
            "and the maximum return variances for US500, GOLD, and OIL_CRUDE during that specific wave. "
            "Identify which asset class triggered the initial systemic destabilization."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # Agent 2: De CRO (Geeft nu één krachtig directie-oordeel per schokgolf)
    chief_risk_officer = Agent(
        role="Chief Risk Officer (CRO)",
        goal="Issue explicit operational risk verdicts per aggregated macro shock event wave.",
        backstory=(
            "You are the CRO of a tier-1 fund. You review consolidated volatility waves instead of single minutes. "
            "For every unique Event ID, you analyze the analyst's findings and issue a single, definitive corporate "
            "verdict for that entire event block. Your report must be concise, structured, and completely free of repetitive noise."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # Taken volledig afgestemd op de nieuwe JSON-sleutels (wave_start_utc, macro_peak_market_returns, etc.)
    analysis_task = Task(
        description=(
            f"Analyze this aggregated Macro Shock Event JSON registry:\n\n{json.dumps(anomalies_data, indent=2)}\n\n"
            "For each Event ID, document: 1) The total duration and timeframe of the volatility wave (start to end UTC). "
            "2) The severity based on the worst isolation score. "
            "3) The peak cross-asset return velocities using 'macro_peak_market_returns'. "
            "Determine if the cluster represents a structural decoupling or a synchronized momentum wave."
        ),
        expected_output="A structured event log mapping out the macro metrics and primary risk drivers for each Event ID.",
        agent=quant_analyst
    )

    briefing_task = Task(
        description=(
            "Review the analyst's event log. Generate a formal C-suite Investment Risk Report in Markdown. "
            "Crucially, for each Macro Event ID documented, you MUST provide a single definitive execution verdict choosing from: "
            "EMERGENCY DE-RISK, TACTICAL HEDGE, OPPORTUNISTIC ENTRY, or MAINTAIN POSITION / HOLD. "
            "Do not write repetitive minutely updates. Provide one elegant, high-level analysis and command per event block. "
            "Structure: # MANTRA Executive Risk Briefing, ## Chronological Shock Logs & Operational Verdicts, and ## Strategic Hedging Framework."
        ),
        expected_output="A polished executive risk brief organized cleanly by Event ID with explicit market verdicts in Markdown format.",
        agent=chief_risk_officer,
        output_file=OUTPUT_REPORT
    )

    financial_crew = Crew(
        agents=[quant_analyst, chief_risk_officer],
        tasks=[analysis_task, briefing_task],
        process=Process.sequential
    )

    print("🚀 Risk Committee Session in progress. Consulting agents...")
    financial_crew.kickoff()
    print(f"✅ Executive Risk Briefing successfully compiled with rolling verdicts: {OUTPUT_REPORT}\n")

if __name__ == "__main__":
    run_agentic_risk_committee()
