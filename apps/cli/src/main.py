import typer
from commands.health import health

app = typer.Typer(help="Plutopus Predictive NOC Copilot CLI")

# Register the health command
app.command(name="health")(health)

if __name__ == "__main__":
    app()
