#include "esp_camera.h"
#include <WiFi.h>
#include "board_config.h"
#include <Adafruit_NeoPixel.h>
#include <PubSubClient.h>

#define NUM_PIXEL 1
#define TOUCH_PIN 38
#define RGB_LED_PIN 39

Adafruit_NeoPixel pixel(NUM_PIXEL,RGB_LED_PIN,NEO_GRB + NEO_KHZ800);

// ===========================
// Enter your WiFi credentials
// ===========================
const char *ssid = "legolan";
const char *password = "legolanpwd";

// MQTT Broker details
const char* mqtt_server = "broker.emqx.io"; // e.g., "broker.emqx.io"
const int mqtt_port = 1883;   // non-TLS MQTT
const char* mqtt_username = "YOUR_MQTT_USERNAME";
const char* mqtt_password = "YOUR_MQTT_PASSWORD";
const char* mqtt_client_id = "ArduinoClient"; // Unique client ID

// Define the topic to subscribe to
const char* mqtt_topic_subscribe = "yolo/detections";

WiFiClient espClient; // Use WiFiClient for non-TLS
PubSubClient client(espClient);

void startCameraServer();
void setupLedFlash();

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);

  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
  }
  Serial.println();
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect(mqtt_client_id, mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(mqtt_topic_subscribe);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}


void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
      config.jpeg_quality = 60;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;

  // pinMode(13, INPUT_PULLUP);
  // pinMode(14, INPUT_PULLUP);


  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  // drop down frame size for higher initial frame rate
    s->set_framesize(s, FRAMESIZE_QQVGA);
    s->set_vflip(s, 0);
    s->set_hmirror(s, 1);   // ESP32-S3-EYE lens needs mirroring
    s->set_brightness(s, 0);
    s->set_saturation(s, 2);
  

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pinMode(TOUCH_PIN, INPUT);
  pixel.begin();
  pixel.clear();
  pixel.show();
}

void loop() {
  //  Everything is done in another task by the web server
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  delay(10000);
}
