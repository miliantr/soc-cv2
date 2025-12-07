import numpy as np
import cv2
from typing import Optional, Tuple, Any

#from src.detection import detection
from detection import detection

def tracking(_img1, _img2):
    template, tmp_cnt, tmp_M = detection(_img1)
    frame, fr_cnt, frame_M = detection(_img2)

    if tmp_cnt is None or fr_cnt is None:
        print("Контуры не найдены")
        return None
    
    _, _, w1, h1 = cv2.boundingRect(tmp_cnt)
    _, _, w2, h2 = cv2.boundingRect(fr_cnt)
    
    if tmp_M["m00"] == 0 or frame_M["m00"] == 0:
        print("Моменты равны нулю, нельзя найти центр")
        return None
    
    cx1, cy1 = int(tmp_M["m10"] / tmp_M["m00"]), int(tmp_M["m01"] / tmp_M["m00"])
    cx2, cy2 = int(frame_M["m10"] / frame_M["m00"]), int(frame_M["m01"] / frame_M["m00"])
    
    x1_start = cx1 - w1 // 2
    y1_start = cy1 - h1 // 2
    x1_end = x1_start + w1
    y1_end = y1_start + h1
    
    x2_start = cx2 - w2 // 2
    y2_start = cy2 - h2 // 2
    x2_end = x2_start + w2
    y2_end = y2_start + h2
    
    def safe_crop(img, x_start, y_start, x_end, y_end):
        img_h, img_w = img.shape[:2]
        
        pad_left = max(0, -x_start)
        pad_top = max(0, -y_start)
        pad_right = max(0, x_end - img_w)
        pad_bottom = max(0, y_end - img_h)

        x_start = max(0, x_start)
        y_start = max(0, y_start)
        x_end = min(img_w, x_end)
        y_end = min(img_h, y_end)

        if x_end <= x_start or y_end <= y_start:
            return None

        cropped = img[y_start:y_end, x_start:x_end].copy()

        if any([pad_left, pad_top, pad_right, pad_bottom]):
            cropped = cv2.copyMakeBorder(
                cropped,
                pad_top, pad_bottom,
                pad_left, pad_right,
                cv2.BORDER_CONSTANT,
                value=[0, 0, 0]
            )
        
        return cropped

    tmp_cut = safe_crop(template, x1_start, y1_start, x1_end, y1_end)
    fr_cut = safe_crop(frame, x2_start, y2_start, x2_end, y2_end)
    
    if tmp_cut is None or fr_cut is None:
        print("Не удалось вырезать области")
        return None

    if tmp_cut.shape != fr_cut.shape:
        h = min(tmp_cut.shape[0], fr_cut.shape[0])
        w = min(tmp_cut.shape[1], fr_cut.shape[1])
        tmp_cut = cv2.resize(tmp_cut, (w, h))
        fr_cut = cv2.resize(fr_cut, (w, h))

    corr_matr = cv2.matchTemplate(tmp_cut, fr_cut, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corr_matr)
    
    print(f"Template center: ({cx1}, {cy1}), size: {w1} x {h1}")
    print(f"Frame center: ({cx2}, {cy2}), size: {w2} x {h2}")
    print(f"Корреляция: {max_val:.4f}")

    cv2.imshow("template_cut", tmp_cut)
    cv2.imshow("frame_cut", fr_cut)
    
    return max_val

def phase_correlation_displacement(_img1, _img2):
    img1, tmp_cnt, tmp_M = detection(_img1)
    img2, fr_cnt, frame_M = detection(_img2)

    F1 = np.fft.fft2(img1)
    F2 = np.fft.fft2(img2)
    
    phase_corr = np.fft.ifft2((F1 * np.conj(F2)) / 
                              np.abs(F1 * np.conj(F2)))

    peak = np.unravel_index(np.argmax(np.abs(phase_corr)), 
                           phase_corr.shape)

    height, width = img1.shape
    dx = peak[1] if peak[1] < width/2 else peak[1] - width
    dy = peak[0] if peak[0] < height/2 else peak[0] - height
    result = cv2.addWeighted(img1, 0.7, img2, 0.5, 0)
    cv2.imshow('Blended Image', result)
    return dx, dy

if __name__ == "__main__":
    img1 = "img/frame_0056.jpg"
    img2 = "img/frame_0057.jpg"
    #tracking(img1, img2)
    x,y = phase_correlation_displacement(img1, img2)
    print(f"Displacement: dx={x}, dy={y}")
    cv2.waitKey(0)