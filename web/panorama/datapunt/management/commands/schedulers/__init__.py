from . import schedule_detection, schedule_rendering, schedule_dlib_detection

schedulers = [
    schedule_detection.DetectionScheduler,
    schedule_dlib_detection.FaceDetection2Scheduler,
#    schedule_rendering.RenderScheduler
]