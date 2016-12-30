from . import render_done, face_detected, licenseplate_detected, dlib_face_detected, blurring_done, profile_detected

listeners = [
    profile_detected.ProfileDone,
    blurring_done.BlurDone,
    dlib_face_detected.FaceDone,
    render_done.RenderDone,
    face_detected.FaceDone,
    licenseplate_detected.LicensePlateDone
]