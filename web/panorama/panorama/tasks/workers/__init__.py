from . import detect_faces, detect_lps, detect_faces_dlib, blur_regions, detect_faces_google, render_pano

workers = [
    render_pano.RenderPano,
    blur_regions.BlurRegions,
    detect_faces_google.DetectFacesGoogle,
    detect_faces_dlib.DetectFacesDlib,
    detect_lps.DetectLicensePlates,
    detect_faces.DetectFaces,
]
