import streamlit as st

import mysql.connector

import pymongo

import sqlalchemy

from sqlalchemy import create_engine

API_KEY='your api key'

import pandas as pd

conn=pymongo.MongoClient("your mongo creds")

conn_sql=sqlalchemy.create_engine('your database creds')

from googleapiclient.discovery import build

api_service_name = "youtube"

api_version = "v3"

youtube=build(api_service_name,api_version,developerKey=API_KEY)

sample=conn['youtube']

channel_id=st.text_input('enter channel id')

def channel_details(youtube,channel_id):
    
    all_data=[]
    request = youtube.channels().list(part="snippet,contentDetails,statistics",id=channel_id)
    response = request.execute()
    coll=sample['channel']
    for item in response['items']:
        data=dict(channel_name=item['snippet']['title'],
                    channel_id=item['id'],
                    subscribers_count=item['statistics']['subscriberCount'],
                    channel_views=item['statistics']['viewCount'],
                    channel_description = item['snippet']['description'],
                    total_videos= item['statistics']['videoCount'],
                    channel_creation_date=item['snippet']['publishedAt'],
                    playlist_id=item['contentDetails']['relatedPlaylists']['uploads'])
        coll.insert_one(data)
        all_data.append(data)
    df=pd.DataFrame(all_data)
    return df

def youtube_data_sql(channel_id):
    re=[]
    a='Sucessful'
    coll_var=sample.channel
    for i in coll_var.find({"channel_id":channel_id}):
        re.append(i)
    df=pd.DataFrame(re)
    df['channel_creation_date']=pd.to_datetime(df['channel_creation_date'])
    df=df.drop(['_id'],axis=1)
    df.to_sql(name='youtube_channell_details',
            con=conn_sql,
            index=False,
            if_exists='append')
    return a

def youtube_playlist(youtube,channel_id):
    coll=sample['playlistdetails'] 
    data2=[]
    request = youtube.playlists().list(part="snippet,contentDetails",channelId=channel_id,maxResults=50)
    response = request.execute()
        
    for item in response['items']:
        data1=dict(playlist_name=item['snippet']['title'],
                        playlist_idd=item['id'],
                        channel_id=item['snippet']['channelId'],
                        videos_in_playlist=item['contentDetails']['itemCount'])
        coll.insert_one(data1)
        data2.append(data1)
    next_page_token=response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlists().list(part="snippet,contentDetails",channelId=channel_id,maxResults=50,pageToken=next_page_token)
        response = request.execute()
        for item in response['items']:
            data1=dict(playlist_name=item['snippet']['title'],
                            playlist_idd=item['id'],
                            channel_id=item['snippet']['channelId'],
                            videos_in_playlist=item['contentDetails']['itemCount'])
            coll.insert_one(data1)
            data2.append(data1)
        next_page_token=response.get('nextPageToken')
    df=pd.DataFrame(data2)
    return df

def youtube_playlistdata_sql(channel_id):
    re=[]
    a='Sucessful'
    coll_var=sample.playlistdetails
    for i in coll_var.find({"channel_id":channel_id}):
        re.append(i)
    df=pd.DataFrame(re)
    df=df.drop(['_id'],axis=1)
    df.to_sql(name='youtube_playlist_channel_details',
            con=conn_sql,
            index=False,
            if_exists='append')
    return a

def youtube_data_playlistid(youtube,channel_id):
    all_data=[]
    request = youtube.channels().list(part="snippet,contentDetails,statistics",id=channel_id)
    response = request.execute()
    try:
        for item in response['items']:
            all_data.append(item['contentDetails']['relatedPlaylists']['uploads'])
    except Exception:
        print('')
    return all_data

try:
    playlist_id=youtube_data_playlistid(youtube,channel_id)
except Exception:
    print('')

def youtube_playlist_videos(youtube,playlist_id):
    data5=[]
    coll=sample['playlist_details']
    for i in range(len(playlist_id)):
        result=playlist_id[i]
        request = youtube.playlistItems().list(part="snippet,contentDetails",maxResults=50,playlistId=result)
        response = request.execute()
        
        for item in response['items']:
                data3=dict(video_id=item['contentDetails']['videoId'],
                        playlist_id=item['snippet']['playlistId'],
                        channel_id=item['snippet']['channelId'],
                        video_title=item['snippet']['title'],
                        video_uploaded_date=item['contentDetails']['videoPublishedAt'],
                        channel_name=item['snippet']['channelTitle'],
                        video_description=item['snippet']['description'])
                coll.insert_one(data3)
                data5.append(data3)
        next_page_token=response.get('nextPageToken')
        while next_page_token is not None:
            request = youtube.playlistItems().list(part="snippet,contentDetails",maxResults=50,playlistId=result,pageToken=next_page_token)
            response = request.execute()
            for item in response['items']:
                data3=dict(video_id=item['contentDetails']['videoId'],
                            playlist_id=item['snippet']['playlistId'],
                            channel_id=item['snippet']['channelId'],
                            video_title=item['snippet']['title'],
                            video_uploaded_date=item['contentDetails']['videoPublishedAt'],
                            channel_name=item['snippet']['channelTitle'],
                            video_description=item['snippet']['description'])
                coll.insert_one(data3)
                data5.append(data3)
            next_page_token=response.get('nextPageToken')
        df=pd.DataFrame(data5)
    return df


def youtube_playlist_video_data_sql(playlist_id):
    re=[]
    a='sucessful'
    #sample=conn['youtube']
    coll_var=sample.playlist_details
    for i in coll_var.find({"playlist_id":playlist_id}):
        re.append(i)
    df=pd.DataFrame(re)
    #try:
    df['video_uploaded_date']=pd.to_datetime(df['video_uploaded_date'])  
    df=df.drop(['_id','video_description','video_uploaded_date'],axis=1)
    df.to_sql(name='youtube_playlist_video_details',
            con=conn_sql,
            index=False,
            if_exists='append')
    return a

def youtube_playlist_videos_id(youtube,playlist_id):

    data5=[]
    for i in range(len(playlist_id)):
        result=playlist_id[i]
        request = youtube.playlistItems().list(part="snippet,contentDetails",maxResults=50,playlistId=result)
        response = request.execute()
        for item in response['items']:
            data5.append(item['contentDetails']['videoId'])
        next_page_token=response.get('nextPageToken')
        while next_page_token is not None:
            request = youtube.playlistItems().list(part="snippet,contentDetails",maxResults=50,playlistId=result,pageToken=next_page_token)
            response = request.execute()
            for item in response['items']:
                data5.append(item['contentDetails']['videoId'])
            next_page_token=response.get('nextPageToken')  
    return data5

try:
    videos_id=youtube_playlist_videos_id(youtube,playlist_id)
except Exception:
    print('')

def comments_details(youtube,videos_id):
    coll=sample['comment_details']
    data6=[]
    try:
        for i in range(len(videos_id)):
            result=videos_id[i]
            request = youtube.commentThreads().list(part="snippet,replies",maxResults=1,videoId=result)
            response = request.execute()
            for item in response['items']:
                data=dict(comment_id=item['id'],
                        video_id=item['snippet']['videoId'],
                        comment_on_video=item['snippet']['topLevelComment']['snippet']['textDisplay'], 
                        comment_made_by=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        comment_date=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                coll.insert_one(data)
                data6.append(data)
            #next_page_token=response.get('nextPageToken')
            #while next_page_token is not None:
            #    request = youtube.commentThreads().list(part="snippet,replies",maxResults=50,videoId=result,pageToken=next_page_token)
            #    response = request.execute()
            #    for item in response['items']:
            #        data=dict(comment_id=item['id'],
            #          video_id=item['snippet']['videoId'],
            #          comment_on_video=item['snippet']['topLevelComment']['snippet']['textDisplay'], 
            #          comment_made_by=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            #          comment_date=item['snippet']['topLevelComment']['snippet']['publishedAt'],
            #          like_on_comment=item['snippet']['topLevelComment']['snippet']['likeCount'])
            #        data6.append(data)
            #    next_page_token=response.get('nextPageToken')
    
    except Exception:
        print('')    
    df=pd.DataFrame(data6)
    return df
    
def youtube_comment_details_data_sql(videos_id):
    re=[]
    a='Sucessfull'
    coll_var=sample.comment_details
    for j in range(len(videos_id)):
        result=videos_id[j]
        for i in coll_var.find({"video_id":result}):
            re.append(i)
    df=pd.DataFrame(re)
    df['comment_date']=pd.to_datetime(df['comment_date'])
    df=df.drop(['_id'],axis=1)
    df.to_sql(name='youtube_comment_details',
            con=conn_sql,
            index=False,
            if_exists='append')
    return a

def videos_info(youtube,videos_id): 
    coll=sample['videos_details']
    data6=[]
    for i in range(len(videos_id)):
        result=videos_id[i]
        request = youtube.videos().list(part="snippet,contentDetails,statistics",maxResults=50,id=result)
        response = request.execute()
        for item in response['items']:
            data3=dict(video_id=item['id'],
                        channel_id=item['snippet']['channelId'],
                        video_title=item['snippet']['title'], 
                        video_description=item['snippet']['description'],
                        video_creation_date=item['snippet']['publishedAt'],
                        video_duration=item['contentDetails']['duration'],
                        views_count=item['statistics']['viewCount'],
                        likes_count=item['statistics']['likeCount'],
                        favourite_count=item['statistics']['favoriteCount'],
                        comment_count=item['statistics']['commentCount'],
                        thumbnail_of_video=item['snippet']['thumbnails']['default']['url'],
                        caption_status=item['contentDetails']['caption'])
            coll.insert_one(data3)
            data6.append(data3)
        next_page_token=response.get('nextPageToken')
        while next_page_token is not None:
            request = youtube.videos().list(part="snippet,contentDetails,statistics",maxResults=50,id=result,pageToken=next_page_token)
            response = request.execute()
            for item in response['items']:
                data3=dict(video_id=item['id'],
                        channel_id=item['snippet']['channelId'],
                        video_title=item['snippet']['title'],  
                        video_description=item['snippet']['description'],
                        video_creation_date=item['snippet']['publishedAt'],
                        video_duration=item['contentDetails']['duration'],
                        views_count=item['statistics']['viewCount'],
                        likes_count=item['statistics']['likeCount'],
                        favourite_count=item['statistics']['favoriteCount'],
                        comment_count=item['statistics']['commentCount'],
                        thumbnail_of_video=item['snippet']['thumbnails']['default']['url'],
                        caption_status=item['contentDetails']['caption'])
                coll.insert_one(data3)
                data6.append(data3)
            next_page_token=response.get('nextPageToken')
    df=pd.DataFrame(data6)
    return df

def youtube_video_details_data_sql(channel_id):
    re=[]
    a='Suceesfull'
    coll_var=sample.videos_details
    for i in coll_var.find({"channel_id":channel_id}):
        re.append(i)
    df=pd.DataFrame(re)
    df['video_creation_date']=pd.to_datetime(df['video_creation_date'])    
    df['video_duration']=df['video_duration'].str.replace('PT','')
    df=df.drop(['_id'],axis=1)
    df.to_sql(name='youtube_video_details',
            con=conn_sql,
            index=False,
            if_exists='append')
    return a

if st.button('Retrive from youtube'):
    st.write(channel_details(youtube,channel_id))
    st.write(youtube_playlist(youtube,channel_id))
    st.write(youtube_playlist_videos(youtube,playlist_id))
    st.write(videos_info(youtube,videos_id))
    st.write(comments_details(youtube,videos_id))        

if st.button('Migrate to sql'):
    st.write(youtube_data_sql(channel_id))
    st.write(youtube_playlistdata_sql(channel_id))
    st.write(youtube_video_details_data_sql(channel_id))
    st.write(youtube_comment_details_data_sql(videos_id))        
