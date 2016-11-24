from . import render_done, face_detected, licenseplate_detected

listeners = [
    render_done.RenderDone,
    face_detected.FaceDone,
    licenseplate_detected.LicensePlateDone
]