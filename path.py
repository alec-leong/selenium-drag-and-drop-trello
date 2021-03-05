import platform
import re

operating_system = platform.system()

if operating_system == 'Linux':
    chromedriver_rel_path = 'chromedrivers/chromedriver_linux64/'
elif operating_system == 'Windows':
    chromedriver_rel_path = 'chromedrivers/chromedriver_win32/'
elif operating_system == 'Darwin':
    chromedriver_rel_path = 'chromedrivers/chromedriver_mac64_m1/' \
        if re.search('ARM', platform.system()) \
        else 'chromedrivers/chromedriver_mac64/'
else:
    raise OSError(f'Unsupported operating system.\n\tActual: {operating_system}\n\tExpected: Linux, Windows, or Darwin')

chromedriver_rel_path += 'chromedriver'
