import cv2
import mediapipe as mp
import time
import winsound

morse_dict = {
    '.-': 'A',   '-...': 'B', '-.-.': 'C',
    '-..': 'D',  '.': 'E',    '..-.': 'F',
    '--.': 'G',  '....': 'H', '..': 'I',
    '.---': 'J', '-.-': 'K',  '.-..': 'L',
    '--': 'M',   '-.': 'N',   '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S',  '-': 'T',    '..-': 'U',
    '...-': 'V', '.--': 'W',  '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5',
    '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}


def decode_morse(code):
    words = code.strip().split("   ")  
    decoded = []
    for word in words:
        letters = word.strip().split()
        decoded_word = ''.join(morse_dict.get(letter, '?') for letter in letters)
        decoded.append(decoded_word)
    return ' '.join(decoded)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

morse_code = ""
hand_present = False
start_time = 0
last_detection_time = time.time()
gesture_started=False

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        if not hand_present:
            start_time = time.time()
            hand_present = True
        else:
            gesture_duration=time.time()-start_time
            if gesture_duration<0.3:
                continue
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    else:
        if hand_present:
            duration = time.time() - start_time
            if duration < 1.5:
                morse_code += "."
                print("Detected DOT")
                winsound.Beep(1000, 100)  # Frequency 1000 Hz, Duration 100 ms
            else:
                morse_code += "-"
                print("Detected DASH")
                winsound.Beep(1000, 300)  # Longer beep


            hand_present = False
            last_detection_time = time.time()
            time.sleep(1.2) 

    pause_duration=time.time()-last_detection_time
    if not hand_present:
        if 3<pause_duration<4:
            if not morse_code.endswith(" "):
                morse_code+=" "
                print("[Letter Gap Detected]")
        elif pause_duration>=4:
            if not morse_code.endswith("  "):
                morse_code += "  "
                print("[Word Gap Detected]")
    
    cv2.putText(img, f'Morse: {morse_code}', (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.imshow("Morse Code Detector", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nFinal Morse Sequence:", morse_code.strip())
decoded = decode_morse(morse_code.strip())
print("Decoded Text:", decoded)
