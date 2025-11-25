import os
import subprocess
import cv2

def mp4_to_gif_cv2(input_mp4, output_gif, max_width=800, max_fps=24, brighten=0.06):
    """
    Convert an MP4 video to a high-quality GIF using ffmpeg, adapting
    fps and resolution from the input video.

    Args:
        input_mp4 : str  - path to input MP4
        output_gif: str  - path to output GIF
        max_width : int  - upper bound on GIF width (keep aspect ratio)
        max_fps   : int  - upper bound on GIF fps
        brighten  : float - ffmpeg eq brightness offset
                           (~0.0 original, 0.05–0.12 is a slight boost)
    """

    # --- 1) Read original FPS and width via OpenCV ---
    cap = cv2.VideoCapture(input_mp4)
    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap.release()

    # Fallbacks in case reading fails
    if orig_fps <= 1 or orig_fps != orig_fps:  # NaN or 0
        orig_fps = 24
    if orig_width <= 1 or orig_width != orig_width:
        orig_width = max_width

    # Use at most max_fps, but not higher than original
    fps = min(orig_fps, max_fps)
    fps = int(round(fps))

    # Use at most max_width, but not higher than original
    width = int(min(orig_width, max_width))

    print(f"[INFO] Using fps={fps}, width={width} for GIF.")

    # --- 2) Build filters for ffmpeg ---
    base_filter = f"fps={fps},scale={width}:-1:flags=lanczos"

    if brighten != 0:
        vf_filter = base_filter + f",eq=brightness={brighten}"
    else:
        vf_filter = base_filter

    # Palette path
    base, _ = os.path.splitext(input_mp4)
    palette_path = base + "_palette.png"

    # --- 3) Generate palette ---
    cmd_palette = [
        "ffmpeg", "-y",
        "-i", input_mp4,
        "-vf", f"{vf_filter},palettegen",
        palette_path,
    ]
    subprocess.run(cmd_palette, check=True)

    # --- 4) Use palette to create GIF ---
    filter_complex = f"{vf_filter}[x];[x][1:v]paletteuse=dither=floyd_steinberg"

    cmd_gif = [
        "ffmpeg", "-y",
        "-i", input_mp4,
        "-i", palette_path,
        "-filter_complex", filter_complex,
        output_gif,
    ]
    subprocess.run(cmd_gif, check=True)

    print(f"Conversion completed! GIF saved as {output_gif}")

# Example usage
input_mp4 = "/Users/yiming/old_Documents/research/projects/SplatVoxel/website/SplatVoxel/static/videos/intro_demo.mp4"
output_gif = input_mp4.replace(".mp4", ".gif")
mp4_to_gif_cv2(input_mp4, output_gif)
