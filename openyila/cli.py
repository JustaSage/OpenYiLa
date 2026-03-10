"""Command-line interface for OpenYila (Typer-based, stateless)."""

import asyncio
import logging
from typing import Annotated

import typer

from openyila.client import YilaClient, open_device
from openyila.device import YilaDevice
from openyila.i18n import t
from openyila.scanner import YilaScanner

app = typer.Typer(
    name="openyila",
    help=t("app.help"),
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.callback()
def callback(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help=t("opt.verbose"))
    ] = False,
):
    typer.echo(t("banner"))
    _setup_logging(verbose)


@app.command(help=t("cmd.scan"))
def scan(
    timeout: Annotated[
        float, typer.Option("--timeout", "-t", help=t("opt.timeout"))
    ] = 6.0,
):
    async def _run():
        scanner = YilaScanner(scan_timeout=timeout)
        typer.echo(t("scan.scanning", timeout=timeout))
        devices = await scanner.scan()
        if not devices:
            typer.echo(t("scan.no_devices"))
            raise typer.Exit()
        typer.echo(t("scan.found", count=len(devices)))
        for d in devices:
            bat = t("scan.battery", level=d["battery_level"]) if d.get("battery_level") else ""
            typer.echo(f"  {d['name']}  [{d['address']}]  RSSI={d['rssi']}{bat}")

    asyncio.run(_run())


@app.command(name="open", help=t("cmd.open"))
def open_cmd(
    address: Annotated[str, typer.Argument(help=t("arg.address"))],
    password: Annotated[str, typer.Option("--password", "-p", help=t("opt.password"))],
    open_time: Annotated[int, typer.Option("--open-time", "-o", help=t("opt.open_time"))] = 500,
    wait_time: Annotated[int, typer.Option("--wait-time", "-w", help=t("opt.wait_time"))] = 500,
    close_time: Annotated[int, typer.Option("--close-time", "-c", help=t("opt.close_time"))] = 500,
    reverse: Annotated[bool, typer.Option("--reverse", "-r", help=t("opt.reverse"))] = False,
):
    _validate_password(password)
    device = YilaDevice(
        address=address,
        password=password,
        open_time=open_time,
        wait_time=wait_time,
        close_time=close_time,
        attribute=1 if reverse else 0,
    )

    async def _run():
        resp = await open_device(device)
        if resp.success:
            typer.echo(t("open.success", address=address))
            if resp.battery_level:
                typer.echo(t("open.battery", level=resp.battery_level))
        else:
            typer.echo(t("open.failed", message=resp.message), err=True)
            raise typer.Exit(1)

    asyncio.run(_run())


@app.command(help=t("cmd.passwd"))
def passwd(
    address: Annotated[str, typer.Argument(help=t("arg.address"))],
    old_password: Annotated[str, typer.Option("--old", "-o", help=t("opt.old_password"))],
    new_password: Annotated[str, typer.Option("--new", "-n", help=t("opt.new_password"))],
):
    _validate_password(old_password)
    _validate_password(new_password)
    device = YilaDevice(address=address, password=old_password)

    async def _run():
        client = YilaClient(device)
        try:
            await client.connect()
            resp = await client.change_password(old_password, new_password)
            if resp.success:
                typer.echo(t("passwd.success", address=address))
            else:
                typer.echo(t("passwd.failed", message=resp.message), err=True)
                raise typer.Exit(1)
        finally:
            await client.disconnect()

    asyncio.run(_run())


def _validate_password(password: str):
    if len(password) != 6 or not password.isdigit():
        typer.echo(t("err.password_format"), err=True)
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
