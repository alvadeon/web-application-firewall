Shieldon is a web application firewall (WAF) project designed to protect websites from malicious attacks and unauthorized access. The project utilizes Streamlit to create an interactive and user-friendly interface for real-time traffic analysis and threat detection. Shieldon operates by intercepting web traffic, analyzing it for malicious patterns, and blocking potentially harmful requests. The system logs all activities, allowing administrators to review and respond to threats effectively. By integrating IP geolocation data, Shieldon enhances its ability to identify and block suspicious traffic based on geographic origin. This project is an essential tool for developers aiming to enhance the security of their web applications, offering robust protection and easy management through its comprehensive and intuitive interface. 

1. Python Libraries:
Streamlit: For building the web-based user interface.
Installation: pip install streamlit
Shieldon: The core library for implementing the Web Application Firewall (WAF) features.
Since you're using a customized version, ensure you have the correct package setup.
Flask: To handle the web application that will be protected by the WAF.
Installation: pip install Flask
SQLite3 (or any other DBMS): For storing logs, IP data, and other related information.
Typically included with Python, but you can install any other database libraries if needed (e.g., pip install SQLAlchemy).
GeoIP2: For IP address geolocation to track and block malicious IPs.
Installation: pip install geoip2
Pandas: For data manipulation and analysis, particularly if you need to work with logs.
Installation: pip install pandas
Scikit-learn or TensorFlow/PyTorch: If you plan to integrate machine learning models for detecting malicious patterns.
Installation: pip install scikit-learn or pip install tensorflow / pip install torch
Requests: For making HTTP requests to interact with APIs or other services.
Installation: pip install requests

For your Shieldon project using Streamlit, here are some essential libraries and tools that you might need:

Streamlit - For creating the web interface.
Requests - For handling HTTP requests.
WebSockets - For handling real-time data transfer.
Flask - If your backend involves Flask for routing.
SQLite - For managing the database if you're using a lightweight database solution.
Pandas - For data manipulation and analysis.
GeoLite2 - For IP geolocation services.
Socket - For managing low-level networking interfaces.
PyCryptodome - For cryptographic functions, if needed.
Matplotlib or Plotly - For visualizing data, especially if you're generating graphs.
