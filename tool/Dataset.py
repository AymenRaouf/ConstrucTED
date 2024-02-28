from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import pandas as pd
import datetime
import csv
import ast
import re
import os


class Dataset:

    def __init__(
            self, sid, eid, cid, api_key = os.getenv('GOOGLE_API_KEY')):
        self.api_key = api_key
        self.sid = sid
        self.eid = eid
        self.cid = cid
        self.series = []
        self.episodes = []
        self.chapters = []


    def extract_instructor_from_description(
            self, description):
        """
        Description : Extracts the instructor from the playlist's description.

        Inputs:
        - description : str - Playlist's description

        Outputs:
        - instructor : str - Instructor's name extracted from the description
        """
        description = description.lower()
        formulations = ['teacher', 'instructor', 'professor']
                
        pattern_instructor = r'(?<=instructor: )\w+ \w+'
        match_instructor = re.search(pattern_instructor, description)
        pattern_teacher = r'(?<=teacher: )\w+ \w+'
        match_teacher = re.search(pattern_teacher, description)
        pattern_professor = r'(?<=professor: )\w+ \w+'
        match_professor = re.search(pattern_professor, description)
        if match_instructor:
            instructor = match_instructor.group(0)
            return instructor
        elif match_teacher:
            teacher = match_teacher.group(0)
            return teacher
        elif match_professor:
            professor = match_professor.group(0)
            return professor
        else:
            return None
    
    def to_dict(self):
        self.series = {
            'Sid' : [serie.sid for serie in self.series],
            'Category' : [serie.category for serie in self.series],
            'Title' : [serie.name for serie in self.series],
            'Professor' : [serie.professor for serie in self.series],
            'Created at' : [serie.created_at for serie in self.series],
            'Corpus' : [serie.corpus for serie in self.series],
            'Description' : [serie.description for serie in self.series],
            'Course' : [serie.course for serie in self.series]
        }
        self.episodes = {
            'Eid' : [episode.eid for episode in self.episodes],
            'Sid' : [episode.sid for episode in self.episodes],
            'Order' : [episode.order_series for episode in self.episodes],
            'Title' : [episode.title for episode in self.episodes],
            'Created at' : [episode.created_at for episode in self.episodes],
            'Description' : [episode.description for episode in self.episodes],
            'Course' : [episode.course for episode in self.episodes]
        }
        self.chapters = {
            'Cid' : [chapter.cid for chapter in self.chapters],
            'Eid' : [chapter.eid for chapter in self.chapters],
            'Title' : [chapter.title for chapter in self.chapters],
            'Text' : [chapter.text for chapter in self.chapters],
            'Begin' : [chapter.begin for chapter in self.chapters],
            'End' : [chapter.end for chapter in self.chapters]
        }
    def save(
                self, path = './'):
            script_dir = os.path.dirname(os.path.realpath('__file__'))
            path = os.path.join(script_dir, path + '/')
            self.to_dict()
            self.series = pd.DataFrame(self.series)
            self.episodes = pd.DataFrame(self.episodes)
            self.chapters = pd.DataFrame(self.chapters)
            self.series.to_csv(path + 'series.csv', index = False, sep = '|')
            self.episodes.to_csv(path + 'episodes.csv', index = False, sep = '|')
            self.chapters.to_csv(path + 'chapters.csv', index = False, sep = '|')

    def create_chapters(
                self, video_id, title, max_time = 3600, min_segment_duration = 1200, unwanted_words = None):
            segments = []
            current_segment = ''
            current_duration = 0
            current_start = 0
            if unwanted_words is None:
                unwanted_words = ['[SQUEAKING]', '[RUSTLING]', '[CLICKING]','\n', '\t', '\r', '|', '[PROFESSOR]', '[Voiceover]', '[AUDIENCE]', '[APPLAUSE]', '[INAUDIBLE]', '[Instructor]']
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-GB', 'en', 'en-US'])
                if transcript :
                    total_duration_seconds = transcript[-1]['start']
                    if total_duration_seconds > max_time:
                        print(f'Extracting subtitles for video {self.cid} with id {video_id} and dividing it')
                        # Divide the transcript into segments of a specified minimal duration
                        for i, line in enumerate(transcript):
                            text = line['text']
                            duration = line['duration']
                            start = line['start']
                            end = start + duration

                            if current_duration + duration > min_segment_duration or i + 1 == len(transcript):
                                current_segment += text + ' '
                                current_duration += duration

                                if text.endswith(('.', '!', '?')) or (current_duration > (min_segment_duration + 120)):
                                    # Add the segment to the segments' list
                                    segments.append((current_segment.strip(), current_start, end))
                                    current_segment = ''
                                    current_duration = 0
                                    current_start = 0
                                    current_end = 0

                            else:
                                if current_duration == 0:
                                    current_start = start

                                current_segment += text + ' '
                                current_duration += duration
                                current_end = end

                        title_number = 0
                        num_parts = len(segments)
                        remaining_duration = total_duration_seconds - segments[-1][1]

                        # Generate the information of chapters for every segment
                        for i, part in enumerate(segments):
                            if i < num_parts - 1:
                                segment_text, segment_start, segment_end = part
                            else:
                                segment_text, segment_start, _ = part
                                segment_end = segment_start + remaining_duration

                            for word in unwanted_words:
                                segment_text = segment_text.replace(word, ' ')

                            start_time = str(datetime.timedelta(seconds=segment_start)).split('.')[0]
                            end_time = str(datetime.timedelta(seconds=segment_end)).split('.')[0]

                            # Add chapter information to the chapters' list
                            chapter = Chapter(
                                self.cid,
                                self.eid,
                                f"{title} Part {title_number}".replace('|', ','),
                                segment_text,
                                start_time,
                                end_time
                            )
                            self.chapters.append(chapter)
                            title_number += 1
                            self.cid += 1
                        

                    else:
                        print(f'Extracting subtitles for video {self.cid} with id {video_id} without dividing it')
                        text = ' '.join([line['text'] for line in transcript])
                        for word in unwanted_words:
                            text = text.replace(word, ' ')

                        if not text.endswith(('.', '!', '?')):
                            text += '.'

                        start_time = str(datetime.timedelta(seconds=0)),
                        end_time = str(datetime.timedelta(seconds=total_duration_seconds)),
                        chapter = Chapter(
                            self.cid,
                            self.eid,
                            title.replace('|', ','),
                            text,
                            str(datetime.timedelta(seconds=0)).split('.')[0],
                            str(datetime.timedelta(seconds=total_duration_seconds)).split('.')[0]
                        )
                        self.chapters.append(chapter)
                        self.cid += 1
                else :
                    start_time = str(datetime.timedelta(seconds=0)).split('.')[0],
                    end_time = str(datetime.timedelta(seconds=total_duration_seconds)).split('.')[0],
                    print(f"Cannot retrieve transcript for video {self.cid} with id {video_id}")
                    chapter = Chapter(
                        self.cid,
                        self.eid,
                        title.replace('|', ','),
                        None,
                        start_time,
                        end_time
                    )
                    self.chapters.append(chapter)
                    self.cid += 1

            except Exception as e:
                print(f"Error retrieving transcript for video {self.cid} with id {video_id}. \n\tException type: {type(e)}. Exception message: {str(e)}")
                chapter = Chapter(
                    self.cid,
                    self.eid,
                    title.replace('|', ',') if title else None,
                    None,
                    str(datetime.timedelta(seconds=0)).split('.')[0],
                    str(datetime.timedelta(seconds=0)).split('.')[0],
                )
                self.chapters.append(chapter)
                self.cid += 1
            """num_rows = len(self.chapters) - cid_start
            if len(chapters) != num_rows:
                print(f"Warning: Number of rows in the 'chapters' file does not match the expected count. Expected: {num_rows}, Actual: {len(chapters)}")
            """

    def create_episodes(
                self, channel_name, playlist_id):         
            youtube = build('youtube', 'v3', developerKey = self.api_key)
            video_ids = []
            episode_names = []
            number = 1
            try:
                playlist = youtube.playlists().list(
                    part='snippet',
                    id=playlist_id).execute()['items'][0]['snippet']
                try:
                    playlist_items = []
                    next_page_token = None
                    while True:
                        res = youtube.playlistItems().list(
                            playlistId = playlist_id,
                            part = 'contentDetails, snippet',
                            maxResults = 50,
                            pageToken = next_page_token
                        ).execute()
                        playlist_items += res['items']
                        next_page_token = res.get('nextPageToken')
                        if not next_page_token:
                            break
                    for item in playlist_items:
                        print(f"Extracting subtitles for whole video n° {item['contentDetails']['videoId']}")
                        video_ids.append(item['contentDetails']['videoId'])
                        episode_names.append(item['snippet']['title'])
                except HttpError as e:
                    print(f'Error retrieving playlist {playlist_id}. Exception type: {type(e)}. Exception message: {str(e)}')
            
                for video_id, episode_name in zip(video_ids, episode_names):
                    video_response = youtube.videos().list(
                        part = 'snippet',
                        id = video_id
                    ).execute()
                    if 'items' in video_response and len(video_response['items']) > 0:
                        published_at = video_response['items'][0]['snippet'].get('publishedAt')
                    else:
                        published_at = None

                    episode = Episode(
                        self.eid,
                        self.sid,
                        number, 
                        episode_name.replace('|', ','),
                        published_at,
                        playlist['description'].replace('\n', ' ').replace('\n', ' ').replace('\r', ''),
                        video_id
                    )
                    self.episodes.append(episode)
                    number += 1
                    self.eid += 1

                    self.create_chapters(video_id, episode_name)
            
            except HttpError as e:
                    print(f'Error retrieving playlist information for playlist {playlist_id}. Exception type: {type(e)}. Exception message: {str(e)}')


    def create_series(
            self, file):
        youtube = build('youtube', 'v3', developerKey = self.api_key)
        with open(file, 'r') as f:
            reader = csv.reader(f)
            next(reader)    
            for row in reader:
                playlist_id, channel_name, category = row
                print(f'Extracting subtitles for serie n° {self.sid}\t with id {playlist_id}')
                #playlist_info = youtube.playlists().list(part = "snippet", id = playlist_id).execute()
                #playlist_title = playlist_info['items'][0]['snippet']['title']
                playlist_response = youtube.playlists().list(
                    part='snippet',
                    id=playlist_id
                ).execute()
                created_at = playlist_response['items'][0]['snippet']['publishedAt']
                title = playlist_response['items'][0]['snippet']['title']
                description = playlist_response['items'][0]['snippet']['description'].replace('\n', ' ').replace('\r', '')
                instructor = self.extract_instructor_from_description(description)


                videos = []

                next_page_token = None
                while True:
                    res = youtube.playlistItems().list(
                        playlistId = playlist_id,
                        part = 'snippet',
                        maxResults = 50,
                        pageToken = next_page_token).execute()
                    videos += res['items']
                    next_page_token = res.get('nextPageToken')
                    if next_page_token is None:
                        break

                serie = Serie(
                    self.sid,
                    category,
                    title.replace('|',','),
                    instructor,
                    created_at,
                    channel_name,
                    description if description else '',
                    playlist_id
                )

                self.series.append(serie)

                self.create_episodes(channel_name, playlist_id)

                self.sid += 1

        self.sid -= 1
        self.eid -= 1
        self.cid -= 1


class Serie:
    def __init__(
            self, sid, category, title, professor, 
            created_at, corpus, description, course):
        self.sid = sid
        self.category = category
        self.name = title
        self.professor = professor
        self.created_at = created_at
        self.corpus = corpus
        self.description = description
        self.course = course
    
            

class Episode:
    def __init__(
            self, eid, sid, order_series, title, 
            created_at, description, course):
        self.eid = eid
        self.sid = sid
        self.order_series = order_series
        self.title = title
        self.created_at = created_at
        self.description = description
        self.course = course


class Chapter:
    def __init__(self, cid, eid, title, text, begin, end):
        self.cid = cid
        self.eid = eid
        self.title = title
        self.text = text
        self.begin = begin
        self.end = end
        