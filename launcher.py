import os
import sys
import traceback


def main():
    try:
        if os.name == 'nt':
            import subprocess
            local_path = os.path.dirname(os.path.abspath(__file__))
            baas_exe_path = os.path.join(local_path, 'baas.exe')
            if os.path.isfile(baas_exe_path):
                subprocess.Popen([baas_exe_path], cwd=local_path)
                return
        import main as baas_main
        baas_main.main()
    except Exception as e:
        traceback.print_exc()
        input('\n按回车键退出...')


if __name__ == '__main__':
    main()
