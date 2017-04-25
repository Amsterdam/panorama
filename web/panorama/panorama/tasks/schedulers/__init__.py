from . import schedule_face_detection, schedule_dlib_detection, schedule_blurring, \
    schedule_lp_detection, schedule_google_detection, schedule_pano_rendering

schedulers = [
    schedule_pano_rendering.RenderScheduler,
    schedule_blurring.BlurScheduler,
    schedule_dlib_detection.FaceDetection2Scheduler,
    schedule_face_detection.FaceDetectionScheduler,
    schedule_google_detection.FaceDetection3Scheduler,
    schedule_lp_detection.LpDetectionScheduler,
]
