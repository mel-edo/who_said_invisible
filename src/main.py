import cv2
import time
import os
import subprocess
import time
import pytesseract

KEYWORDS = ["invisible", "metal gear", "solid", "snake"]
# Path to your reference images
REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "../reference_images")
CINEMATIC_SCRIPT = os.path.join(os.path.dirname(__file__), "cinematic.py")
SCREENSHOT_PATH = "/tmp/screen.png"

# Load all reference images and compute keypoints/descriptors
def load_references():
    references = []
    orb = cv2.ORB_create()
    for filename in os.listdir(REFERENCE_FOLDER):
        path = os.path.join(REFERENCE_FOLDER, filename)
        img = cv2.imread(path, 0)  # grayscale
        if img is not None:
            kp, des = orb.detectAndCompute(img, None)
            references.append((filename, kp, des, img))
    return references

# Take a screenshot using grim
def capture_screen():
    subprocess.run(["grim", SCREENSHOT_PATH])
    img = cv2.imread(SCREENSHOT_PATH, 0)
    return img

# Match the screen with reference images
def match_screen_to_refs(screen_img, references):
    orb = cv2.ORB_create()
    screen_kp, screen_des = orb.detectAndCompute(screen_img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    for name, ref_kp, ref_des, ref_img in references:
        matches = bf.match(ref_des, screen_des)
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = [m for m in matches if m.distance < 50]
        print(f"[{name}] Found {len(good_matches)} good matches.")

        if len(good_matches) > 20:  # tweak threshold if needed
            matched_points = [screen_kp[m.trainIdx].pt for m in good_matches]
            if matched_points:
                xs, ys = zip(*matched_points)
                avg_x = int(sum(xs) / len(xs))
                avg_y = int(sum(ys) / len(ys))
                return True, name, (avg_x, avg_y)
    return False, None, None

def play_audio():
    subprocess.Popen([
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
        os.path.join(os.path.dirname(__file__), "../overlays/audio/invisible.mp4")
    ])

# Run cinematic.py in a subprocess
def trigger_cinematic(match_pos):
    x, y = match_pos
    subprocess.Popen(["python3", CINEMATIC_SCRIPT, str(x), str(y)])
    play_audio()

if __name__ == "__main__":
    references = load_references()
    print("Loaded reference images.")

    while True:
        screen = capture_screen()
        matched, name, match_pos = match_screen_to_refs(screen, references)

        if matched:
            print(f"💥 Metal Gear detected via: {name} at {match_pos}")
            trigger_cinematic(match_pos)
            break

        time.sleep(2)
