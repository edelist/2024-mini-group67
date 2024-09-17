# Exercise 1:

Min bright: 1000
Max bright: 50000

# Exercise 2:

Code plays "Twinkle Twinkle Little Star" in exercise_sound.py

# Exercise 3:

## Design Decisions
### 1. Platform and Hardware:
Raspberry Pi Pico used as the microcontroller.
Button Input and LED Output for reaction time game interaction.

### 2. Connectivity:
Wi-Fi for connecting the Pico to the internet using network module to enable communication with Firebase.

### 3. Firebase Integration:
Firebase Authentication: Users can sign in or create accounts using email and password.
Firestore Database: Reaction times and game data are uploaded securely to each user’s own collection.

### 4. Game Logic:
Reaction Time Measurement: LED randomly flashes, and the user’s response time is measured based on button press.
Scoring: Misses, minimum, maximum, and average response times are calculated for each game session.

### 5. Security:
Firestore Security Rules: Only authenticated users can read/write their own data based on auth.uid.

### 6. Code Structure:
Modular approach, separating Wi-Fi connection, Firebase authentication, game logic, and Firestore data upload functions for clarity and maintainability.

### 7. Data Handling:
Reaction times and scores are formatted into JSON before being sent to Firebase.
The use of structured Firestore data schema (e.g., doubleValue, integerValue for Firestore fields).
