import compileall
from pathlib import Path
import shutil


def prepare_dist(pro_dir):
    dist_dir = pro_dir / 'dist'
    if dist_dir.exists():
        shutil.rmtree(dist_dir)


def ignore_dir(src, des):
    return ['.git', '.idea', 'dist']


def hide_code(pro_dir):
    for p in pro_dir.iterdir():
        if p.is_dir():
            hide_code(p)
        else:
            if p.suffix == '.py' and p.name != 'wsgi.py':
                p.unlink()
            elif p.suffix == '.pyc':
                new_name = p.name.replace('.cpython-37', '')
                p.replace(p.parent.parent / new_name)


def main():
    project_dir = Path(r'E:\project\vision')
    project_name = project_dir.name
    prepare_dist(project_dir)
    shutil.copytree(project_dir, project_dir / 'dist' / project_name,
                    ignore=ignore_dir)
    compileall.compile_dir(project_dir / 'dist' / project_name, 100, force=True)
    hide_code(project_dir / 'dist' / project_name)


if __name__ == '__main__':
    main()
