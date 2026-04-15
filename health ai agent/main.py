"""
Ambulatory Empires Healthcare AI Agent — CLI Entry Point
"""
from __future__ import annotations

import sys
import os
from datetime import datetime
from typing import Optional

# ── Ensure project root is on path ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt
from rich import print as rprint
from rich.live import Live
from rich.spinner import Spinner

app = typer.Typer(
    name="ambulatory-agent",
    help="🏥 Ambulatory Empires Healthcare AI Agent — 2026 Care Navigator",
    add_completion=False,
)
console = Console()


def _check_api_key() -> bool:
    from config import GOOGLE_API_KEY
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_gemini_api_key_here":
        console.print(
            Panel(
                "[red]❌ GOOGLE_API_KEY not set!\n\n"
                "1. Copy [bold].env.example[/bold] → [bold].env[/bold]\n"
                "2. Add your Gemini API key from [link]https://aistudio.google.com/app/apikey[/link]\n"
                "3. Re-run this command",
                title="API Key Required",
                border_style="red",
            )
        )
        return False
    return True


def _print_triage_badge(route: str, confidence: float) -> None:
    colors = {
        "EMERGENCY": "bold red on red",
        "ASC": "bold blue on blue",
        "HOME_MONITORING": "bold green on green",
        "RETAIL": "bold yellow on yellow",
        "UNKNOWN": "dim",
    }
    icons = {
        "EMERGENCY": "🚨",
        "ASC": "🏥",
        "HOME_MONITORING": "🏠",
        "RETAIL": "🏪",
        "UNKNOWN": "❓",
    }
    label_colors = {
        "EMERGENCY": "red",
        "ASC": "blue",
        "HOME_MONITORING": "green",
        "RETAIL": "yellow",
        "UNKNOWN": "white",
    }
    icon = icons.get(route, "❓")
    color = label_colors.get(route, "white")
    console.print(
        f"\n  {icon} [bold {color}]Care Route: {route}[/bold {color}] "
        f"[dim](confidence: {confidence:.0%})[/dim]"
    )


@app.command()
def chat(
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Resume an existing session ID"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Show debug info"),
):
    """
    🗨️  Start an interactive chat with the Healthcare AI Agent.
    """
    if not _check_api_key():
        raise typer.Exit(1)

    from agent.core import AmbulatoryCareAgent
    from agent.memory import store

    agent = AmbulatoryCareAgent()

    if session_id:
        session = store.get_or_create(session_id)
        console.print(f"[dim]Resuming session: {session.session_id}[/dim]")
    else:
        session = agent.new_session()

    # Welcome banner
    console.print(
        Panel(
            Markdown(agent.welcome_message()),
            title="[bold cyan]🏥 Ambulatory Empires Healthcare Agent[/bold cyan]",
            subtitle=f"[dim]Session: {session.session_id}[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    console.print("[dim]Type [bold]exit[/bold] or [bold]quit[/bold] to end. "
                  "Type [bold]vitals[/bold] to enter a vitals reading.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session ended. Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        if user_input.lower() in ("exit", "quit", "bye", "q"):
            console.print(
                Panel(
                    f"[green]Session saved.[/green]\n"
                    f"Session ID: [bold]{session.session_id}[/bold]\n"
                    f"Messages: {len(session.messages)} | "
                    f"Alerts: {len(session.alerts_triggered)}",
                    title="Goodbye! 👋",
                    border_style="green",
                )
            )
            break

        if user_input.lower() == "vitals":
            _run_vitals_wizard(agent, session)
            continue

        # Chat with spinner
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            try:
                result = agent.chat(session, user_input)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                if debug:
                    import traceback
                    traceback.print_exc()
                continue

        # Display triage badge
        triage = result["triage"]
        _print_triage_badge(triage.route.value, triage.confidence)
        if debug:
            console.print(f"  [dim]Reasoning: {triage.reasoning}[/dim]")
            console.print(f"  [dim]Keywords: {', '.join(triage.keywords) or 'N/A'}[/dim]")
            console.print(f"  [dim]Method: {triage.method}[/dim]")

        # Display agent reply
        console.print(
            Panel(
                Markdown(result["reply"]),
                title="[bold green]🤖 Agent[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        # Emergency alert
        if triage.route.value == "EMERGENCY":
            console.print(
                Panel(
                    "[bold red]⚠️  EMERGENCY DETECTED — CALL 911 IMMEDIATELY[/bold red]",
                    border_style="red",
                )
            )


def _run_vitals_wizard(agent, session) -> None:
    """Interactive vitals collection wizard."""
    console.print("\n[bold cyan]📊 Vitals Entry Wizard[/bold cyan]")
    console.print("[dim]Press Enter to skip any reading.[/dim]\n")

    from agent.memory import VitalsReading

    def safe_float(prompt: str) -> float | None:
        val = Prompt.ask(prompt, default="")
        if not val.strip():
            return None
        try:
            return float(val)
        except ValueError:
            return None

    vitals = VitalsReading(
        timestamp=datetime.now(),
        heart_rate=safe_float("  Heart Rate (bpm)"),
        blood_pressure_systolic=safe_float("  Blood Pressure Systolic (mmHg)"),
        blood_pressure_diastolic=safe_float("  Blood Pressure Diastolic (mmHg)"),
        oxygen_saturation=safe_float("  Oxygen Saturation (%)"),
        blood_glucose=safe_float("  Blood Glucose (mg/dL)"),
        temperature=safe_float("  Temperature (°F)"),
        respiratory_rate=safe_float("  Respiratory Rate (breaths/min)"),
    )

    with console.status("[dim]Analyzing vitals...[/dim]", spinner="dots"):
        result = agent.analyze_vitals(session, vitals)

    alert_colors = {
        "NORMAL": "green", "MONITOR": "yellow",
        "ALERT": "orange3", "EMERGENCY": "red",
    }

    from modules.hospital_at_home import analyze_vitals
    rule_result = analyze_vitals({k: v for k, v in vitals.to_dict().items() if k != "timestamp" and v is not None})
    alert_level = rule_result.get("overall_alert", "NORMAL")
    color = alert_colors.get(alert_level, "white")

    console.print(f"\n  [bold {color}]Alert Level: {alert_level}[/bold {color}]")
    console.print(
        Panel(
            Markdown(result["analysis"]),
            title="[bold]🩺 Vitals Analysis[/bold]",
            border_style=color,
            padding=(1, 2),
        )
    )

    if result["is_critical"]:
        console.print(
            Panel("[bold red]⚠️  CRITICAL VITALS — Contact your care team immediately![/bold red]",
                  border_style="red")
        )


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to listen on"),
    reload: bool = typer.Option(True, help="Auto-reload on code changes"),
):
    """
    🌐 Start the FastAPI REST server.
    """
    if not _check_api_key():
        raise typer.Exit(1)

    import uvicorn
    console.print(
        Panel(
            f"[bold cyan]🏥 Ambulatory Empires Healthcare API[/bold cyan]\n\n"
            f"🔗 API:  [link]http://{host}:{port}[/link]\n"
            f"📖 Docs: [link]http://{host}:{port}/docs[/link]\n"
            f"🔄 Reload: {'enabled' if reload else 'disabled'}",
            border_style="cyan",
        )
    )
    uvicorn.run("api.app:app", host=host, port=port, reload=reload)


@app.command()
def demo():
    """
    🎬 Run a scripted demo conversation showcasing all three pillars.
    """
    if not _check_api_key():
        raise typer.Exit(1)

    from agent.core import AmbulatoryCareAgent

    console.print(
        Panel(
            "[bold cyan]🎬 Ambulatory Empires Demo[/bold cyan]\n"
            "Showcasing all three care pathways with sample queries...",
            border_style="cyan",
        )
    )

    agent = AmbulatoryCareAgent()

    demo_queries = [
        ("🏪 Retail Health", "I've had a runny nose and sore throat for 2 days. Not sure if it's strep."),
        ("🏥 ASC / Outpatient", "My doctor said I need a knee replacement. Where can I get this done without a long hospital stay?"),
        ("🏠 Hospital-at-Home", "I have heart failure and just got home from the hospital. What devices should I use to monitor myself?"),
        ("🚨 Emergency", "My 65-year-old father suddenly has face drooping on one side and can't speak clearly."),
    ]

    for title, query in demo_queries:
        console.print(f"\n[bold yellow]━━━ {title} ━━━[/bold yellow]")
        console.print(f"[dim]Query:[/dim] {query}")

        session = agent.new_session()
        with console.status("[dim]Processing...[/dim]", spinner="dots"):
            try:
                result = agent.chat(session, query)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue

        triage = result["triage"]
        _print_triage_badge(triage.route.value, triage.confidence)
        console.print(
            Panel(
                Markdown(result["reply"][:800] + ("..." if len(result["reply"]) > 800 else "")),
                border_style="green",
                padding=(0, 1),
            )
        )


@app.command()
def session_info(session_id: str = typer.Argument(..., help="Session ID to inspect")):
    """
    🔍 Display information about a session.
    """
    from agent.memory import store
    session = store.get_session(session_id)
    if not session:
        console.print(f"[red]Session '{session_id}' not found.[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Session: {session_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    s = session.summary()
    for k, v in s.items():
        table.add_row(str(k), str(v))

    console.print(table)


if __name__ == "__main__":
    app()
