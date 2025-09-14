
# -*- mode: python -*-

block_cipher = None


a = Analysis(['app.py'],
             pathex=['/Users/sai.teja/Documents/Code/talkbot/desktop-app'],
             binaries=[],
             datas=[
                 ('db.py', '.'),
                 ('gemini_ui.py', '.'),
                 ('integrations_ui.py', '.'),
                 ('mcp_impl.py', '.'),
                 ('todo_ui.py', '.'),
                 ('gemini.py', '.'),
                 ('.env.example', '.'),
                 ('tools', 'tools'),
                 ('/Users/sai.teja/.cache/huggingface/hub/models--nvidia--parakeet-tdt-0.6b-v3/snapshots/bc3e42c344d9127e85c2d2f92be914f57d741b59', 'nemo_model')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['Carbon'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Talkbot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='icon.icns',
          info_plist={
              'NSMicrophoneUsageDescription': 'This app needs access to the microphone to transcribe your voice.',
              'NSAccessibilityUsageDescription': 'This app needs accessibility permissions to type on your keyboard.',
              'CFBundleName': 'Talkbot',
              'CFBundleDisplayName': 'Talkbot',
              'CFBundleGetInfoString': 'Talkbot, a voice transcription app',
              'CFBundleIdentifier': 'com.yourcompany.talkbot',
              'CFBundleVersion': '0.1.0',
              'CFBundleShortVersionString': '0.1.0',
          })

app = BUNDLE(exe,
             name='Talkbot.app',
             icon='icon.icns',
             bundle_identifier='com.yourcompany.talkbot')
