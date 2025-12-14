__all__ = []


def __dir__():
    return []


from color_boundings import enhanced_image2bboxes
import numpy as np


class Predictor:
    def __init__(self, settings, aim_model, trigger_model, head_conf=0.6, head_thresh=0.12):
        self.imgsz = settings.neural_input_area_size
        self.half = settings.rtx_gpu
        self.device = settings.device
        self.region = settings.region
        self.aim_model = aim_model
        self.trigger_model = trigger_model
        self.lower_color_hsv = settings.lower_color_hsv
        self.upper_color_hsv = settings.upper_color_hsv
        self.morph_iterations = settings.morph_iterations
        self.dilate_iterations = settings.dilate_iterations
        self.morph_kernel = settings.morph_kernel
        self.dilate_kernel = settings.dilate_kernel
        self.min_ratio = settings.min_ratio
        self.max_ratio = settings.max_ratio
        self.use_centroids = settings.use_centroids
        self.thresh = settings.centroids_thresh
        self.aim_model_name = settings.aim_model_name
        self.trigger_model_name = settings.trigger_model_name
        self.detection_classes = settings.detection_classes
        # self.trigger_model_name = 'best'

        self.head_conf = head_conf
        self.head_thresh = head_thresh
        self.is_aim_head = False

    def yolo_pose(self, model, image):
        aims = []

        result = model.predict(source=image, imgsz=self.imgsz, half=self.rtx_gpu,
                            device=self.device, verbose=False)[0]

        predict = result.keypoints.cpu().numpy()
        boxes = result.boxes.data.cpu().numpy()

        if len(predict) == 0:
            return aims, boxes

        for person in predict.data:
            person = person[:5, :]
            thresh = person[:, 2] >= 0.5
            if not thresh.any():
                continue
            mean = person[thresh, :2].mean(0)
            aims.append((np.concatenate((mean, mean)) + [self.region[0] - 1, self.region[1] - 1,
                                                        self.region[0] - 1, self.region[1] - 1]).tolist())

        return aims, boxes


    def yolo_pose_track(self, model, image):
        aims = []

        result = model.track(source=image, imgsz=self.imgsz, half=self.rtx_gpu,
                            device=self.device, verbose=False, tracker='botsort.yaml')[0]

        predict = result.keypoints.cpu().numpy()
        boxes = result.boxes.data.cpu().numpy()

        if len(predict) == 0:
            return aims, boxes

        for person in predict.data:
            person = person[:5, :]
            thresh = person[:, 2] >= 0.5
            if not thresh.any():
                continue
            mean = person[thresh, :2].mean(0)
            aims.append((np.concatenate((mean, mean)) + [self.region[0] - 1, self.region[1] - 1,
                                                        self.region[0] - 1, self.region[1] - 1]).tolist())

        return aims, boxes


    def yolo(self, model, image):
        aims = []

        boxes = model.predict(source=image, imgsz=self.imgsz,
                            device=self.device, verbose=False)[0].boxes.data.cpu().numpy()

        # half=settings.rtx_gpu

        if len(boxes) == 0:
            return aims, boxes

        for box in boxes:
            if round(box[5]) in self.detection_classes:
                aims.append([box[0] + self.region[0] - 1, box[1] + self.region[1] - 1,
                            box[2] + self.region[0] - 1, box[3] + self.region[1] - 1])

        return aims, boxes


    def color_boundings(self, image):
        aims = []

        boxes = enhanced_image2bboxes(image, self.lower_color_hsv, self.upper_color_hsv,
                                    morph_iterations=self.morph_iterations,
                                    dilate_iterations=self.dilate_iterations, morph_kernel=self.morph_kernel,
                                    dilate_kernel=self.dilate_kernel,
                                    min_ratio=self.min_ratio, max_ratio=self.max_ratio, use_centroids=self.use_centroids, 
                                    thresh=self.thresh)

        if len(boxes) == 0:
            return aims, boxes

        for box in boxes:
            aims.append([box[0] + self.region[0] - 1, box[1] + self.region[1] - 1,
                        box[2] + self.region[0] - 1, box[3] + self.region[1] - 1])

        return aims, boxes


    def yolo_get_aims(self, model_type: str, image):
        if model_type == 'aim':
            if self.aim_model_name[-5:] == '-pose':
                return self.yolo_pose(self.aim_model, image)
            elif self.aim_model == 'color':
                return self.color_boundings(image)
            else:
                return self.yolo(self.aim_model, image)
        else:
            if self.trigger_model_name[-5:] == '-pose':
                return self.yolo_pose(self.trigger_model, image)
            elif self.trigger_model == 'color':
                return self.color_boundings(image)
            else:
                return self.yolo(self.trigger_model, image)
