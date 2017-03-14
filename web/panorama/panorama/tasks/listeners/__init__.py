from . import face_detected, licenseplate_detected, dlib_face_detected, blurring_done

listeners = [
    blurring_done.BlurDone,
    dlib_face_detected.FaceDone,
    face_detected.FaceDone,
    licenseplate_detected.LicensePlateDone
]
