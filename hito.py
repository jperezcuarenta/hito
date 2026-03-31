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


def get_deterministic_bit(seed_phrase, identifier):
    """
    Creates a unique, reproducible bit (0 or 1) for any given identifier 
    (like a week number or day index) based on the song title.
    """
    combined = f"{seed_phrase}-{identifier}".encode('utf-8')
    hash_hex = hashlib.sha256(combined).hexdigest()
    return int(hash_hex[0], 16) % 2


def get_hitomezashi_pixel(date):
    """
    Calculates the Hitomezashi state for a specific calendar date.
    Uses 'Global Coordinates' so the pattern never shifts.
    """
    delta = date - REFERENCE_DATE
    week_index = delta.days // 7
    day_index = delta.days % 7
    
    h_bit = get_parity_bit_from_song(SONG_TITLE, "row", day_index)
    v_bit = get_parity_bit_from_song(SONG_TITLE, "col", week_index)
    
    return 1 if (h_bit + week_index) % 2 == (v_bit + day_index) % 2 else 0


def get_parity_bit_from_song(phrase, dimension, index):
    """Helper to generate a stable bit for a specific row or column index."""
    combined = f"{phrase}-{dimension}-{index}".encode('utf-8')
    return int(hashlib.md5(combined).hexdigest()[0], 16) % 2


def get_grid_dates():
    """Generates the 7x52 matrix of dates for the current GitHub view."""
    today = datetime.now()
    start_of_grid = today - timedelta(weeks=51, days=(today.weekday() + 1) % 7)
    return np.array([[start_of_grid + timedelta(weeks=c, days=r) for c in range(52)] for r in range(7)])


def view_mode(): 
    plt.figure(figsize=(14, 4), facecolor='#0d1117')
    ax = plt.gca()
    ax.set_facecolor('#161b22')
    
    plt.imshow(np.vectorize(get_hitomezashi_pixel)(get_grid_dates()),
               cmap='Greens',
               interpolation='nearest',
               aspect='auto')
    
    plt.title(f"Hitomezashi Pattern: {SONG_TITLE} (Hash-Seeded)", color='white', pad=20)
    plt.yticks(np.arange(7), ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], color='white')
    plt.xticks(color='white')
    plt.tick_params(colors='white')
    plt.tight_layout()
    plt.show()


def push_mode():
    dates = get_grid_dates()
    today = datetime.now()
    
    for r in range(7):
        for c in range(52):
            target_date = dates[r, c]
            if target_date > today: continue
                
            if get_hitomezashi_pixel(target_date):
                date_str = target_date.strftime('%Y-%m-%d 12:00:00')
                env = os.environ.copy()
                env["GIT_AUTHOR_DATE"] = date_str
                env["GIT_COMMITTER_DATE"] = date_str
                
                for _ in range(COMMITS_PER_DOT):
                    subprocess.run(
                        ["git", "commit", "--allow-empty", "-m", "chore: weave update", "--date", date_str],
                        env=env, capture_output=True, text=True, check=True
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["view", "push"])
    args = parser.parse_args()

    if args.action == "view":
        view_mode()
    else:
        push_mode()