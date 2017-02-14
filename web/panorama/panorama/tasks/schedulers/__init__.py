from . import schedule_face_detection, schedule_rendering, schedule_dlib_detection, schedule_blurring, \
    schedule_lp_detection, schedule_profiles

schedulers = [
    schedule_blurring.BlurScheduler,
    schedule_profiles.ProfileDetectionScheduler,
    schedule_dlib_detection.FaceDetection2Scheduler,
    schedule_face_detection.FaceDetectionScheduler,
    schedule_lp_detection.LpDetectionScheduler,
    schedule_rendering.RenderScheduler
]
