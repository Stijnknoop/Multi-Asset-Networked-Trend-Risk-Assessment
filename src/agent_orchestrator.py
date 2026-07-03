import os
import json
import sys
from crewai import Agent, Task, Crew, Process, LLM

ANALYZED_DIR = os.path.join("data", "analyzed")
INPUT_JSON = os.path.join(ANALYZED_DIR, "rolling_anomalies.json")
OUTPUT_REPORT = os.path.join(ANALYZED_DIR, "risk_committee_report.md")

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
        with open(OUTPUT_REPORT, "w") as f:
            f.write("# MANTRA Risk Committee Briefing\n\n**Status:** NOMINAL\n\nNo systemic anomalies detected. Maintain current structural portfolio allocations.")
        return

    print(f"📈 Loaded {len(anomalies_data)} systemic anomaly nodes for executive evaluation...")

    # Configure Gemini 1.5 Flash for cost-efficient, high-speed text generation
    gemini_llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.15 # Low temperature to enforce strict mathematical/logical consistency
    )

    # Define Agent 1: The Quantitative Risk Analyst
    quant_analyst = Agent(
        role="Senior Quantitative Risk Analyst",
        goal="Deconstruct rolling anomaly logs into cross-asset mathematical shock signals.",
        backstory=(
            "You are an elite quantitative analyst. You process anomaly datastreams "
            "chronologically. You are strictly forbidden from looking ahead; you evaluate each "
            "anomaly timestamp purely with the context provided up to that second. Your job is to calculate "
            "the mathematical velocity of the shock and identify which asset broke its historical bounds first."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # Define Agent 2: The Chief Risk Officer (CRO)
    chief_risk_officer = Agent(
        role="Chief Risk Officer (CRO)",
        goal="Issue explicit risk execution verdicts (De-risk, Hedge, Hold, Opportunistic Entry) for every market shock.",
        backstory=(
            "You are the CRO of a major institutional fund. You do not gamble on directional alpha. "
            "You protect institutional capital. When a rolling anomaly occurs, you look at the analyst's "
            "metrics and issue a definitive operational command for the trading desk based strictly on risk thresholds."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # Define Tasks - Enforcing strict chronological, out-of-sample execution behavior
    analysis_task = Task(
        description=(
            f"Analyze this chronological streaming JSON anomaly log:\n\n{json.dumps(anomalies_data, indent=2)}\n\n"
            "For each timestamp, process the data out-of-sample (assume you do not know what happens in the next timestamps). "
            "Determine: 1) The exact magnitude of the sudden return spike. 2) The directionality (crash vs rally). "
            "3) Whether it is an isolated asset event or a coordinated systemic cross-asset market shock."
        ),
        expected_output="A step-by-step chronological telemetry breakdown showing the mathematical escalation of each anomaly event.",
        agent=quant_analyst
    )

    briefing_task = Task(
        description=(
            "Review the analyst's telemetry. Act as the CRO and generate a formal C-suite Investment Risk Report in Markdown. "
            "Crucially, for each anomaly timestamp documented, you MUST provide a definitive execution verdict choosing from:\n"
            "- **🔴 VERDICT: EMERGENCY DE-RISK** (If an asset crashes violently, threatening margin limits)\n"
            "- **🟡 VERDICT: TACTICAL HEDGE** (If high-velocity cross-asset correlations threaten current portfolio balance)\n"
            "- **🟢 VERDICT: OPPORTUNISTIC ENTRY** (If an anomaly represents an oversold price dislocation with stabilizing metrics)\n"
            "- **⚪ VERDICT: MAINTAIN POSITION / HOLD** (If the anomaly is high-volume but within safe risk parameters)\n\n"
            "Structure the report with clear headers: # MANTRA Executive Risk Briefing, ## Chronological Shock Logs & Operational Verdicts, and ## Strategic Hedging Framework."
        ),
        expected_output="A highly professional executive risk brief with explicit, time-stamped market verdicts in Markdown format.",
        agent=chief_risk_officer,
        output_file=OUTPUT_REPORT
    )

    # Run the crew
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
