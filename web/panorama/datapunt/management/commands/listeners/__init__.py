from . import render_done, face_detected, licenseplate_detected, dlib_face_detected

listeners = [
    dlib_face_detected.FaceDone,
    render_done.RenderDone,
    face_detected.FaceDone,
    licenseplate_detected.LicensePlateDone
]