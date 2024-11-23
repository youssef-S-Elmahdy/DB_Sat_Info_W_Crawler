# Satellite TV Database Application

## Introduction

This project involves building a database application to gather and manage information about TV-broadcasting satellites across Asia, Europe, the Atlantic, and the Americas. The application will store and provide detailed data on satellites, carrier rockets, their positions, channels they broadcast, and the networks they belong to. The goal is to create a flexible tool that allows users to filter, aggregate, and identify satellites and channels based on their location and preferences, addressing the limitations of the current resources such as Lyngsat.com.

---

## Project Milestones

### **Milestone I: Database Design & Implementation**
**Tools:** MySQL  
**Description:**  
Design and implement the database backend based on the data requirements. This involves:
- Creating an **Entity-Relationship Diagram (ERD)** for the system.
- Designing the relational model for the database.
- Writing SQL scripts to define the database schema in MySQL.

**Deliverables (20 points):**
1. Entity-Relationship Diagram (ERD).
2. Relational model.
3. SQL transcript for creating the database schema.

---

### **Milestone II: Web Crawling and Data Population**
**Tools:** Selenium, Python
**Description:**  
Develop a web crawler to extract relevant data from Lyngsat.com and populate the database. Tasks include:
- Crawling the website for satellite and channel data across all regions.
- Parsing the HTML content to extract relevant fields for the database.
- Populating the non-user tables with extracted data.
- Using sample data to populate user-related tables.

**Deliverables:**
1. Crawling script.
2. Populated MySQL database dump.
3. CSV files for the values in each table.

---

### **Milestone III: Application Layer**
**Tools:** Any platform or language (Web-based, GUI, or Command-Line)  
**Description:**  
Create an application capable of interacting with the database hosted on a remote MySQL server. The application should provide the following functionalities:
1. **User Management:**
   - Register new users.
   - Create and manage a list of favorite channels.
2. **Channel Discovery:**
   - Show all channels viewable from a specific location (longitude).
   - Identify which favorite channels are viewable based on user location, along with satellite, frequency, and encryption details.
3. **Statistical Insights:**
   - Display the top 5 TV networks/providers by the number of channels and their average satellite availability.
   - List the top 5 carrier rockets by the number of satellites they launched.
   - Identify the top 5 growing satellites by the number of channels added since their launch.
   - Show the top 5 channels for each language based on their satellite availability.
4. **Filtering:**
   - Provide a filtered list of channels based on region, satellite, HD/SD quality, and language.

**Deliverables:**
1. Application source code and executable.
2. Latest database dump.
3. A demo showcasing the application.

---

## Features Overview

### Database Design:
- Stores detailed information about satellites (e.g., name, position, region, launch details).
- Includes data on channels, their attributes (e.g., beam, frequency, encryption, language), and their associated networks/packages.
- Supports users by storing profiles, locations, and favorite channel lists.

### Application Features:
1. **User Registration**:
   - Users can register with email, username, location, and preferences.
2. **Location-Based Satellite & Channel Discovery**:
   - Helps users find satellites in range (+/-10° of longitude).
   - Displays channels viewable at the user's location.
3. **Detailed Statistics**:
   - Insights on top networks, rockets, and channels across languages.
   - Historical growth trends for satellites and channels.
4. **Advanced Filtering**:
   - Enables customized queries for channels based on HD/SD, region, satellite, and language.

---

## Tools and Technologies
- **Database:** MySQL
- **Web Crawling:** Selenium, Python

---

## Notes
- The application must communicate with a remote MySQL server (not localhost).
- Bonus points are available for GUI or web-based implementations.
- Ensure that the database schema and application are optimized for scalability and ease of use.

Let’s build an intelligent Satellite TV database system and revolutionize how users interact with satellite and channel data!

