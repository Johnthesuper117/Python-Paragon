#!/usr/bin/env python3
"""
PythonParagon - A Professional Python Terminal Application

Main entry point for the application.

Author: PythonParagon Team
Version: 2.0.0
License: MIT
"""
import sys
from paragon.core.shell import InteractiveShell

# Import all command modules
from paragon.commands import system, network, filelab, utils, data, git, docker, text, filesystem, archive, shell_utils


def main():
    """Main entry point for PythonParagon."""
    
    # Create shell instance
    shell = InteractiveShell()
    
    # Register all system commands
    shell.register_command('system.cpu', system.monitor_cpu)
    shell.register_command('system.memory', system.monitor_memory)
    shell.register_command('system.processes', system.list_processes)
    shell.register_command('system.disk', system.disk_usage)
    shell.register_command('system.env', system.show_environment)
    shell.register_command('system.whoami', system.whoami_command)
    shell.register_command('system.hostname', system.hostname_command)
    shell.register_command('system.uptime', system.uptime_command)
    shell.register_command('system.date', system.date_command)
    shell.register_command('system.which', system.which_command)
    shell.register_command('system.kill', system.kill_command)
    
    # Register network commands
    shell.register_command('network.ip', network.public_ip)
    shell.register_command('network.http-check', network.http_status_checker)
    shell.register_command('network.port-scan', network.port_scanner)
    shell.register_command('network.ping', network.ping_host)
    shell.register_command('network.wget', network.wget_command)
    
    # Register filelab commands
    shell.register_command('filelab.rename', filelab.bulk_rename)
    shell.register_command('filelab.metadata', filelab.file_metadata)
    shell.register_command('filelab.tree', filelab.directory_tree)
    shell.register_command('filelab.search', filelab.search_files)
    
    # Register utils commands
    shell.register_command('utils.currency', utils.currency_converter)
    shell.register_command('utils.password', utils.password_generator)
    shell.register_command('utils.markdown', utils.markdown_renderer)
    shell.register_command('utils.base64', utils.base64_converter)
    shell.register_command('utils.hash', utils.hash_text)
    shell.register_command('utils.uuid', utils.generate_uuid)
    
    # Register data commands
    shell.register_command('data.json-format', data.json_format)
    shell.register_command('data.yaml-format', data.yaml_format)
    shell.register_command('data.csv-stats', data.csv_stats)
    shell.register_command('data.json-query', data.json_query)
    
    # Register git commands
    shell.register_command('git.status', git.git_status)
    shell.register_command('git.log', git.git_log)
    shell.register_command('git.branches', git.git_branches)
    shell.register_command('git.diff', git.git_diff)
    
    # Register docker commands
    shell.register_command('docker.ps', docker.docker_ps)
    shell.register_command('docker.images', docker.docker_images)
    shell.register_command('docker.stats', docker.docker_stats)
    
    # Register text commands
    shell.register_command('text.log-analyze', text.log_analyze)
    shell.register_command('text.text-stats', text.text_stats)
    shell.register_command('text.word-count', text.word_count)
    
    # Register filesystem commands
    shell.register_command('filesystem.ls', filesystem.ls_command)
    shell.register_command('filesystem.cp', filesystem.cp_command)
    shell.register_command('filesystem.mv', filesystem.mv_command)
    shell.register_command('filesystem.rm', filesystem.rm_command)
    shell.register_command('filesystem.mkdir', filesystem.mkdir_command)
    shell.register_command('filesystem.touch', filesystem.touch_command)
    shell.register_command('filesystem.cat', filesystem.cat_command)
    shell.register_command('filesystem.head', filesystem.head_command)
    shell.register_command('filesystem.tail', filesystem.tail_command)
    shell.register_command('filesystem.grep', filesystem.grep_command)
    shell.register_command('filesystem.sort', filesystem.sort_command)
    
    # Register archive commands
    shell.register_command('archive.zip', archive.zip_command)
    shell.register_command('archive.unzip', archive.unzip_command)
    shell.register_command('archive.tar', archive.tar_command)
    
    # Register shell utility commands
    shell.register_command('shell.echo', shell_utils.echo_command)
    shell.register_command('shell.history', shell_utils.history_command)
    shell.register_command('shell.alias', shell_utils.alias_command)
    shell.register_command('shell.clear', shell_utils.clear_command)
    shell.register_command('shell.sleep', shell_utils.sleep_command)
    shell.register_command('shell.pwd', shell_utils.pwd_command)
    shell.register_command('shell.cd', shell_utils.cd_command)
    shell.register_command('shell.export', shell_utils.export_command)
    shell.register_command('shell.printenv', shell_utils.printenv_command)
    
    # Register aliases for convenience
    # System aliases
    shell.register_alias('cpu', 'system.cpu')
    shell.register_alias('memory', 'system.memory')
    shell.register_alias('mem', 'system.memory')
    shell.register_alias('processes', 'system.processes')
    shell.register_alias('ps', 'system.processes')
    shell.register_alias('disk', 'system.disk')
    shell.register_alias('env', 'system.env')
    shell.register_alias('whoami', 'system.whoami')
    shell.register_alias('hostname', 'system.hostname')
    shell.register_alias('uptime', 'system.uptime')
    shell.register_alias('date', 'system.date')
    shell.register_alias('which', 'system.which')
    shell.register_alias('kill', 'system.kill')
    
    # Network aliases
    shell.register_alias('ip', 'network.ip')
    shell.register_alias('http', 'network.http-check')
    shell.register_alias('scan', 'network.port-scan')
    shell.register_alias('ping', 'network.ping')
    shell.register_alias('wget', 'network.wget')
    shell.register_alias('download', 'network.wget')
    
    # Filelab aliases
    shell.register_alias('rename', 'filelab.rename')
    shell.register_alias('metadata', 'filelab.metadata')
    shell.register_alias('tree', 'filelab.tree')
    shell.register_alias('search', 'filelab.search')
    
    # Filesystem aliases
    shell.register_alias('ls', 'filesystem.ls')
    shell.register_alias('dir', 'filesystem.ls')
    shell.register_alias('cp', 'filesystem.cp')
    shell.register_alias('copy', 'filesystem.cp')
    shell.register_alias('mv', 'filesystem.mv')
    shell.register_alias('move', 'filesystem.mv')
    shell.register_alias('rm', 'filesystem.rm')
    shell.register_alias('del', 'filesystem.rm')
    shell.register_alias('mkdir', 'filesystem.mkdir')
    shell.register_alias('touch', 'filesystem.touch')
    shell.register_alias('cat', 'filesystem.cat')
    shell.register_alias('type', 'filesystem.cat')
    shell.register_alias('head', 'filesystem.head')
    shell.register_alias('tail', 'filesystem.tail')
    shell.register_alias('grep', 'filesystem.grep')
    shell.register_alias('sort', 'filesystem.sort')
    
    # Archive aliases
    shell.register_alias('zip', 'archive.zip')
    shell.register_alias('unzip', 'archive.unzip')
    shell.register_alias('tar', 'archive.tar')
    
    # Shell utility aliases
    shell.register_alias('echo', 'shell.echo')
    shell.register_alias('history', 'shell.history')
    shell.register_alias('alias', 'shell.alias')
    shell.register_alias('clear', 'shell.clear')
    shell.register_alias('cls', 'shell.clear')
    shell.register_alias('sleep', 'shell.sleep')
    shell.register_alias('pwd', 'shell.pwd')
    shell.register_alias('cd', 'shell.cd')
    shell.register_alias('export', 'shell.export')
    shell.register_alias('printenv', 'shell.printenv')
    
    # Utils aliases
    shell.register_alias('currency', 'utils.currency')
    shell.register_alias('password', 'utils.password')
    shell.register_alias('passwd', 'utils.password')
    shell.register_alias('markdown', 'utils.markdown')
    shell.register_alias('md', 'utils.markdown')
    shell.register_alias('base64', 'utils.base64')
    shell.register_alias('b64', 'utils.base64')
    shell.register_alias('hash', 'utils.hash')
    shell.register_alias('uuid', 'utils.uuid')
    
    # Data aliases
    shell.register_alias('json-format', 'data.json-format')
    shell.register_alias('json', 'data.json-format')
    shell.register_alias('yaml-format', 'data.yaml-format')
    shell.register_alias('yaml', 'data.yaml-format')
    shell.register_alias('csv-stats', 'data.csv-stats')
    shell.register_alias('csv', 'data.csv-stats')
    shell.register_alias('json-query', 'data.json-query')
    
    # Git aliases
    shell.register_alias('git', 'git.status')
    shell.register_alias('git-status', 'git.status')
    shell.register_alias('git-log', 'git.log')
    shell.register_alias('git-branches', 'git.branches')
    shell.register_alias('git-diff', 'git.diff')
    
    # Docker aliases
    shell.register_alias('docker', 'docker.ps')
    shell.register_alias('docker-ps', 'docker.ps')
    shell.register_alias('docker-images', 'docker.images')
    shell.register_alias('docker-stats', 'docker.stats')
    
    # Text aliases
    shell.register_alias('log-analyze', 'text.log-analyze')
    shell.register_alias('log', 'text.log-analyze')
    shell.register_alias('text-stats', 'text.text-stats')
    shell.register_alias('word-count', 'text.word-count')
    shell.register_alias('wc', 'text.word-count')
    
    # Run the shell
    shell.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
