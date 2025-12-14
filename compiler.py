# from io import BytesIO

# import onnx
# import torch
# from yolo_model import YOLO as yolo
# from engine import EngineBuilder

# from models.common import PostDetect, optim

# try:
#     import onnxsim
# except ImportError:
#     onnxsim = None


# def compile_model(model_name, shape=[1, 3, 640, 640], device='cuda:0', opset=11, topk=100, simplify=True,
#                   conf_thres=0.25, iou_thres=0.65):
#     PostDetect.conf_thres = conf_thres
#     PostDetect.iou_thres = iou_thres
#     PostDetect.topk = topk
#     b = shape[0]
#     YOLOv8 = YOLO(model_name)
#     model = YOLOv8.model.fuse().eval()
#     for m in model.modules():
#         optim(m)
#         m.to(device)
#     model.to(device)
#     fake_input = torch.randn(shape).to(device)
#     for _ in range(2):
#         model(fake_input)
#     save_path = model_name.replace('.pt', '.onnx')
#     with BytesIO() as f:
#         torch.onnx.export(
#             model,
#             fake_input,
#             f,
#             opset_version=opset,
#             input_names=['images'],
#             output_names=['num_dets', 'bboxes', 'scores', 'labels'])
#         f.seek(0)
#         onnx_model = onnx.load(f)
#     onnx.checker.check_model(onnx_model)
#     shapes = [b, 1, b, topk, 4, b, topk, b, topk]
#     for i in onnx_model.graph.output:
#         for j in i.type.tensor_type.shape.dim:
#             j.dim_param = str(shapes.pop(0))
#     if simplify:
#         try:
#             onnx_model, check = onnxsim.simplify(onnx_model)
#             assert check, '[Compiler] WARNING: assert check failed'
#         except Exception as e:
#             print(f'[Compiler] ERROR: Simplifier failure: {e}')
#     onnx.save(onnx_model, save_path)
#     print(f'[Compiler] INFO: ONNX export success, saved as {save_path}')

import os

__all__ = []


def __dir__():
    return []


def autocompile(settings):

    aim_model = None
    trigger_model = None

    if settings.aim_model_name == 'color':
        aim_model = 'color'
    if settings.trigger_model_name == 'color':
        trigger_model = 'color'
    if not aim_model == trigger_model == 'color':
        from ultralytics import YOLO

    if settings.rtx_gpu and settings.cuda_runtime == 'trt':
        task = 'detect'

        if settings.aim_model_name[-5:] == '-pose':
            task = 'pose'

        if not aim_model:
            try:
                print(f'[Main] [I]: Runtime: ({settings.cuda_runtime}). Loading aim model')
                aim_model = YOLO(settings.aim_model_name + f"{settings.neural_input_area_size}.engine", task=task)
            except FileNotFoundError:
                print('[Main] [I]: TensorRT aim model not found. Compiling new one...')
                try:
                    model = YOLO(settings.aim_model_name + ".pt")
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.aim_model_name, '.pt', sep='')
                    return False, None, None
                model.export(format='engine', imgsz=(settings.neural_input_area_size, settings.neural_input_area_size),
                             half=True, device=int(settings.device[-1:]), nms=True)
                os.rename(settings.aim_model_name + '.engine', settings.aim_model_name +
                          f'{settings.neural_input_area_size}.engine')
                print('[Compiler] [I]: Successfully compiled TensorRT model ',
                      settings.aim_model_name + f'{settings.neural_input_area_size}.engine', sep='')
                print('[Main] [I]: Loading aim model')
                aim_model = YOLO(settings.aim_model_name + f'{settings.neural_input_area_size}.engine', task=task)

        if not trigger_model:
            try:
                print(f'[Main] [I]: Runtime: ({settings.cuda_runtime}). Loading trigger model')
                trigger_model = YOLO(settings.trigger_model_name + f"{settings.neural_input_area_size}.engine",
                                     task='detect')
            except:
                print('[Main] [I]: TensorRT trigger model not found. Compiling new one...')
                try:
                    model = YOLO(settings.trigger_model_name + '.pt')
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.trigger_model_name, '.pt', sep='')
                    return False, None, None
                model.export(format='engine', imgsz=(settings.neural_input_area_size, settings.neural_input_area_size),
                             half=True, device=int(settings.device[-1:]))
                os.rename(settings.trigger_model_name + '.engine', settings.trigger_model_name +
                          f'{settings.neural_input_area_size}.engine')
                print('[Compiler] [I]: Successfully compiled TensorRT model ',
                      settings.trigger_model_name + f'{settings.neural_input_area_size}.engine', sep='')
                print('[Main] [I]: Loading trigger model')
                trigger_model = YOLO(settings.trigger_model_name + f"{settings.neural_input_area_size}.engine",
                                     task='detect')
    else:
        if settings.cuda_runtime not in ['onnx', 'torchscript']:
            if not aim_model:
                print(f'[Main] [I]: Runtime: (torch). Loading aim model')
                try:
                    aim_model = YOLO(settings.aim_model_name + ".pt")
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.aim_model_name, '.pt', sep='')
                    return False, None, None

            if not trigger_model:
                print(f'[Main] [I]: Runtime: (torch). Loading models')
                try:
                    trigger_model = YOLO(settings.trigger_model_name + '.pt')
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.trigger_model_name, '.pt', sep='')
                    return False, None, None
            return True, aim_model, trigger_model

        task = 'detect'

        if settings.aim_model_name[-5:] == '-pose':
            task = 'pose'
        if not aim_model:
            try:
                print(f'[Main] [I]: Runtime: ({settings.cuda_runtime}). Loading aim model')
                aim_model = YOLO(settings.aim_model_name + f"{settings.neural_input_area_size}.{settings.cuda_runtime}",
                                 task=task)
            except FileNotFoundError:
                print(f'[Main] [I]: {settings.cuda_runtime.upper()} aim model not found. Compiling new one...')
                try:
                    model = YOLO(settings.aim_model_name + ".pt")
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.aim_model_name, '.pt', sep='')
                    return False, None, None
                model.export(format=settings.cuda_runtime, imgsz=(settings.neural_input_area_size,
                                                                  settings.neural_input_area_size),
                             device=int(settings.device[-1:]))
                os.rename(settings.aim_model_name + '.' + settings.cuda_runtime,
                          settings.aim_model_name + f'{settings.neural_input_area_size}.{settings.cuda_runtime}')
                print(f'[Compiler] [I]: Successfully compiled {settings.cuda_runtime.upper()} model ',
                      settings.aim_model_name + f'{settings.neural_input_area_size}.{settings.cuda_runtime}', sep='')
                print('[Main] [I]: Loading aim model')
                aim_model = YOLO(settings.aim_model_name + f'{settings.neural_input_area_size}.{settings.cuda_runtime}',
                                 task=task)

        task = 'detect'

        if settings.trigger_model_name[-5:] == '-pose':
            task = 'pose'

        if not trigger_model:
            try:
                print(f'[Main] [I]: Runtime: ({settings.cuda_runtime}). Loading trigger model')
                trigger_model = YOLO(settings.trigger_model_name +
                                     f"{settings.neural_input_area_size}.{settings.cuda_runtime}", task=task)
            except FileNotFoundError:
                print(f'[Main] [I]: {settings.cuda_runtime.upper()} trigger model not found. Compiling new one...')
                try:
                    model = YOLO(settings.trigger_model_name + '.pt')
                except FileNotFoundError:
                    print('[Main] [F]: Cannot load torch model ', settings.trigger_model_name, '.pt', sep='')
                    return False, None, None
                model.export(format=settings.cuda_runtime, imgsz=(settings.neural_input_area_size,
                                                                  settings.neural_input_area_size),
                             device=int(settings.device[-1:]))
                os.rename(settings.trigger_model_name + '.' + settings.cuda_runtime,
                          settings.trigger_model_name + f'{settings.neural_input_area_size}.{settings.cuda_runtime}')
                print(f'[Compiler] [I]: Successfully compiled {settings.cuda_runtime.upper()} model ',
                      settings.aim_model_name + f'{settings.neural_input_area_size}.{settings.cuda_runtime}]', sep='')
                print('[Main] [I]: Loading trigger model')
                trigger_model = YOLO(settings.trigger_model_name +
                                     f"{settings.neural_input_area_size}.{settings.cuda_runtime}", task='detect')

    return True, aim_model, trigger_model
