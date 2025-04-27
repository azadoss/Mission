# Geo Map AI Agent Dashboard Web App for example

## 📌 Overview

Geo agentiniñ baqılaw taqtasınıñ mısalı kodı - bul aşıq bastapqı LLM (Gemma, LLaMA jäne t. Ol naqtı waqıttağı geokeñistiktik derekterdi vïzwalïzacïyalawdı jäne ïnfraqurılımdı baqılaw üşin AI basqaratın tüsinikterdi usınadı. Jüye kartağa negizdelgen analïtïkası bar ïntwïtïvti baqılaw taqtasın usınatın Django, Leaflet.js jäne LLM API arqılı qurastırılğan. Bul jobanıñ maqsatı LLM paydalanw jäne onı kartamen öñdewge qoldanw jolın körsetw. Bul oñay tüsinw üşin jıldam ülgisi men algorïtmi bar qarapayım mexanïzmge ïe. Onı tüsingennen keyin önimdilikti jaqsartwğa boladı.

---

Geo Agent Dashboard is **interactive mapping solution** powered by **Open-source LLMs (Gemma, LLaMA, etc.)**. It provides **real-time geospatial data visualization** and **AI-driven insights** for infrastructure monitoring. The system is built using **Django**, **Leaflet.js**, and **LLM APIs**, offering an intuitive dashboard with **map-based analytics**. This project has the purpose of demonstration how to use LLM and apply it to map handling. This has simple mechanism with prompt template and algorithm to understand it easily. You can improve the performance after understanding it. 
</br><img src="https://github.com/mac999/geo-llm-agent-dashboard/blob/main/doc/geo_llm_demo.gif" width=800 /></br>

## ✨ Features
- **AI-driven Geo Visualization**: Uses **LLM AI models** for geo-data processing.
- **Interactive Mapping**: Powered by **Leaflet.js** for real-time infrastructure monitoring.
- **LLM-based Query Processing**: Supports **natural language queries** for location insights.

#### Prompt example
   ```sh
zoom in tokyo and draw circle with 10 km, red color.
zoom out
zoom out, 2 times. 
Zoom in newyork and draw circle with 20 km. blue color.
zoom out, 3 times. 
add marker to center of newyork.
zoom in seoul,  add marker to center of it and draw circle with 5km. 
   ```

## 🚀 Installation

### Prerequisites
- **Python** (3.8+)
- **Web Browser** (Chrome, Firefox, Edge, etc.)
- **Django and LLM API Key** (Gemma, LLaMA, etc.)
- **JavaScript Runtime** (for local testing)

### Steps
1. **Clone the Repository**
   ```sh
   Download directory https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2Fazadoss%2FMission%2Ftree%2Fmain%2FDOME%2Fgeo-agent
   cd geo-map-ai-agent
   ```

2. **Create Virtual Environment & Install Dependencies**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install django-cors-headers Django pandas numpy gunicorn whitenoise django-environ langchain
   server.bat
   ```

3. **Open in Browser**
   - Simply open `index.html` in your web browser.
   - No need for a database or server setup.

4. **Customize API Configuration**
   - Modify `config.js` to set your LLM API key and preferences.
   
## 🔧 Configuration
- **API Settings**: Set up API endpoints and credentials in `settings.py`.
- **Customization**: Modify CSS and JavaScript files for UI/UX improvements.
- **Static Files**: Hosted on any web server or used locally.

## 📂 Project Structure
```
geo-llm-agent-dashboard/
│── charts/static/                    # CSS, JavaScript, images
│── charts/templates/index.html       # Main UI file
│── dashbaord                         # asgi, settings
│── static                            # resource files
│── manage.py                         # Django entry point
```

## 📜 License
This project is licensed under the **MIT License**.
