import os
import json
import sys
from crewai import Agent, Task, Crew, Process, LLM

INPUT_JSON = os.path.join("data", "analyzed", "rolling_anomalies.json")
# Nieuwe dedicated map voor de agent analyses
OUTPUT_DIR = os.path.join("data", "agentic_analysis_of_rolling_anomalies")
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "risk_committee_report.md")

def run_agentic_risk_committee():
    """Orchestrates a CrewAI multi-agent workflow to analyze financial anomalies using Gemini."""
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
            f.write("# MANTRA Risk Committee Briefing\n\n**Status:** NOMINAL\n\nNo systemic rolling anomalies detected during this tracking interval.")
        return

    print(f"📈 Loaded {len(anomalies_data)} systemic anomaly nodes for executive evaluation...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Inzet van het stabiele gemini-2.5-flash model via de native CrewAI wrapper
    gemini_llm = LLM(
        model="gemini/gemini-2.5-flash", 
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.10
    )

    # Analyst Agent met strenge schaalbeperkingen
    quant_analyst = Agent(
        role="Senior Quantitative Risk Analyst",
        goal="Deconstruct rolling anomaly logs into cross-asset mathematical shock signals with precise scale awareness.",
        backstory=(
            "You are an elite quantitative analyst. You process minutely anomaly data streams. "
            "CRITICAL CONTEXT: You evaluate 1-minute interval returns. A 1-minute return between -0.1% and +0.1% "
            "is a minor intraday fluctuation, NOT a massive 'crash' or a 'rally'. You only use words like 'sharp spike' or "
            "'rapid drop' if a 1-minute return exceeds absolute 0.15%. You maintain absolute mathematical sobriety."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # CRO Agent met focus op realistische institutionele oordelen
    chief_risk_officer = Agent(
        role="Chief Risk Officer (CRO)",
        goal="Issue explicit risk execution verdicts based on institutional volatility baselines.",
        backstory=(
            "You are the CRO of a major institutional fund. You translate quant telemetry into C-suite reports. "
            "CRITICAL: Do not use sensationalist retail trading language. If an asset drops by 0.05% in a minute, "
            "do NOT call it a crash; call it a minor negative divergence or fractional deviation. Your verdicts must "
            "be calibrated to institutional scales where only massive multi-asset joint moves trigger emergency hedging."
        ),
        verbose=True,
        llm=gemini_llm
    )

    analysis_task = Task(
        description=(
            f"Analyze this chronological streaming JSON anomaly log containing 1-minute interval steps:\n\n{json.dumps(anomalies_data, indent=2)}\n\n"
            "Evaluate each timestamp out-of-sample. Determine the true magnitude of the 1-minute returns. "
            "Note that a 0.05% move is tiny background ripple, while a 0.2% move is a significant micro-shock. "
            "Clearly map out the actual cross-asset directionality without exaggerating minor numbers."
        ),
        expected_output="A step-by-step chronological telemetry breakdown showing the mathematical escalation of each anomaly event.",
        agent=quant_analyst
    )

    briefing_task = Task(
        description=(
            "Review the analyst's telemetry. Generate a formal C-suite Investment Risk Report in Markdown. "
            "For each timestamp, provide a definitive execution verdict choosing from: EMERGENCY DE-RISK, TACTICAL HEDGE, "
            "OPPORTUNISTIC ENTRY, or MAINTAIN POSITION / HOLD. Ensure your text reflects the true scale of the data: "
            "do not issue aggressive hedge commands for minor fractional fluctuations unless multiple assets show genuine correlation breaks. "
            "Structure: # MANTRA Executive Risk Briefing, ## Chronological Shock Logs & Operational Verdicts, and ## Strategic Hedging Framework."
        ),
        expected_output="A polished executive risk brief with realistic, time-stamped market verdicts in Markdown format.",
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
