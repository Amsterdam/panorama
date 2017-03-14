from . import schedule_face_detection, schedule_dlib_detection, schedule_blurring, schedule_lp_detection

schedulers = [
    schedule_blurring.BlurScheduler,
    schedule_dlib_detection.FaceDetection2Scheduler,
    schedule_face_detection.FaceDetectionScheduler,
    schedule_lp_detection.LpDetectionScheduler,
]
