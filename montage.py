import os
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
from moviepy.video.fx import all as vfx
from moviepy.video.VideoClip import ImageSequenceClip

def add_noise(clip, noise_level=0.05):
    """إضافة تأثير ضوضاء (Noise) إلى مقطع الفيديو."""
    # إنشاء طبقة من الضوضاء باستخدام numpy
    def make_frame(t):
        frame = clip.get_frame(t)
        noise = np.random.normal(scale=255 * noise_level, size=frame.shape).astype('uint8')
        noisy_frame = np.clip(frame + noise, 0, 255).astype('uint8')
        return noisy_frame

    # تطبيق الضوضاء على الفيديو باستخدام make_frame
    return clip.fl(make_frame)

def create_video_with_audio_and_noise(image_folder, audio_file, output_file, duration_per_image=4, zoom_factor=1.1, noise_level=0.05):
    # قراءة الصوت
    audio_clip = AudioFileClip(audio_file)
    
    # قائمة لحفظ مقاطع الفيديو التي تحتوي على الصور
    video_clips = []

    # قراءة كل الصور من المجلد
    for image_file in sorted(os.listdir(image_folder)):
        if image_file.endswith(('.png', '.jpg', '.jpeg')):
            # قراءة الصورة
            image_path = os.path.join(image_folder, image_file)
            image_clip = ImageClip(image_path)

            # تعيين مدة الصورة (4 ثوانٍ)
            image_clip = image_clip.set_duration(duration_per_image)

            # تطبيق تأثير Zoom In (التكبير التدريجي)
            zoomed_clip = image_clip.fx(vfx.zoom_in, factor=zoom_factor, duration=duration_per_image)

            # إضافة تأثير الضوضاء (Noise) على الصورة
            noisy_clip = add_noise(zoomed_clip, noise_level)

            # إضافة الصورة (المقطع) إلى قائمة مقاطع الفيديو
            video_clips.append(noisy_clip)
    
    # دمج جميع مقاطع الفيديو في فيديو واحد
    final_video = concatenate_videoclips(video_clips, method="compose")

    # إضافة الصوت إلى الفيديو
    final_video = final_video.set_audio(audio_clip)
    
    # ضبط مدة الفيديو لتكون مساوية لملف الصوت
    final_video = final_video.set_duration(audio_clip.duration)

    # تصدير الفيديو النهائي
    final_video.write_videofile(output_file, fps=24)

# استخدام السكربت
image_folder = "images"  # المجلد الذي يحتوي على الصور
audio_file = "audio.mp3"  # مسار ملف الصوت
output_file = "output_video_with_noise.mp4"  # اسم ملف الفيديو النهائي

# إنشاء الفيديو مع إضافة الضوضاء
create_video_with_audio_and_noise(image_folder, audio_file, output_file)
