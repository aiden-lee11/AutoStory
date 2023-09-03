from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, concatenate_videoclips
from credentials import MyCreds
import csv, os, re
from reddit_scraper import scraper
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip  
from audio_tts_timestamps import tts
from pydub import AudioSegment
import random
from uploader import uploader
import pyautogui



AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

titles = []
post_texts = []
ids = []
authors = []
video_durations =[]
video_paths = []
def get_paths(id, title):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    background_video_path = os.path.join(script_directory, 'Background_Videos', 'mc_parkour.mkv')
    tts_audio_path = os.path.join(script_directory, f"{title}.mp3")
    completed_videos_folder = os.path.join(script_directory, 'completed_videos')
    output_video_filename = f"{title}.mp4"
    output_video_path = os.path.join(completed_videos_folder, output_video_filename)
    return background_video_path, output_video_path, tts_audio_path

def clean_file_name(file_name):
    # Remove invalid characters from the file name
    cleaned_name = re.sub(r'[\/:*?"<>|]', '', file_name[2:])
    return cleaned_name

def create_tts_audio(text, output_path):
    tts = gTTS(text, lang='en', tld='com.au') #https://gtts.readthedocs.io/en/latest/module.html#localized-accents
    tts.save(output_path)

def create_tts_word_objs(mp3_name):
    sound = AudioSegment.from_mp3(mp3_name)
    sound.export(mp3_name.replace(".mp3", ".wav"), format="wav")
    print(mp3_name.replace(".mp3", ".wav"))
    return tts(mp3_name.replace(".mp3", ".wav"))

    

def combine_audio_with_video(audio_path, video_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    video_clip = VideoFileClip(video_path)
    
    audio_duration = int(audio_clip.duration)
    video_duration = int(video_clip.duration)
    starter_point = random.randint(0, video_duration - audio_duration)
    
    video_clip = video_clip.subclip(starter_point, starter_point + audio_duration)
    
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec="libx264")
    return final_clip
    
    
def clean_text(text):
    # Encode the text using 'ignore' error handling to remove unsupported characters
    cleaned_text = text.encode('utf-8', 'ignore').decode('utf-8')
    return cleaned_text

def reader(csv_file):
    
    with open(csv_file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Read the header row
        
        for row in csv_reader:
            title = row[0]
            post_text = row[1]
            post_id = row[2]
            author = row[3]
            
            cleaned_post_text = clean_text(post_text)
            
            titles.append(title)
            post_texts.append(cleaned_post_text)
            ids.append(post_id)
            authors.append(author)

def make_vids():
    for i in range(len(titles)):
        paths = get_paths(id = ids[i], title = titles[i])
        input_text = titles[i] + post_texts[i]
        background_video_path, output_video_path, tts_audio_path  = clean_file_name(paths[0]), clean_file_name(paths[1]), clean_file_name(paths[2])
        video_paths.append(output_video_path)
        #print(output_video_path)      C:\Users\Villa\OneDrive\desktop\CS\Reddit-TikTok\completed_videos\Good news - I'm back!.mp4

        create_tts_audio(input_text, tts_audio_path)
        final_clip = combine_audio_with_video(tts_audio_path, background_video_path, output_video_path)   
        
        subtitle_clips = []
        word_objs = create_tts_word_objs(mp3_name=tts_audio_path)
        for k, word in enumerate(word_objs):
            word_duration = word.end - word.start
            if k > 0:
                word_duration += (word.start - word_objs[k - 1].end) #adjusting slightly for difference pauses in the tts that captions struggle with
            subtitle = TextClip(word.word, fontsize=100, color='white', method='caption', font='Arial-Bold')
            subtitle = subtitle.set_duration(word_duration).set_start(word.start)
            subtitle_clips.append(subtitle)
            
            

        # Concatenate the subtitle clips
        concatenated_subtitles = concatenate_videoclips(subtitle_clips, method="compose").set_position(('center', 'center'))

        # Overlay concatenated subtitles onto the video
        video_with_subtitles = CompositeVideoClip([final_clip, concatenated_subtitles])

        # Write the final video with subtitles
        video_with_subtitles.write_videofile(output_video_path, codec="libx264")
        video_durations.append(video_with_subtitles.duration)
        
        if os.path.exists(tts_audio_path):
            os.remove(tts_audio_path)
            os.remove(tts_audio_path.replace('.mp3', '.wav'))
            
    return uploader(video_paths=video_paths, titles=titles, authors=authors, video_durs=video_durations)

if __name__ == "__main__":
    subreddit = pyautogui.prompt(text='Which Subreddit would you like to scrape?', title='AutoStory')
    time = pyautogui.prompt('What time frame? ("all", "day", "hour", "month", "week", or "year")', title='AutoStory')
    num_posts = int(pyautogui.prompt(text='How many posts?', title='AutoStory'))
    csv_file = scraper(subreddit=subreddit,time_filter=time,num_posts=num_posts)
    reader(csv_file=csv_file)
    print(make_vids())
    
    
