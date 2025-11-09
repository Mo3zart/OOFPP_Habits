# Habit Tracker App

A command-line Python3 application to **create, track, and analyze habits** — developed for the IU course *Object Oriented and Functional Programming with Python (DLBDSOOFPP01)*.

**Developed by Moritz Zewinger – OOFPP – DLBDSOOFPP01**

---

## 🎯 Project Overview
This project demonstrates the design and implementation of a **habit tracking system** that helps users build consistency through periodic tracking. It focuses on the integration of **object-oriented programming (OOP)** and **functional programming (FP)** principles in Python.

### Key Features
- Create, edit, and delete daily or weekly habits
- Mark habits as completed
- View and analyze streaks and performance trends
- Persist data using SQLite
- Analyze results using functional programming concepts
- Fully tested with `pytest`

---

## ⚙️ Installation Instructions

### **1. Run with Docker**

> [!IMPORTANT]
> Docker needs to be installed on your system.
> It is also important to change the directory to OOFPP_Habits_Phase2/OOFPP_Habits

To build and run the application inside Docker:
```bash
docker build --no-cache -t habit-tracker .
docker run -it habit-tracker
```

After running, the CLI automatically starts:
```
----------------------------------------------------------
 _   _       _     _ _ _____              _
| | | |     | |   (_) |_   _|            | |
| |_| | __ _| |__  _| |_| |_ __ __ _  ___| | _____ _ __
|  _  |/ _` | '_ \| | __| | '__/ _` |/ __| |/ / _ \ '__|
| | | | (_| | |_) | | |_| | | | (_| | (__|   <  __/ |
\_| |_/\__,_|_.__/|_|\__\_/_|  \__,_|\___|_|\_\___|_|
----------------------------------------------------------
```

*`---OR---`*

### **1. Clone the repository**
```bash
git clone https://github.com/Mo3zart/OOFPP_Habits.git
cd OOFPP_Habits
```

### **2. (Optional) Create a virtual environment**
```bash
python3 -m venv .habit-tracker
source .habit-tracker/bin/activate  # macOS/Linux
.habit-tracker\Scripts\activate    # Windows
```

### **3. Install dependencies**
```bash
pip3 install -r requirements.txt
python3 src/modules/seed_db.py
```

### **4. Run locally**
```bash
python3 src/main.py
```

You’ll see the interactive CLI start with the HabitTracker banner.

---

## 💻 Usage
Once inside the CLI, you can type commands such as:
- `create` – Create a new habit
- `edit` – Modify an existing habit
- `delete` – Delete a habit
- `complete` – Mark a habit as completed
- `analyze` – View habit statistics and streaks
- `help` – Show all available commands
- `exit` – Quit the application

Example:
```bash
HabitTracker > create 
Enter habit name: Drink Water
Enter periodicity (daily/weekly/monthly): daily

✅ Habit '<habit_name>' (<periodicity>) saved successfully!
```

> The `help` command always shows which commands you can run!

---

## 🧩 Project Structure
```
OOFPP_Habits/
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
├── src/
│   ├── main.py                   # Entry point and CLI logic
│   ├── data/sample_habits.db     # Predefined example data
│   └── modules/
│       ├── habit.py              # Habit entity (OOP)
│       ├── habit_manager.py      # Manages habit creation and persistence
│       ├── analytics.py          # FP-based analytics (streaks, summaries)
│       ├── sqlite_handler.py     # Handles SQLite operations
│       ├── storage_handler.py    # Abstract persistence interface
│       └── admin_tools.py        # CLI helper utilities
└── tests/                        # Unit test suite (pytest)
```

---

## 🧠 Design and Implementation

### **Object-Oriented Programming (OOP)**
- `Habit` class encapsulates all habit-related attributes and methods.
- `HabitManager` handles creation, update, deletion, and retrieval of habits.

### **Functional Programming (FP)**
- `analytics.py` uses **pure functions** and **higher-order functions** to calculate streaks, filter habits, and perform aggregations.
- Functional design ensures modularity and testability.

### **Persistence Layer**
- SQLite is used for local data storage.
- The database structure ensures data integrity and easy query operations.

---

## 🧪 Testing

All major functionalities are tested using **pytest**.
To run tests:
```bash
pytest -v --disable-warnings
```

Example output:
```
collected 28 items

28 passed in 0.02s ✅
```

---

## 📊 Example Data

The app ships with **five predefined habits** (both daily and weekly) and four weeks of completion data for testing and demonstration. These are stored in `src/data/sample_habits.db`.

---

## 💬 Reflection and Future Improvements
- ✅ **Strengths:** clear OOP structure, modular architecture, strong analytics logic
- ⚙️ **Possible enhancements:** GUI integration (e.g., Tkinter or Flask), cloud persistence, and extended analytics (failure streaks, goal tracking)
- 💡 **Lessons learned:** combining OOP and FP enhances maintainability and testability.

---

## 🔗 Project Info
**Author:** Moritz Zewinger  
**Course:** OOFPP – DLBDSOOFPP01 (IU International University)  
**GitHub:** [https://github.com/Mo3zart/OOFPP_Habits](https://github.com/Mo3zart/OOFPP_Habits)

---

> This README.md and all code are part of the IU portfolio submission for the course *Object Oriented and Functional Programming with Python (DLBDSOOFPP01)*.
