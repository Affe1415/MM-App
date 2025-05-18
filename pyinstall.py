import PyInstaller.__main__

PyInstaller.__main__.run([
    'app.py',
    '--windowed',
    '--noconsole',
    '--icon=mail_app_icon.icns',
])