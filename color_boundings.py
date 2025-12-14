__all__ = []


def __dir__():
    return []


import cv2
import numpy as np


def merge_boxes(boxes, x_val, y_val):
    size = len(boxes)
    if size < 2:
        return boxes

    if size == 2:
        if boxes_merge_able(boxes[0], boxes[1], x_val, y_val):
            boxes[0] = union(boxes[0], boxes[1])
            del boxes[1]
        return boxes

    boxes = sorted(boxes, key=lambda r: r[0])
    i = size - 2
    while i >= 0:
        if boxes_merge_able(boxes[i], boxes[i + 1], x_val, y_val):
            boxes[i] = union(boxes[i], boxes[i + 1])
            del boxes[i + 1]
        i -= 1
    return boxes


def boxes_merge_able(box1, box2, x_val, y_val):
    (x1, y1, w1, h1) = box1
    (x2, y2, w2, h2) = box2
    return max(x1, x2) - min(x1, x2) - minx_w(x1, w1, x2, w2) < x_val \
        and max(y1, y2) - min(y1, y2) - miny_h(y1, h1, y2, h2) < y_val


def minx_w(x1, w1, x2, w2):
    return w1 if x1 <= x2 else w2


def miny_h(y1, h1, y2, h2):
    return h1 if y1 <= y2 else h2


def union(a, b):
    x = min(a[0], b[0])
    y = min(a[1], b[1])
    w = max(a[0] + a[2], b[0] + b[2]) - x
    h = max(a[1] + a[3], b[1] + b[3]) - y
    return x, y, w, h


def divide_line(a, b, divisions):
    divided = []
    if len(divisions) == 0:
        return divided, a, b
    if len(divisions) == 1:
        if divisions[0] <= (a + b) / 2:
            divided.append((a, divisions[0] * 2 - a))
            a = divisions[0] * 2 - a
        else:
            divided.append((divisions[0] * 2 - b, b))
            b = divisions[0] * 2 - b
        return divided, a, b
    elif len(divisions) == 2:
        if min(abs(divisions[0] - a), abs(divisions[0] - b)) <= min(abs(divisions[-1] - a), abs(divisions[-1] - b)):
            r_divd, a, b = divide_line(a, b, [divisions.pop(0)])
            divided += r_divd
        else:
            r_divd, a, b = divide_line(a, b, [divisions.pop(-1)])
            divided += r_divd
        r_divd, a, b = divide_line(a, b, divisions)
        return divided + r_divd, a, b
    else:
        while len(divisions) > 1:
            r_divs = [divisions.pop(0), divisions.pop(-1)]
            r_divd, a, b = divide_line(a, b, r_divs)
            divided += r_divd
        r_divd, a, b = divide_line(a, b, divisions)
        return divided + r_divd, a, b


def remove_innerboxes(boxes, x_thres=0, y_thres=0):
    remove_idx = set()
    for i, box1 in enumerate(boxes):
        x1, y1, w1, h1 = box1
        for j, box2 in enumerate(boxes):
            if i == j:
                continue
            x2, y2, w2, h2 = box2
            if x1 - x_thres <= x2 <= w2 <= w1 + x_thres and y1 - y_thres <= y2 <= h2 <= h1 + y_thres:
                remove_idx.add(j)
    idx = {i for i in range(len(boxes))}
    idx.difference_update(remove_idx)
    boxes = [boxes[i] for i in idx]
    return boxes


def hex2rgb(hex_color: str):
    return tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))


def filter_bboxes(bboxes, centroids, min_ratio=0.33, max_ratio=0.93):
    filtered_boxes = []
    # print('центроиды ', centroids)
    for bbox in bboxes:
        x1, y1, w, h = bbox
        x2, y2 = x1 + w, y1 + h
        ratio = w / h
        if min_ratio <= ratio <= max_ratio:
            # bbox_centroids = []
            x_sort = []
            # print('Бокс', x1, x2)
            for centroid in centroids:
                if x1 <= centroid[0] <= x2 and y1 <= centroid[1] <= y2:
                    # bbox_centroids.append(centroid)
                    # centroids.remove(centroid)
                    x_sort.append(centroid[0])
            
            x_sort.sort()
            if len(x_sort) != 0:
                divided_x = divide_line(x1, x2, x_sort)[0]
                # print('Координаты центроидов', x_sort)
                # print('Разделенные боксы', divided_x)
                for (xs1, xs2) in divided_x:
                    filtered_boxes.append((xs1, y1, xs2, y2))
                    # print('РБокс ', (xs1, y1, xs2, y2))
            else:
                filtered_boxes.append((x1, y1, x2, y2))
    return filtered_boxes


def image2bboxes(image_bgr, lower_color_hex, upper_color_hex, merge_x_thres=40, merge_y_thres=50, overlap_x_thres=20,
                 overlap_y_thres=20, morph_kernel=(2, 2), dilate_kernel=(2, 2), morph_iterations=1,
                 dilate_iterations=2):
    # Convert image to HSV color space
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # Convert HEX colors to HSV
    lower_color_rgb = hex2rgb(lower_color_hex)
    upper_color_rgb = hex2rgb(upper_color_hex)

    lower_color_hsv = cv2.cvtColor(np.array(lower_color_rgb, dtype='uint8').reshape((1, 1, 3)), cv2.COLOR_RGB2HSV)[0, 0]
    upper_color_hsv = cv2.cvtColor(np.array(upper_color_rgb, dtype='uint8').reshape((1, 1, 3)), cv2.COLOR_RGB2HSV)[0, 0]

    # Create a binary mask for the color range
    mask = cv2.inRange(image_hsv, lower_color_hsv, upper_color_hsv)

    # Apply morphological and dilation operations to remove noise
    morph_kernel = np.ones(morph_kernel, np.uint8)
    dilate_kernel = np.ones(dilate_kernel, np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel, iterations=morph_iterations)
    mask = cv2.dilate(mask, dilate_kernel, iterations=dilate_iterations)

    # Find contours of objects in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extracting bboxes from contours
    bboxes = [cv2.boundingRect(c) for c in contours]

    # Merging close bboxes
    bboxes = merge_boxes(bboxes, x_val=merge_x_thres, y_val=merge_y_thres) # Where x_val and y_val are axis thresholds

    # Convert bboxes from xywh to xyxy format
    bboxes = [(x, y, x + w, y + h) for x, y, w, h in bboxes]

    # Remove overlapping bboxes
    bboxes = remove_innerboxes(bboxes, x_thres=overlap_x_thres, y_thres=overlap_y_thres)

    return bboxes


def get_centroids(mask, thresh=0.5):
    dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    ret, blobs = cv2.threshold(dist_transform, thresh*dist_transform.max(), 255, 0)

    blobs = np.uint8(blobs)

    # cv2.imshow('Result', blobs)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Finding centroids from blobs
    contours, hierarchy = cv2.findContours(blobs,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    centroids = []
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        # calculate x,y coordinate of center
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centroids.append((cX, cY))
    
    return centroids


def smart_inrange_hsv(image_hsv, lower_hsv, upper_hsv):
    """
    Возвращает маску, используя наименьший по длине диапазон Hue с учётом wrap-around.
    lower_hsv и upper_hsv — кортежи (H, S, V), где H в [0,179].
    """
    lh, ls, lv = lower_hsv
    uh, us, uv = upper_hsv
    max_h = 180

    # вычисляем две длины: прямую и через границу 0-179
    if lh <= uh:
        direct_len = uh - lh
        wrap_len = lh + (max_h - uh)
    else:
        direct_len = (uh + max_h) - lh
        wrap_len = lh - uh

    if direct_len <= wrap_len:
        # обычный диапазон без перехода через 0
        mask = cv2.inRange(image_hsv, (lh, ls, lv), (uh, us, uv))
    else:
        # «короткий» диапазон — через границу 179→0
        # объединяем два интервала: [lh..179] и [0..uh]
        mask1 = cv2.inRange(image_hsv, (lh, ls, lv), (max_h-1, us, uv))
        mask2 = cv2.inRange(image_hsv, (0, ls, lv), (uh, us, uv))
        mask = cv2.bitwise_or(mask1, mask2)

    return mask


def enhanced_image2bboxes(image_bgr, lower_color_hsv, upper_color_hsv, morph_kernel=(5, 5), dilate_kernel=(3, 3),
                          morph_iterations=10, dilate_iterations=2, min_ratio=0.33, max_ratio=0.93, thresh=0.7, use_centroids=True):
    # Convert image to HSV color space
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # print(lower_color_hsv, upper_color_hsv)

    # Create a binary mask for the color range

    mask = smart_inrange_hsv(image_hsv, lower_color_hsv, upper_color_hsv)
    # mask = cv2.inRange(image_hsv, lower_color_hsv, upper_color_hsv)

    # cv2.imshow('Result', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Apply morphological operations
    morph_kernel = np.ones(morph_kernel, np.uint8)
    dilate_kernel = np.ones(dilate_kernel, np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, dilate_kernel, iterations=dilate_iterations)
    # cv2.imshow('Result', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if morph_iterations != 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel, iterations=morph_iterations)
        mask = cv2.dilate(mask, morph_kernel, morph_iterations)
    
    # cv2.imshow('Result', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if use_centroids:
        centroids = get_centroids(mask, thresh)
    else:
        centroids = []

    # for centroid in centroids:
    #     cv2.circle(image_bgr, centroid, 5, (255, 255, 255), -1)
    
    # mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

    # cv2.imshow('Result', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # mask_del = cv2.dilate(mask, dilate_kernel, iterations=dilate_iterations)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel_2, iterations=2)
    # cv2.imshow('Result', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract bounding boxes and filter them
    bboxes = [cv2.boundingRect(c) for c in contours]

    # Convert bboxes from xywh to xyxy format
    # Adjust bboxes with centroids
    # Filter by aspect ratio
    return filter_bboxes(bboxes, centroids, min_ratio=min_ratio, max_ratio=max_ratio)


if __name__ == '__main__':
    import time

    lower_aim_rgb = hex2rgb('#9b964d')
    upper_aim_rgb = hex2rgb('#fbff00')

    lower_aim_hsv = cv2.cvtColor(np.array(lower_aim_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]
    upper_aim_hsv = cv2.cvtColor(np.array(upper_aim_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]

    image = cv2.imread('test.png')
    # image = image[440:440+200,860:860+200]
    start_time = time.perf_counter()
    # eboxes = image2bboxes(image, '#4b4a41', ) #ff00f7 #68526b
    # eboxes = enhanced_image2bboxes(image, lower_aim_hsv, upper_aim_hsv, morph_iterations=2, dilate_iterations=3, dilate_kernel=(19, 5), morph_kernel=(3, 3), max_ratio=2)
    eboxes = enhanced_image2bboxes(image, lower_aim_hsv, upper_aim_hsv, morph_iterations=1, dilate_iterations=6, dilate_kernel=(17, 3), morph_kernel=(3, 3), max_ratio=3, min_ratio=0, use_centroids=True)
    # eboxes = image2bboxes(image, '#4b4a41', '#a9ff00')
    end_time = time.perf_counter()
    # mask1, mask2, mask3 = image, image, image


    xc, yc = 600, 200
    # image = image[yc:yc+640,xc:xc+640]

    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # print(hsv_image)

    # Define color range to detect
    # lower_color = np.array([0, 100, 100])
    # upper_color = np.array([10, 255, 255])
    lower_color_hsv = np.array([28, 100, 100])
    upper_color_hsv = np.array([60, 255, 255])

    # lower_color_bgr = np.uint8([[[0, 200, 200]]])
    # upper_color_bgr = np.uint8([[[30, 255, 255]]])

    # lower_color_hsv = cv2.cvtColor(lower_color_bgr, cv2.COLOR_BGR2HSV)
    # upper_color_hsv = cv2.cvtColor(upper_color_bgr, cv2.COLOR_BGR2HSV)

    # start_time = time.perf_counter()

    # Create a binary mask for the color range
    mask = cv2.inRange(hsv_image, lower_color_hsv, upper_color_hsv)

    # cv2.imshow('Mask', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Apply morphological operations to remove noise
    kernel = np.ones((2, 2), np.uint8)
    dilate_kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=2)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((4, 4), np.uint8))

    # cv2.imshow('Denoised', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Find contours of objects in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = [cv2.boundingRect(c) for c in contours]
    boxes = merge_boxes(boxes, x_val=40, y_val=50) # Where x_val and y_val are axis thresholds

    boxes = [(x, y, x + w, y + h) for x, y, w, h in boxes]

    # scores = [0.9] * len(boxes)

    # score_threshold = 0.5
    # nms_threshold = 0.8

    # indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold, nms_threshold)

    # print(indices)

    # filtered_boxes = [boxes[i] for i in indices]
    filtered_boxes = remove_innerboxes(boxes, x_thres=20, y_thres=20)

    # print(filtered_boxes)

    # end_time = time.perf_counter()

    # Draw bounding boxes around objects
    for box in eboxes:
        x, y, width, height = box
        cv2.rectangle(image, (x, y), (width, height), (255, 0, 0), 1)

    # Display result
    print((end_time-start_time)*1000)

    # cv2.imshow('Result', mask1)
    # cv2.waitKey(0)
    # cv2.imshow('Result', mask2)
    # cv2.waitKey(0)
    # cv2.imshow('Result', mask3)
    # cv2.waitKey(0)
    cv2.imshow('Result', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()