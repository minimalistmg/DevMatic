import pytest
from click.testing import CliRunner
from devmatic.cli.main import cli

def test_cli_help():
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'DevMatic - Windows Development Environment Tool' in result.output

def test_cli_debug_flag():
    """Test debug flag"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'list'])
    assert result.exit_code == 0 