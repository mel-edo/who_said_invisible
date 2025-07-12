import cv2
import pytesseract
import time
import os
import subprocess

REFERENCE_FOLDER = os.path.join(os.path.dirname(__file__), "../reference_images")
CINEMATIC_SCRIPT = os.path.join(os.path.dirname(__file__), "cinematic.py")
SCREENSHOT_PATH = "/tmp/screen.png"
KEYWORDS = ["invisible", "metal gear", "solid", "snake"]

def load_references():
    references = []
    orb = cv2.ORB_create()
    for filename in os.listdir(REFERENCE_FOLDER):
        path = os.path.join(REFERENCE_FOLDER, filename)
        img = cv2.imread(path, 0)
        if img is not None:
            kp, des = orb.detectAndCompute(img, None)
            references.append((filename, kp, des, img))
    return references

def capture_screen():
    subprocess.run(["grim", SCREENSHOT_PATH])
    img_gray = cv2.imread(SCREENSHOT_PATH, 0)
    img_color = cv2.imread(SCREENSHOT_PATH)
    return img_gray, img_color

def match_screen_to_refs(screen_img, references):
    orb = cv2.ORB_create()
    screen_kp, screen_des = orb.detectAndCompute(screen_img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    for name, ref_kp, ref_des, ref_img in references:
        matches = bf.match(ref_des, screen_des)
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = [m for m in matches if m.distance < 50]
        print(f"[{name}] Found {len(good_matches)} good matches.")

        if len(good_matches) > 20:
            matched_points = [screen_kp[m.trainIdx].pt for m in good_matches]
            if matched_points:
                xs, ys = zip(*matched_points)
                avg_x = int(sum(xs) / len(xs))
                avg_y = int(sum(ys) / len(ys))
                return True, name, (avg_x, avg_y)
    return False, None, None

def check_ocr_keywords(img):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    for i in range(len(data['text'])):
        word = data['text'][i].strip().lower()
        if word in KEYWORDS:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            center = (x + w // 2, y + h // 2)
            print(f"OCR detected '{word}' at {center}")
            return True, center
    return False, None

def play_audio():
    subprocess.Popen([
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
        os.path.join(os.path.dirname(__file__), "../overlays/audio/invisible.mp4")
    ])

def trigger_cinematic(match_pos):
    x, y = match_pos
    subprocess.Popen(["python3", CINEMATIC_SCRIPT, str(x), str(y)])
    play_audio()

if __name__ == "__main__":
    references = load_references()
    print("Loaded reference images.")
    cooldown = 30
    last_trigger = 0

    while True:
        now = time.time()
        if now - last_trigger < cooldown:
            time.sleep(2)
            continue

        screen_gray, screen_color = capture_screen()
        matched, name, match_pos = match_screen_to_refs(screen_gray, references)

        if matched:
            print(f"Metal Gear detected via: {name} at {match_pos}")
            trigger_cinematic(match_pos)
            last_trigger = now
            continue

        ocr_matched, ocr_pos = check_ocr_keywords(screen_color)
        if ocr_matched:
            print(f"OCR match at {ocr_pos}")
            trigger_cinematic(ocr_pos)
            last_trigger = now

        time.sleep(2)
