#!/usr/bin/env python3
"""Entry point for the Shift Intake Parser agent."""
import asyncio
import sys

from agent.config import DomainConfig, Settings
from agent.agent import ShiftIntakeParserAgent


def main() -> None:
    settings = Settings()
    domain = DomainConfig(settings.dictionaries_path)
    agent = ShiftIntakeParserAgent(settings, domain)
    print(f"Starting Shift Intake Parser — polling every {settings.poll_interval_seconds}s", flush=True)
    asyncio.run(agent.start())


if __name__ == "__main__":
    main()
