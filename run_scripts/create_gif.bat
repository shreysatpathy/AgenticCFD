@echo off
REM Script to create animated GIF of boiling pool simulation from Windows
REM Shows temperature contours and velocity vectors

echo === Boiling Pool Simulation GIF Creator ===
echo.

REM Check if we're in the right directory
if not exist "case.foam" (
    echo Error: case.foam file not found!
    echo Make sure you're in the OpenFOAM case directory.
    pause
    exit /b 1
)

REM Check if simulation results exist
if not exist "0.1" if not exist "1" (
    echo Warning: No time directories found. Make sure the simulation has been run.
    echo Run the simulation first with WSL: wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && . /opt/openfoam11/etc/bashrc && ./Allrun"
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

echo Creating animation frames with ParaView in WSL...

REM Run the ParaView Python script through WSL
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && . /opt/openfoam11/etc/bashrc && pvpython create_animation.py"

if %errorlevel% neq 0 (
    echo Error running ParaView script!
    echo Trying alternative method...
    wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && . /opt/openfoam11/etc/bashrc && paraview --script=create_animation.py"
)

REM Check if frames were created
if not exist "animation_frames" (
    echo Error: Animation frames were not created!
    pause
    exit /b 1
)

REM Count frames
for /f %%i in ('dir /b animation_frames\*.png 2^>nul ^| find /c /v ""') do set frame_count=%%i

if %frame_count%==0 (
    echo Error: No PNG frames found!
    pause
    exit /b 1
)

echo Found %frame_count% animation frames.
echo Creating animated GIF...

REM Try different methods to create GIF

REM Method 1: Try ImageMagick (if installed on Windows)
where convert >nul 2>nul
if %errorlevel%==0 (
    echo Using ImageMagick to create GIF...
    convert -delay 20 -loop 0 animation_frames\*.png boiling_simulation.gif
    if %errorlevel%==0 (
        echo ✓ GIF created successfully with ImageMagick: boiling_simulation.gif
        for %%A in (boiling_simulation.gif) do echo File size: %%~zA bytes
        goto success
    )
)

REM Method 2: Try ffmpeg (if installed on Windows)
where ffmpeg >nul 2>nul
if %errorlevel%==0 (
    echo Using ffmpeg to create GIF...
    ffmpeg -y -framerate 5 -pattern_type glob -i "animation_frames/*.png" -vf "fps=5,scale=800:-1:flags=lanczos,palettegen" palette.png
    ffmpeg -y -framerate 5 -pattern_type glob -i "animation_frames/*.png" -i palette.png -filter_complex "fps=5,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse" boiling_simulation.gif
    if %errorlevel%==0 (
        echo ✓ GIF created successfully with ffmpeg: boiling_simulation.gif
        for %%A in (boiling_simulation.gif) do echo File size: %%~zA bytes
        del palette.png 2>nul
        goto success
    )
)

REM Method 3: Try through WSL with ImageMagick
echo Trying ImageMagick through WSL...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && convert -delay 20 -loop 0 animation_frames/*.png boiling_simulation.gif"
if %errorlevel%==0 (
    echo ✓ GIF created successfully with WSL ImageMagick: boiling_simulation.gif
    for %%A in (boiling_simulation.gif) do echo File size: %%~zA bytes
    goto success
)

REM Method 4: Try through WSL with ffmpeg
echo Trying ffmpeg through WSL...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && ffmpeg -y -framerate 5 -pattern_type glob -i 'animation_frames/*.png' -vf 'fps=5,scale=800:-1:flags=lanczos,palettegen' palette.png"
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && ffmpeg -y -framerate 5 -pattern_type glob -i 'animation_frames/*.png' -i palette.png -filter_complex 'fps=5,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse' boiling_simulation.gif"
if %errorlevel%==0 (
    echo ✓ GIF created successfully with WSL ffmpeg: boiling_simulation.gif
    for %%A in (boiling_simulation.gif) do echo File size: %%~zA bytes
    del palette.png 2>nul
    goto success
)

REM Method 5: Try Python with Pillow through WSL
echo Trying Python with Pillow through WSL...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/User/Surfing/flows && python3 -c \"
import os
import glob
from PIL import Image

try:
    frame_files = sorted(glob.glob('animation_frames/*.png'))
    if not frame_files:
        print('No frames found!')
        exit(1)
    
    images = [Image.open(f) for f in frame_files]
    images[0].save('boiling_simulation.gif',
                   save_all=True,
                   append_images=images[1:],
                   duration=200,
                   loop=0)
    print('✓ GIF created successfully with Python/Pillow')
except ImportError:
    print('Pillow not available')
    exit(1)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
\""

if %errorlevel%==0 (
    echo ✓ GIF created successfully with WSL Python/Pillow: boiling_simulation.gif
    for %%A in (boiling_simulation.gif) do echo File size: %%~zA bytes
    goto success
)

REM If all methods failed
echo.
echo ❌ Could not create GIF automatically.
echo.
echo Manual options:
echo 1. Install ImageMagick for Windows from: https://imagemagick.org/script/download.php#windows
echo    Then run: convert -delay 20 -loop 0 animation_frames\*.png boiling_simulation.gif
echo.
echo 2. Install ffmpeg for Windows from: https://ffmpeg.org/download.html
echo    Then use the ffmpeg commands shown above
echo.
echo 3. Install Python Pillow in WSL: wsl -d Ubuntu -- pip install Pillow
echo    Then run this script again
echo.
echo 4. Use online tools like ezgif.com to create GIF from the PNG frames
echo.
echo Animation frames are saved in: animation_frames\
echo You can view them individually or use any tool to create the GIF.
echo.
pause
exit /b 1

:success
echo.
echo 🎉 Animation GIF created successfully!
echo.
echo The GIF shows:
echo - Temperature contours (blue=cold, red=hot)
echo - Velocity vectors (arrows showing flow direction)
echo - Water surface (light blue transparent surface)
echo - Time evolution of the boiling process
echo.
echo You can now view boiling_simulation.gif with any image viewer.
pause
