from . import face_detected, licenseplate_detected, dlib_face_detected, blurring_done, \
    google_face_detected, panorama_rendered

listeners = [
    panorama_rendered.RenderingDone,
    blurring_done.BlurDone,
    dlib_face_detected.FaceDone,
    face_detected.FaceDone,
    google_face_detected.FaceDone,
    licenseplate_detected.LicensePlateDone
]
