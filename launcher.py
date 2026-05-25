import os
import subprocess
import sys
import time
import traceback
import urllib.request

windows_git_repo_https = 'https://gitee.com/baas-pro/baas-pro-win.git'
windows_git_repo_ssh = 'git@gitee.com:baas-pro/baas-pro-win.git'
macos_m_git_repo_https = 'https://gitee.com/baas-pro/baas-pro-macos.git'
macos_m_git_repo_ssh = 'git@gitee.com:baas-pro/baas-pro-macos.git'
git_download_url = 'https://gitee.com/baas-pro/baas-windows/releases/download/git/Git-2.43.0-64-bit.exe'


def _try_clone(url, path, cwd, extra_args=None):
    cmd = ['git'] + (extra_args if extra_args else []) + ['clone', url, path]
    print(f"  尝试方式: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode == 0


def git_clone_and_pull():
    path = 'baas-pro'
    print('检查是否已安装: {0}'.format(path))
    https_url = windows_git_repo_https if os.name == 'nt' else macos_m_git_repo_https
    ssh_url = windows_git_repo_ssh if os.name == 'nt' else macos_m_git_repo_ssh
    directory = resource_path(path)
    if not os.path.isdir(directory):
        print(f'未找到目录 {directory}，正在开始克隆仓库...')
        cwd = resource_path('')
        strategies = [
            (https_url, None, 'HTTPS系统凭证'),
            (ssh_url, None, 'SSH'),
            (https_url, ['-c', 'http.sslVerify=false'], 'HTTPS(关闭SSL验证)'),
        ]
        success = False
        for url, extra, label in strategies:
            print(f'尝试克隆方式：{label}')
            if _try_clone(url, path, cwd, extra):
                success = True
                break
            print(f'  {label} 失败，切换到下一种方式...')
        if not success:
            print('\n提示：如果一直失败可能是因为需要账号密码，请前往下列网址注册并登录 Gitee 账号：')
            print('  https://gitee.com/signup')
            print('登录后请重试，感谢。\n')
            raise RuntimeError('所有克隆方式均失败，请检查您的 Gitee 账号权限后重试')
        print('BaasPro 克隆完成...')
    else:
        try:
            git_pull(directory)
            print('BaasPro 更新完成...')
        except Exception as e:
            print('更新失败，将使用本地已有版本运行', e)
            print('\n提示：如果一直失败可能是因为需要账号密码，请前往下列网址注册并登录 Gitee 账号：')
            print('  https://gitee.com/signup')
            print('登录后请重试，感谢。\n')
    git_logs(resource_path(path))


def command_exists(command):
    print('检查是否已安装: {0}'.format(command))
    try:
        subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return True


def install_homebrew():
    print('正在安装 Homebrew...')
    subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', shell=True, check=True)


def install_git_on_windows():
    download_url = git_download_url
    git_file_path = 'Git-Installer.exe'

    if not os.path.exists(git_file_path):
        print('正在下载 Git 安装程序...')
        urllib.request.urlretrieve(download_url, git_file_path)
    else:
        print('Git 安装程序已存在，跳过下载。')

    print('正在安装 Git，请稍候...')
    try:
        subprocess.run([git_file_path, '/VERYSILENT'], check=True)
    except Exception as e:
        stack_trace = traceback.format_exc()
        print('\n安装异常: {0}'.format(e))
        print('堆栈跟踪:\n{0}'.format(stack_trace))
        print('安装失败: 如果提示没有权限,拒绝访问. 请以管理员身份运行!!!')

    print('Git安装完成。请关闭当前命令行窗口，重新打开命令行窗口后再次运行Launcher脚本。')
    wait()
    sys.exit(0)


def install_git():
    if os.name == 'nt':
        print('未检测到 Git，正在开始安装git...')
        install_git_on_windows()
        return

    if not command_exists('brew'):
        install_homebrew()

    print('正在尝试使用 Homebrew 安装 Git...')
    subprocess.run(['brew', 'install', 'git'], check=True)


def git_pull(directory):
    print_title('开始更新', f"在目录 {directory} 中执行 'git pull origin main' 更新...")

    cmds = [
        ['git', 'merge', '--abort'],
        ['git', 'checkout', '.'],
        ['git', 'clean', '-fd'],
        ['git', 'fetch', 'origin'],
        ['git', 'reset', '--hard', 'origin/main'],
        ['git', 'pull', 'origin', 'main'],
    ]
    for cmd in cmds:
        run_cmd(directory, cmd)


def run_cmd(directory, args):
    try:
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        if args[0] == 'git':
            args = ['git', '-c', 'credential.helper='] + args[1:]
        subprocess.run(args, cwd=directory, check=True, env=env)
    except Exception as e:
        pass


def git_logs(directory):
    log_command = ['git', 'log', '--pretty=format:%ad %d %s', '--date=short', '-n', '10']
    result = subprocess.run(log_command, cwd=directory, check=True, capture_output=True, text=True, encoding='utf-8')
    print_title('更新日志', f"在目录 {directory} 中执行 'git log' 更新...\n" + result.stdout)


def print_title(title, message=None):
    print(f'========================================== {title} ==========================================')
    if message is not None:
        print(message)


def start_baas():
    if os.name == 'nt':
        start_baas_windows()
    else:
        start_baas_macos()


def start_baas_windows():
    local_path = resource_path('baas-pro')
    baas_exe_path = os.path.join(local_path, 'baas.exe')

    if not os.path.isfile(baas_exe_path):
        print(f'启动程序未找到 {baas_exe_path}')
        return

    print_title('BaasPro启动')
    print('请耐心等待程序启动...')
    subprocess.Popen([baas_exe_path], cwd=local_path)


def start_baas_macos():
    local_path = resource_path('')
    baas_app_path = os.path.join(local_path, 'baas-pro/baas')
    print_title('BaasPro启动')
    print('请耐心等待程序启动...')
    try:
        subprocess.Popen([baas_app_path])
    except Exception as e:
        print('An error occurred:', e)


def resource_path(relative_path):
    if hasattr(sys, 'frozen'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def main():
    try:
        print_title('BaasPro启动器 v6.0')
        if os.name == 'nt' and not is_admin():
            print('请使用管理员方式运行')
            wait()
            return
        if not command_exists('git'):
            install_git()
        git_clone_and_pull()
        start_baas()
        for i in range(3, 0, -1):
            print(f'程序将在 {i} 秒后自动关闭...')
            time.sleep(1)
        sys.exit(0)
    except Exception as e:
        stack_trace = traceback.format_exc()
        print('\n运行异常:{0}'.format(e))
        print('堆栈跟踪:\n{0}'.format(stack_trace))
        wait()


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def wait():
    input('\n按回车键退出...')


if __name__ == '__main__':
    main()
