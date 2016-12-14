from . import detect_faces, detect_lps, render_pano, detect_faces_dlib

workers = [
    detect_faces_dlib.DetectFacesDlib,
    detect_lps.DetectLicensePlates,
    detect_faces.DetectFaces,
    render_pano.RenderPano
]
