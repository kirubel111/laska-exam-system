# 🎓 Laska Exam System

Hello! Welcome to my project, Laska Exam System. This is a web application I build to help student take their exam on the internet easily. I use Python Flask and Tailwind CSS for making this.

## ✨ Features in this project
* User Dashboard: A page for student to see the courses they will take.
* Smart Quiz: * If you flag a question, it will not count in final score.
    * Student can not go back to previous question (unless it is flagged).
* Auto Timer: There is a clock counting down. When the time is finish, the exam will submit by itself automatically.
* No Internet Needed for Design: I setup Tailwind CSS locally (version 3). So the design will load very fast and work even if you don't have internet connection.

## 🛠️ Technology I Use
* Backend: Python (Flask)
* Frontend: HTML5, Tailwind CSS v3

## 🚀 How to Run in Your Computer

Please follow this steps to start the project in your machine:

### 1. Download the project
```bash
git clone https://github.com/kirubel111/laska-exam-system.git
cd laska-exam-system
```
### 2. Install Python things
You need to install the packages from requirements file.
 ```bash
  pip install -r requirements.txt
 ```
### 3. Build Tailwind CSS
You must have Node.js installed in your computer. Then open terminal and type this to make the CSS work:
```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```
> [!NOTE]
> (Please keep this terminal open when you are writing code).

### 4. Start the Flask App
Open another terminal and run the app:
```python
python app.py
```
📂 Files Inside
app.py - The main Python backend code
templates/ - Where the HTML files are (like quiz, dashboard)
static/ - Where I put CSS and images
tailwind.config.js - Setting for Tailwind CSS
📝 License
This project is free to use (MIT License).
Thank you for visiting my project! If you find problem, please tell me.
