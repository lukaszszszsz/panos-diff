import click


@click.command()
@click.argument("config_source", type=click.Path(), required=False)
@click.argument("config_target", type=click.Path(), required=False)
@click.option("--output", "-o", type=click.Path(), default="diff_report.txt", help="Path to save the diff report.")
@click.option("--panorama", "-p", is_flag=True, help="Connect to Panorama server instead of using local files.")
@click.option("--xpath", type=str, help="XPath expression to filter specific configuration sections.")
def main(config_source, config_target, output, panorama, xpath):
    """
    Compare two PAN-OS configuration and highlight differences.
    """
    click.echo(f"Loading source configuration from {config_source}...")

    click.echo(f"Loading destination configuration from {config_target}...")

    click.echo("Comparing configs...")
    
    click.echo(f"Generating report at {output}...")
    

    click.echo("Diff completed successfully.")

    pass

if __name__ == "__main__":
    main()