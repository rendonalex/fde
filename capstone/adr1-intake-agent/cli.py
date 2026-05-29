#!/usr/bin/env python3
"""CLI tool for testing ADR-1 Intake Agent."""

import asyncio
import json
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.models import ExtractionResult, IntakeChannel
from src.mocks import MockCMSAPI
from src.services import IntakeAgent, ClaimValidator

load_dotenv()


@click.group()
def cli():
    """ADR-1 Claim Intake Agent CLI"""
    pass


@cli.command()
@click.argument("extraction_file", type=click.Path(exists=True))
async def process(extraction_file):
    """Process a claim from extraction JSON file."""
    # Load extraction result
    with open(extraction_file) as f:
        data = json.load(f)

    extraction = ExtractionResult(**data)

    # Initialize services
    agent = IntakeAgent()
    cms_api = MockCMSAPI()
    validator = ClaimValidator()

    # Process claim
    click.echo(f"Processing claim: {extraction.source_claim_ref}")
    click.echo(f"Channel: {extraction.intake_channel.value}")

    claim = await agent.process_extraction(extraction)

    # Validate
    is_valid, errors = validator.validate_claim(claim)
    if not is_valid:
        click.echo("Validation errors:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)

    # Display result
    click.echo(f"\n extraction_status: {claim.extraction_status.value}")
    click.echo(f"SLA Queue: {claim.sla_queue.value}")

    if claim.low_confidence_fields:
        click.echo(f"Low confidence fields: {', '.join(claim.low_confidence_fields)}")

    # Write to CMS if AUTO_COMPLETE
    if claim.extraction_status.value == "AUTO_COMPLETE":
        cms_response = await cms_api.create_claim(claim)
        if "error" in cms_response:
            click.echo(f"\nDuplicate detected: {cms_response['existing_claim_id']}")
        else:
            click.echo(f"\n Claim ID: {cms_response['claim_id']}")
            click.echo("Status: QUEUED")


@cli.command()
def serve():
    """Start FastAPI server."""
    import uvicorn

    click.echo("Starting ADR-1 API server...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)


@cli.command()
def test():
    """Run test suite."""
    import pytest

    sys.exit(pytest.main(["-v", "tests/"]))


if __name__ == "__main__":
    # Fix asyncio for Click
    if sys.argv[1:2] == ["process"]:
        asyncio.run(process.callback(sys.argv[2]))
    else:
        cli()
