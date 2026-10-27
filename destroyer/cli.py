"""
Command-Line Interface (CLI)
============================
Entry point for the Destroyer terminal interface and automated batch operations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional
from destroyer.config import load_configuration
from destroyer.core.engine import DestroyerEngine
from destroyer.core.entropy import estimate_crack_time
from destroyer.exporters.hashcat import export_hashcat_masks, export_hashcat_rules
from destroyer.exporters.john import export_john_rules
from destroyer.models.profile import TargetProfile
from destroyer.osint.scraper import harvest_endpoint_keywords

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

C_RED = "\033[1;31m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"
C_RESET = "\033[0m"


def print_banner(silent: bool = False) -> None:
    """Print standard technical CLI header."""
    if silent:
        return

    text = (
        "Destroyer Wordlist Generator - Targeted Security Profiling Utility\n"
        "Modules: PCFG Grammar | Passphrase Engine | OSINT Harvester | GPU Exporters"
    )

    if RICH_AVAILABLE:
        p = Panel(
            f"[bold cyan]{text}[/bold cyan]",
            border_style="blue",
            title="[bold green]Destroyer v3.0[/bold green]",
            subtitle="[dim]Security Assessment Utility[/dim]"
        )
        console.print(p)
    else:
        print(f"{C_CYAN}{text}{C_RESET}\n")


def prompt_questionnaire() -> TargetProfile:
    """Execute terminal profiling wizard to construct a TargetProfile."""
    if RICH_AVAILABLE:
        console.print("[bold cyan][*] Initializing Reconnaissance Profiling Questionnaire[/bold cyan]")
        console.print("[dim white]Press Enter on optional fields to skip.[/dim white]\n")
    else:
        print("[*] Initializing Reconnaissance Profiling Questionnaire")
        print("Press Enter on optional fields to skip.\n")

    data: Dict[str, Any] = {}

    if RICH_AVAILABLE:
        console.print("[bold yellow]1. Primary Target Identification[/bold yellow]")
    else:
        print("1. Primary Target Identification")

    name = input("> First Name: ").strip().lower()
    while not name:
        print("[-] Error: Primary name is required to establish target context.")
        name = input("> First Name: ").strip().lower()

    data["name"] = name
    data["surname"] = input("> Surname: ").strip().lower()
    data["nick"] = input("> Nickname / Alias: ").strip().lower()

    handles_in = input("> Known Handles / Usernames (comma-separated): ").strip()
    data["handles"] = [h.strip().lower() for h in handles_in.split(",") if h.strip()]

    data["email"] = input("> Email Address: ").strip().lower()
    data["birthdate"] = input("> Birthdate (DDMMYYYY / YYYY-MM-DD / YYYY): ").strip()
    data["mobile"] = input("> Telephone Number: ").strip()

    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]2. Associates, Relations & Identifiers[/bold yellow]")
    else:
        print("2. Associates, Relations & Identifiers")

    data["partner_name"] = input("> Partner / Spouse Name: ").strip().lower()
    data["partner_nick"] = input("> Partner Alias: ").strip().lower()
    data["partner_birthdate"] = input("> Partner Birthdate: ").strip()

    children_in = input("> Children Names (comma-separated): ").strip()
    data["children_names"] = [c.strip().lower() for c in children_in.split(",") if c.strip()]

    pets_in = input("> Pet Names (comma-separated): ").strip()
    data["pet_names"] = [p.strip().lower() for p in pets_in.split(",") if p.strip()]

    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]3. Organizational & Enterprise Parameters[/bold yellow]")
    else:
        print("3. Organizational & Enterprise Parameters")

    data["company"] = input("> Organization / Employer: ").strip().lower()
    data["company_acronym"] = input("> Organization Acronym: ").strip().lower()
    data["department"] = input("> Department (e.g. IT, DevOps, Finance): ").strip().lower()
    data["domain"] = input("> Enterprise Domain (e.g. corp.internal): ").strip().lower()

    projects_in = input("> Internal Projects / Codename Tokens (comma-separated): ").strip()
    data["project_names"] = [pr.strip().lower() for pr in projects_in.split(",") if pr.strip()]

    target_url = input("> Organizational Web Endpoint to Crawl (optional): ").strip()
    data["target_url"] = target_url

    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]4. Geographical & Custom Keywords[/bold yellow]")
    else:
        print("4. Geographical & Custom Keywords")

    data["city"] = input("> City / Primary Location: ").strip().lower()
    data["sports_team"] = input("> Affiliation / Sports Team: ").strip().lower()

    keywords_in = input("> Additional Keywords (comma-separated): ").strip()
    base_keywords = [kw.strip().lower() for kw in keywords_in.split(",") if kw.strip()]

    if target_url:
        scraped_tokens = harvest_endpoint_keywords(target_url, max_words=50)
        base_keywords.extend(scraped_tokens)

    data["keywords"] = list(dict.fromkeys(base_keywords))
    return TargetProfile.from_dict(data)


def display_summary(stats: Dict[str, Any]) -> None:
    """Render compilation metrics and keyspace entropy statistics."""
    crack_time = estimate_crack_time(stats["avg_entropy"])

    if RICH_AVAILABLE:
        table = Table(title="[bold green]Compilation Metrics[/bold green]", border_style="blue")
        table.add_column("Parameter", style="bold white")
        table.add_column("Measurement", style="bold yellow")

        table.add_row("Total Generated Candidates", f"{stats['total_words']:,}")
        table.add_row("NIST SP 800-63B Compliant (>= 15 chars)", f"{stats['nist_compliant']:,}")
        table.add_row("Mean Keyspace Entropy", f"{stats['avg_entropy']:.2f} bits")
        table.add_row("Estimated Offline Recovery Time (100 GH/s)", f"{crack_time}")
        table.add_row("Execution Duration", f"{stats['elapsed_seconds']:.2f} s")
        table.add_row("Generation Rate", f"{stats['speed_wps']:,.0f} words/s")
        table.add_row("Output File Size", f"{stats['file_size_kb']:.2f} KB")
        table.add_row("Destination", f"{stats['output_path']}")
        console.print("\n", table, "\n")
    else:
        print("\n" + "=" * 64)
        print(" COMPILATION METRICS")
        print("=" * 64)
        print(f" Total Generated Candidates : {stats['total_words']:,}")
        print(f" NIST SP 800-63B (>= 15 ch) : {stats['nist_compliant']:,}")
        print(f" Mean Keyspace Entropy      : {stats['avg_entropy']:.2f} bits")
        print(f" Est. Recovery Time (100 GH): {crack_time}")
        print(f" Execution Duration         : {stats['elapsed_seconds']:.2f} s")
        print(f" Generation Rate            : {stats['speed_wps']:,.0f} words/s")
        print(f" Output File Size           : {stats['file_size_kb']:.2f} KB")
        print(f" Destination                : {stats['output_path']}")
        print("=" * 64 + "\n")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI options."""
    parser = argparse.ArgumentParser(
        prog="destroyer",
        description="Destroyer Wordlist Generator - Targeted Security Profiling Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  destroyer -i
  destroyer -p profile.json -o wordlist.txt
  destroyer -p profile.json --url https://target.internal -o corp_wordlist.txt
  destroyer -p profile.json --mode deep --hashcat-rules custom.rule --hashcat-masks custom.hcmask
  destroyer -p profile.json --nist -o nist_passphrases.txt
        """
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch terminal questionnaire wizard")
    parser.add_argument("-p", "--profile", type=str, help="Load target profile from a JSON file")
    parser.add_argument("-u", "--url", type=str, help="Harvest keywords from an HTTP/HTTPS endpoint")
    parser.add_argument("-o", "--output", type=str, default="passwords.txt", help="Output file path (default: passwords.txt)")
    parser.add_argument("-c", "--config", type=str, help="Path to custom INI configuration file")
    parser.add_argument("-m", "--mode", choices=["fast", "standard", "deep", "passphrase"], default="standard",
                        help="Combinatorial depth mode (default: standard)")
    parser.add_argument("--min-len", type=int, default=8, help="Minimum candidate length filter (default: 8)")
    parser.add_argument("--max-len", type=int, default=64, help="Maximum candidate length filter (default: 64)")
    parser.add_argument("--nist", action="store_true", help="Enforce NIST SP 800-63B standard (minimum length: 15)")
    parser.add_argument("--leet", choices=["off", "light", "standard"], default="light",
                        help="Mutation depth: off, light (selective), or standard (default: light)")
    parser.add_argument("--no-corporate", action="store_true", help="Disable organizational directory patterns")
    parser.add_argument("--hashcat-rules", type=str, help="Export targeted Hashcat rule file (.rule)")
    parser.add_argument("--hashcat-masks", type=str, help="Export targeted Hashcat mask configuration (.hcmask)")
    parser.add_argument("--john-rules", type=str, help="Export targeted John the Ripper rule file (.rules)")
    parser.add_argument("--save-profile", type=str, help="Save questionnaire inputs to JSON for replayability")
    parser.add_argument("--no-banner", action="store_true", help="Suppress terminal header for pipe operations")
    parser.add_argument("--inspect", action="store_true", help="Print top 50 generated candidates upon completion")
    return parser.parse_args()


def main() -> None:
    """Main CLI execution flow."""
    args = parse_arguments()
    config = load_configuration(args.config)

    print_banner(silent=args.no_banner)

    target_profile: Optional[TargetProfile] = None

    if args.profile:
        if not os.path.isfile(args.profile):
            print(f"[-] Error: Profile file '{args.profile}' not found.")
            sys.exit(1)
        with open(args.profile, "r", encoding="utf-8") as fh:
            profile_data = json.load(fh)
            target_profile = TargetProfile.from_dict(profile_data)
            print(f"[+] Loaded target profile: {args.profile}")
    else:
        target_profile = prompt_questionnaire()

    if args.url:
        scraped_tokens = harvest_endpoint_keywords(
            args.url,
            max_words=config.scraper_max_words,
            timeout=config.scraper_timeout,
            user_agent=config.user_agent,
        )
        target_profile.keywords = list(dict.fromkeys(target_profile.keywords + scraped_tokens))

    if args.save_profile:
        with open(args.save_profile, "w", encoding="utf-8") as fh:
            json.dump(target_profile.to_dict(), fh, indent=4)
        print(f"[+] Saved profile configuration: {args.save_profile}")

    engine = DestroyerEngine(
        profile=target_profile,
        config=config,
        mode=args.mode,
        min_len=args.min_len,
        max_len=args.max_len,
        leet_mode=args.leet,
        include_corporate=not args.no_corporate,
        nist_mode=args.nist,
    )

    print(f"[*] Executing generation pipeline (Mode: {args.mode.upper()})...")
    stats = engine.execute(args.output)
    display_summary(stats)

    if args.hashcat_rules:
        export_hashcat_rules(args.hashcat_rules)
        print(f"[+] Hashcat rule file written: {args.hashcat_rules}")

    if args.hashcat_masks:
        export_hashcat_masks(args.hashcat_masks)
        print(f"[+] Hashcat mask file written: {args.hashcat_masks}")

    if args.john_rules:
        export_john_rules(args.john_rules)
        print(f"[+] John the Ripper rule file written: {args.john_rules}")

    if args.inspect:
        print(f"[*] Head inspection (top 50 lines from {args.output}):")
        try:
            with open(args.output, "r", encoding="utf-8") as fh:
                for idx, line in enumerate(fh):
                    if idx >= 50:
                        break
                    print(f" {idx + 1:02d}: {line.strip()}")
        except OSError as err:
            print(f"[-] Read error during inspection: {err}")

    print("[+] Wordlist compilation completed.")


if __name__ == "__main__":
    main()
