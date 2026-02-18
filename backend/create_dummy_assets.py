import cv2
import numpy as np
import os

os.makedirs('assets/merch', exist_ok=True)

# Generate simple colored squares as dummy merch designs

try:
    # Design 1: Red
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    img[:] = (0, 0, 255) # BGR -> Red
    cv2.imwrite('assets/merch/design1.png', img)
    print("Created design1.png")

    # Design 2: Blue
    img[:] = (255, 0, 0) # BGR -> Blue
    cv2.imwrite('assets/merch/design2.png', img)
    print("Created design2.png")

    # Design 3: Green
    img[:] = (0, 255, 0) # BGR -> Green
    cv2.imwrite('assets/merch/design3.png', img)
    print("Created design3.png")

except Exception as e:
    print(f"Error creating assets: {e}")
