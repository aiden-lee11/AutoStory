from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, concatenate_videoclips
from credentials import MyCreds
import csv, os
from reddit_scraper import scraper
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip  
from audio_tts_timestamps import tts
from pydub import AudioSegment


titles = []
post_texts = []
ids = []

def get_paths(id, title):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    background_video_path = os.path.join(script_directory, 'Background_Videos', 'trimmed_test.mp4')
    tts_audio_path = os.path.join(script_directory, f"{title[:30]}_{id}.mp3")
    completed_videos_folder = os.path.join(script_directory, 'completed_videos')
    output_video_filename = f"{title[:30]}_{id}.mp4"
    output_video_path = os.path.join(completed_videos_folder, output_video_filename)
    return background_video_path, output_video_path, tts_audio_path


def create_tts_audio(text, output_path):
    tts = gTTS(text, lang='en')
    tts.save(output_path)

def create_tts_word_objs(mp3_name):
    sound = AudioSegment.from_mp3(mp3_name)
    sound.export(mp3_name.replace(".mp3", ".wav"), format="wav")
    return mp3_name.replace(".mp3", ".wav")

    

def combine_audio_with_video(audio_path, video_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec="libx264")
    
    
def clean_text(text):
    # Encode the text using 'ignore' error handling to remove unsupported characters
    cleaned_text = text.encode('utf-8', 'ignore').decode('utf-8')
    return cleaned_text

def reader():
    mycreds = MyCreds()
    
    with open(mycreds.path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Read the header row
        
        for row in csv_reader:
            title = row[0]
            post_text = row[1]
            post_id = row[2]
            
            cleaned_post_text = clean_text(post_text)
            
            titles.append(title)
            post_texts.append(cleaned_post_text)
            ids.append(post_id)

def make_vids():
    for i in range(len(titles)):
        paths = get_paths(id = ids[i], title = titles[i])
        input_text = titles[i] + post_texts[i]
        background_video_path, output_video_path, tts_audio_path  = paths[0], paths[1], paths[2]
        create_tts_audio(input_text, tts_audio_path)
        combine_audio_with_video(tts_audio_path, background_video_path, output_video_path)
        
        video_clip = VideoFileClip(background_video_path)
        audio_clip = AudioFileClip(tts_audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        
        video_width, video_height = video_clip.size
        
        subtitle_clips = []
        
        words = create_tts_word_objs(mp3_name=tts_audio_path)
        print(words)
        for j, word in enumerate(words):
            subtitle = TextClip(word, fontsize=50, color='yellow', bg_color='black', size=(video_width*3/4, None), method='caption')
            subtitle = subtitle.set_duration(word_duration).set_start(j * word_duration)
            text_pos = ('center', 'bottom')
            subtitle_clips.append(subtitle.set_position(text_pos))
            

        # Concatenate the subtitle clips
        concatenated_subtitles = concatenate_videoclips(subtitle_clips, method="compose")

        # Overlay concatenated subtitles onto the video
        video_with_subtitles = CompositeVideoClip([final_clip, concatenated_subtitles])

        # Write the final video with subtitles
        video_with_subtitles.write_videofile(output_video_path, codec="libx264")
        if os.path.exists(tts_audio_path):
            os.remove(tts_audio_path)
    return "Successfully Made Videos"

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

if __name__ == "__main__":
    if input('Would you like to rescrape? (y/n) \n') == 'y':
        subreddit = input('Which Subreddit would you like to scrape? \n')
        time = input('What time frame? \n')
        num_posts = int(input('How many posts? \n'))
        print("Scraping Reddit...")
        scraper(subreddit=subreddit,time_filter=time,num_posts=num_posts)
    else:
        print("Skipping scraping.")
    
    reader()
    print(make_vids())
