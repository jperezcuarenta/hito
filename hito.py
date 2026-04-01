import subprocess
import argparse
import os
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


SONG_TITLE = "Mucho Corazón"
COMMITS_PER_DOT = 20
REFERENCE_DATE = datetime(2000, 1, 1)
NUMROWS = 7
NUMCOLS = 52


def get_hitomezashi_pixel(date):
    delta = date - REFERENCE_DATE
    week_index = delta.days // 7
    day_index = delta.days % 7
    
    h_bit = get_parity_bit_from_song(SONG_TITLE, "row", day_index)
    v_bit = get_parity_bit_from_song(SONG_TITLE, "col", week_index)
    
    return 1 if (h_bit + week_index) % 2 == (v_bit + day_index) % 2 else 0


def get_parity_bit_from_song(phrase, dimension, index):
    combined = f"{phrase}-{dimension}-{index}".encode('utf-8')
    return int(hashlib.md5(combined).hexdigest()[0], 16) % 2


def get_grid_dates():
    today = datetime.now()
    start_of_grid = today - timedelta(weeks=NUMCOLS - 1, days=(today.weekday() + 1) % NUMROWS)
    return np.array([[start_of_grid + timedelta(weeks=c, days=r) for c in range(NUMCOLS)] for r in range(NUMROWS)])


def view_mode(): 
    plt.figure(figsize=(14, 4), facecolor='#0d1117')
    ax = plt.gca()
    ax.set_facecolor('#161b22')
    plt.imshow(np.vectorize(get_hitomezashi_pixel)(get_grid_dates()),
               cmap='Greens', interpolation='nearest', aspect='auto')
    plt.show()


def weave_mode():
    """Fills the last 52 weeks of history."""
    dates = get_grid_dates()
    today = datetime.now()
    for r in range(NUMROWS):
        for c in range(NUMCOLS):
            target_date = dates[r, c]
            if target_date > today:
                continue
            if get_hitomezashi_pixel(target_date):
                do_commits(target_date)


def stitch_mode():
    """Checks only today's pixel for the automated cron job."""
    today = datetime.now()
    if get_hitomezashi_pixel(today):
        do_commits(today)


def do_commits(target_date):
    date_str = target_date.strftime('%Y-%m-%d 12:00:00')
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    for _ in range(COMMITS_PER_DOT):
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "chore: hito weave", "--date", date_str],
            env=env, capture_output=True, text=True, check=True
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["view", "weave", "stitch"])
    args = parser.parse_args()

    if args.action == "view":
        view_mode()
    elif args.action == "weave":
        weave_mode()
    elif args.action == "stitch":
        stitch_mode()