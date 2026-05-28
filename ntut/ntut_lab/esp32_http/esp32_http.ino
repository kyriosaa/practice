#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "LittleFS.h"

// SPIFFS read
String API_KEY;
String ssid;
String password;

const int MOTOR_PIN1 = 12;
const int MOTOR_PIN2 = 13;
const int MOTOR_PWM = 14;

// port 80
WebServer server(80);

void handlePostData();
void handleOptions();

void setup() {
  Serial.begin(115200);

  // init SPIFFS
  if (!LittleFS.begin(true)) {
    Serial.println("SPIFFS mount failed.");
    return;  
  }
  Serial.println("SPIFFS mounted successfully.");

  // load SSID
  File ssidFile = LittleFS.open("/ssid.txt", "r");
  if (!ssidFile) {
    Serial.println("Failed to open /ssid.txt");
    return;
  }
  ssid = ssidFile.readString();
  ssidFile.close();
  ssid.trim();
  Serial.println("SSID loaded from SPIFFS");

  // load password
  File passFile = LittleFS.open("/pass.txt", "r");
  if (!passFile) {
    Serial.println("Failed to open /pass.txt");
    return;
  }
  password = passFile.readString();
  passFile.close();
  password.trim();
  Serial.println("Password loaded from SPIFFS");
  
  // load API key
  File keyFile = LittleFS.open("/api_key.txt", "r");
  if (!keyFile) {
    Serial.println("Failed to open /api_key.txt");
    return; 
  }
  API_KEY = keyFile.readString();
  keyFile.close(); 
  API_KEY.trim();
  Serial.println("API key loaded from SPIFFS.");
  
  pinMode(MOTOR_PIN1, OUTPUT);
  pinMode(MOTOR_PIN2, OUTPUT);
  pinMode(MOTOR_PWM, OUTPUT);
  digitalWrite(MOTOR_PIN1, LOW);
  digitalWrite(MOTOR_PIN2, LOW);
  analogWrite(MOTOR_PWM, 0);
  
  // wifi conn
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi");
  Serial.print("Local IP: ");
  Serial.println(WiFi.localIP());
  Serial.println("Access via: http://101.12.246.165:80/api/data");

  // register handlers
  server.on("/api/data", HTTP_POST, handlePostData);
  server.on("/api/data", HTTP_OPTIONS, handleOptions);
  
  server.enableCORS(true);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();  // ESP32 standby until receives request
}

void handlePostData() {
  // verify API key
  if (!server.hasHeader("Authorization")) {
    server.send(401, "application/json", "{\"error\":\"Missing API key\"}");
    return;
  }
  String authHeader = server.header("Authorization");
  if (authHeader != String("Bearer ") + API_KEY) {
    server.send(403, "application/json", "{\"error\":\"Invalid API key\"}");
    return;
  }

  String body = server.arg("plain");
  Serial.println("Received POST data:");
  Serial.println(body);

  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, body);
  if (error) {
    server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }

  const char* command = doc["command"];
  int speed = doc["speed"] | 0;

  // command exec
  if (strcmp(command, "motor_on") == 0) {
    digitalWrite(MOTOR_PIN1, HIGH);
    digitalWrite(MOTOR_PIN2, LOW);
    analogWrite(MOTOR_PWM, constrain(speed, 0, 255));
    Serial.printf("Motor ON at speed %d\n", speed);
  } else if (strcmp(command, "motor_off") == 0) {
    digitalWrite(MOTOR_PIN1, LOW);
    digitalWrite(MOTOR_PIN2, LOW);
    analogWrite(MOTOR_PWM, 0);
    Serial.println("Motor OFF");
  } else {
    server.send(400, "application/json", "{\"error\":\"Unknown command\"}");
    return;
  }

  server.send(200, "application/json", "{\"status\":\"success\",\"message\":\"Command executed\"}");
}

void handleOptions() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  server.send(204);
}