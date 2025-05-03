# Face Recognition Attendance

**Face Recognition Attendance** is a simple and efficient Python application that automates attendance using real-time face recognition. It uses OpenCV for face detection and recognition, and Streamlit to provide an easy-to-use web interface.

---

## 📋 How to Use

1. **Add Faces**

   * Select the **"Add Faces"** option from the sidebar.
   * Enter your name.
   * Allow camera access and position your face in front of the webcam.
   * The app will capture and save multiple images of your face.

2. **Take Attendance**

   * Select the **"Take Attendance"** option.
   * Ensure camera access is granted.
   * The app will recognize faces in real time and mark the corresponding names in the attendance log.

3. **Display Presentees**

   * Click on **"Display Presentees"** to view the attendance sheet.
   * Attendance data is stored in a CSV file with names and timestamps.

---

## 🛠️ Dependencies

The following libraries are required to run the application:

* `streamlit`
* `opencv-python`
* `numpy`
* `pandas`
* `scikit-learn`

Additionally, the app uses standard Python modules:

* `pickle`
* `os`
* `csv`
* `datetime`
* `time`

You can install the required packages with:

```bash
pip install streamlit opencv-python numpy pandas scikit-learn
```

---

## ✅ Features

* Real-time face detection and recognition
* Simple three-step process (Add Faces, Take Attendance, Display Presentees)
* Attendance logs stored in CSV format with timestamps
* Clean and intuitive interface using Streamlit

---

## 📌 Notes

* Ensure your webcam is functional and permissions are granted when prompted.
* The system works best under good lighting conditions.
* For any issues or contributions, feel free to open an issue or pull request.
