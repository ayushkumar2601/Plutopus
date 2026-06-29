import typer
from client import PlutopusClient
from plutopus_schemas import HealthResponse

router = typer.Typer()

@router.callback(invoke_without_command=True)
def health(ctx: typer.Context):
    """
    Check the health of the Plutopus API backend.
    """
    client = PlutopusClient()
    try:
        data = client.check_health()
        health_resp = HealthResponse(**data)
        if health_resp.status == "healthy":
            typer.secho(f"Plutopus API: {health_resp.status.upper()}", fg=typer.colors.GREEN, bold=True)
        else:
            typer.secho(f"Plutopus API: UNHEALTHY ({health_resp.status})", fg=typer.colors.RED, bold=True)
    except Exception as e:
        typer.secho(f"Failed to connect to Plutopus API: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
