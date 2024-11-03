# OpenPLC V3 Docker Autostart
Create OpenPLC Docker, modify OpenPLC configuration including Slave Configuration and Settings, import your selected structured text file and start OpenPLC in run mode with the uploaded script.st.

## Steps
1. Copy your script into script.st or select your own OpenPLC st file.
2. Modify database.sh according to your requirement. See comments for more details.
3. Build Docker image
    ```
    docker build -t openplc:v3 --build-arg script=<your script.st> --build-arg database=database.sh .
    ```
4.  Run Docker image
    ```
    docker run -it --rm --privileged -p 8080:8080 openplc:v3
    ```
5. Alternatively run with docker-compose.yml.
