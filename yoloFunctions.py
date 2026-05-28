import math
from collections import deque

pose_history = deque(maxlen=5)

def is_horse_down(outputs):
    if outputs is None or len(outputs) == 0:
        return None

    data = outputs[0]

    if len(data.shape) == 3:
        data = data[0]

    if len(data) == 0:
        return None

    det = data[0]

    keypoints_raw = det[5:]

    keypoints = [(keypoints_raw[i], keypoints_raw[i+1]) 
                 for i in range(0, len(keypoints_raw) - 2, 3)]

    if len(keypoints) < 4:
        return None

    def pt(i):
        return float(keypoints[i][0]), float(keypoints[i][1])

    def angle(a, b):
        return abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))

    try:
        head = pt(0)
        mid1 = pt(len(keypoints) // 4)
        mid2 = pt(len(keypoints) // 2)
        rear = pt(3 * len(keypoints) // 4)
    except IndexError:
        return None

    if any(x == 0.0 and y == 0.0 for x, y in [head, mid1, mid2, rear]):
        return None

    angles = [
        angle(head, mid2),
        angle(mid1, mid2),
        angle(mid2, rear)
    ]

    main_angle = angle(head, rear)

    print(f"Hoved-til-bagkrop vinkel: {main_angle:.1f} grader")

    is_laying_now = (main_angle < 45 or main_angle > 135)

    pose_history.append(is_laying_now)

    if pose_history.count(True) >= 3:
        return "laying"
    elif pose_history.count(False) >= 3:
        return "standing"

    return None
    
