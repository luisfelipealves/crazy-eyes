"""Exercise real WFF battery data and pulse animation on the current style."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import time
from PIL import Image
from tools.watchface_style_device_check import assert_style, StyleStability, STYLES


def assert_mood(picture, style, tired):
    if not tired:
        assert_style(picture, style)
        return
    picture = picture.convert('RGB').resize((450, 450))
    for origin in (54, 243):
        if max(picture.getpixel((origin + 76, 187 if style == 'monster' else 182))) > 30:
            raise AssertionError(f'{style}: upper eyelid did not close at20% battery')
        if min(picture.getpixel((origin + 76, 272))) < 150:
            raise AssertionError(f'{style}: tired eye is missing or fully blinking')
        if max(picture.getpixel((origin + 3, 126))) > 30:
            raise AssertionError(f'{style}: mood mask produced a rectangular overlay')


def pupil_widths(picture):
    """Horizontal iris extent is unaffected by the ordinary vertical blink."""
    picture = picture.convert('RGB').resize((450, 450))
    widths = []
    for origin in (54, 243):
        def iris(x):
            return min(picture.getpixel((origin + x, 226))) < 160
        if not iris(76):
            raise AssertionError('Pupil center is not visible')
        # Reflections can split a row into separate runs. Measure the outer
        # extent so ordinary vertical blinking cannot move a highlight into
        # the row and falsely look like a horizontal pulse.
        marked = [x for x in range(36, 117) if iris(x)]
        widths.append(marked[-1] - marked[0] + 1)
    return widths


def overlay_has_focus(window_dump):
    """Ignore stale overlay windows and ordinary watch face blinks."""
    return any('mCurrentFocus=' in line and
               ('ChargingActivity' in line or 'AllAppsLauncherActivity' in line)
               for line in window_dump.splitlines())


def watchface_clock_visible(picture):
    # The existing clock remains visible during blinks and mood transitions.
    # Full-screen system cards (including low-battery warnings) cover it.
    clock = picture.convert('RGB').resize((450, 450)).crop((100, 0, 350, 70))
    return sum(clock.convert('L').histogram()[81:]) >= 150


def run(style, output):
    output.mkdir(parents=True, exist_ok=True)
    def adb(*args):
        return subprocess.check_output(['adb', *args], timeout=25)
    def power(level, charging):
        adb('emu', 'power', 'capacity', str(level))
        adb('emu', 'power', 'ac', 'on' if charging else 'off')
        adb('emu', 'power', 'status', 'charging' if charging else 'discharging')
        adb('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
    last_dismissed = float('-inf')
    def capture(label):
        nonlocal last_dismissed
        focus = adb('shell', 'dumpsys', 'window').decode()
        (output / f'{style}-focus.txt').write_text('\n'.join(
            line for line in focus.splitlines() if 'mCurrentFocus=' in line))
        picture = Image.open(io.BytesIO(adb('exec-out', 'screencap', '-p')))
        now = time.monotonic()
        if (overlay_has_focus(focus) or not watchface_clock_visible(picture)) and now - last_dismissed >= 3:
            adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
            last_dismissed = now
        picture.save(output / f'{style}-{label}.png')
        return picture
    def wait_mood(label, tired):
        stable = StyleStability(lambda image, selected: assert_mood(image, selected, tired))
        deadline = time.monotonic() + 35
        while True:
            started = time.monotonic()
            picture = capture(label)
            if stable.observe(picture, style, started): return picture
            if time.monotonic() >= deadline:
                raise stable.error or AssertionError(f'{style}: {label} did not stabilize')
            # Blinks and mood transitions are not navigation failures. Only
            # capture() dismisses a confirmed focused system overlay.
            time.sleep(.4)
    traces = []
    try:
        power(21, False); wait_mood('awake-21', False)
        power(20, False); wait_mood('tired-20', True)
        power(20, True); wait_mood('charging-20', False)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline or len(traces) < 4:
            picture = capture('pulse-' + str(len(traces)))
            try:
                assert_mood(picture, style, False)
                traces.append(pupil_widths(picture))
            except AssertionError:
                if time.monotonic() >= deadline + 8: raise
            time.sleep(.25)
        (output / f'{style}-pulse.json').write_text(json.dumps(traces))
        if any(max(t[i] for t in traces) - min(t[i] for t in traces) < 4 for i in (0, 1)):
            raise AssertionError(f'{style}: charging pupil pulse not observed on both eyes: {traces}')
        power(20, False); wait_mood('unplugged-20', True)
        power(21, False); wait_mood('recovered-21', False)
        print(f'PASS battery {style}: awake21%, tired20%, charging pulse, unplugged-low and recovery', flush=True)
    finally:
        power(80, False)
        (output / f'{style}-logcat.txt').write_bytes(adb('logcat', '-d', '-v', 'brief'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', choices=STYLES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.style, args.output)
