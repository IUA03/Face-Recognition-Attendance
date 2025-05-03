import streamlit as st
import cv2
import pickle
import numpy as np
import os
import csv
import pandas as pd
from datetime import datetime
import time
from sklearn.neighbors import KNeighborsClassifier

st.sidebar.title("Choose an action")
app_choice=st.sidebar.radio("Select an Application", ("Add Face", "Take Attendance", "Display Presentees"))
if not os.path.exists('data'):
    os.makedirs('data')

if app_choice=="Add Face":
    st.title("Face Capture for Attendance System")

    with st.form(key='face_capture_form'):
        user_name=st.text_input("Enter your name:")
        submit_button=st.form_submit_button(label="Submit")

    if submit_button:
        if not user_name:
            st.warning("Please enter your name to proceed.")
            st.stop()
        face_cascade=cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
        video=cv2.VideoCapture(0)

        single_person_faces_data=[]
        st.title(f"Face Capture for {user_name}")
        status_text=st.empty()
        frame_placeholder=st.empty()

        while len(single_person_faces_data) < 100:
            ret, frame=video.read()
            if not ret:
                st.error("Failed to capture image.")
                break

            gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces=face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                crop_face=frame[y:y + h, x:x + w]
                resized_face=cv2.resize(crop_face, (50, 50))
                if len(single_person_faces_data) < 100:
                    single_person_faces_data.append(resized_face)
                cv2.putText(frame, f'Images: {len(single_person_faces_data)}', (30, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            frame_placeholder.image(frame, channels="BGR", use_container_width=True)
            status_text.text(f"Capturing faces: {len(single_person_faces_data)} / 100")
            if len(single_person_faces_data) >= 100:
                break

        video.release()
        faces_data_np=np.array(single_person_faces_data)

        
        if 'names.pkl' not in os.listdir('data/'):
            names=[user_name] * faces_data_np.shape[0]
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)
        else:
            with open('data/names.pkl', 'rb') as f:
                names=pickle.load(f)
            names.extend([user_name] * faces_data_np.shape[0])
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)

        if 'faces_data.pkl' not in os.listdir('data/'):
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(faces_data_np, f)
        else:
            with open('data/faces_data.pkl', 'rb') as f:
                existing_faces=pickle.load(f)
            existing_faces=np.append(existing_faces, faces_data_np, axis=0)
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(existing_faces, f)

        st.success(f"[INFO] {len(single_person_faces_data)} face images of '{user_name}' saved successfully!")


elif app_choice=="Take Attendance":
    st.title("Face Recognition Attendance System")
    attendance_dir="Attendance"
    if not os.path.exists(attendance_dir):
        os.makedirs(attendance_dir)

    
    with open("data/names.pkl", 'rb') as f:
        LABELS=pickle.load(f)

    with open("data/faces_data.pkl", 'rb') as f:
        FACES=pickle.load(f)

    FACES=np.array(FACES).astype('float32').reshape((len(FACES), -1))

    knn=KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    face_cascade=cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
    video=cv2.VideoCapture(0)
    if not video.isOpened():
        st.error("Unable to access the webcam.")
        st.stop()

    st.write("Webcam is active. Press **Q** to stop attendance.")
    COL_NAME=["NAME", "TIME"]
    
    frame_placeholder=st.empty()
    
    def write_to_csv(attendance_data):
        is_present=False
        show_presented_once=False
        date=datetime.now().strftime("%d-%m-%y")
        attendance_path=f"{attendance_dir}/Attendance_{date}.csv"
        exists=os.path.isfile(attendance_path)
    
        try:
            if not exists:
                with open(attendance_path, '+a', newline='') as csv_file:
                    writer=csv.writer(csv_file)
                    writer.writerow(COL_NAME)

        except Exception as e:
            st.error(f"Error writing to CSV: {e}")

        attendance_name=attendance[0]
        attendance_time=attendance[1]
        

        with open(attendance_path, 'r', newline='') as csv_file:
            rows=csv.reader(csv_file)
            for x in rows:
                name_in_csv=x[0]
                time_in_csv=x[1]
                if name_in_csv== attendance_name and time_in_csv[:2] == attendance_time[:2]:
                    is_present=True

        if not is_present:
            with open(attendance_path, 'a', newline='') as csv_file:
                writer=csv.writer(csv_file)
                writer.writerow(attendance_data)
                st.write(f"✅ {attendance_data[0]} marked at {attendance_data[1]}")

    while True:
        ret, frame=video.read()
        if not ret:
            continue

        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces=face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            crop_face=frame[y:y + h, x:x + w]
            resized_face=cv2.resize(crop_face, (50, 50)).flatten().reshape(1, -1)

            distances, indices=knn.kneighbors(resized_face)
            if distances[0][0] > 3000:  
                continue  

            output=knn.predict(resized_face)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 168, 82), 2)
            cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 168, 82), -1)

           
            cv2.putText(frame, str(output[0]).title(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            timestamp=datetime.now().strftime("%H:%M:%S")
            attendance=[str(output[0]).title(), str(timestamp)]
            name_time=attendance[0] + " " + attendance[1]
            write_to_csv(attendance)

        frame_rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


elif app_choice=="Display Presentees":
    st.title("Attendance Records")
    ts=time.time()
    date=datetime.fromtimestamp(ts).strftime("%d-%m-%y")
    try:
        df=pd.read_csv(f'Attendance/Attendance_{date}.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error(f"No attendance records found for {date}")