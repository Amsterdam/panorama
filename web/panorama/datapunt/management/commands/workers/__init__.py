from . import detect_faces, detect_lps, render_pano

workers = [
    detect_lps.DetectLicensePlates,
    detect_faces.DetectFaces,
    render_pano.RenderPano
]
