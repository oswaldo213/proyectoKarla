#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include "SSD1306Wire.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

#define RST_PIN 4
#define SS_PIN 5

const char *ssid = "INFINITUM2A37";
const char *password = "Mp7taEYHdb";
const char *servidor = "http://192.168.68.118:5000/identificar";

MFRC522 rfid(SS_PIN, RST_PIN);
SSD1306Wire display(0x3C, 21, 22);
Servo puerta;

void mostrarOLED(String linea1, String linea2, String linea3)
{
  display.clear();
  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 0, linea1);
  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 14, linea2);
  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 36, linea3);
  display.display();
}

void setup()
{
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  rfid.PCD_SetAntennaGain(rfid.RxGain_max);

  display.init();
  display.flipScreenVertically();

  puerta.attach(13);
  puerta.write(0);

  mostrarOLED("Conectando", "WiFi...", "");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi conectado");
  Serial.println(WiFi.localIP());
  mostrarOLED("WiFi OK", WiFi.localIP().toString(), "Acerca tarjeta");
}

void loop()
{
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial())
    return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++)
  {
    if (rfid.uid.uidByte[i] < 0x10)
      uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.println("UID: " + uid);
  mostrarOLED("Leyendo...", uid, "");

  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    http.begin(servidor);
    http.addHeader("Content-Type", "application/json");

    String body = "{\"uid\":\"" + uid + "\"}";
    int codigo = http.POST(body);

    if (codigo > 0)
    {
      String respuesta = http.getString();
      Serial.println("Respuesta: " + respuesta);

      StaticJsonDocument<200> json;
      deserializeJson(json, respuesta);

      String acceso = json["acceso"].as<String>();
      String nombre = json["nombre"].as<String>();
      String rol = json["rol"].as<String>();

      if (acceso == "permitido")
      {
        mostrarOLED(rol, nombre, "Acceso permitido");
        puerta.write(90);
        delay(3000);

        puerta.write(0);
      }
      else if (acceso == "equipo")
      {
        mostrarOLED("Equipo", nombre, "Registrado");
      }
      else
      {
        mostrarOLED("Acceso", "Denegado", uid);
      }
    }
    else
    {
      mostrarOLED("Error", "Sin respuesta", "del servidor");
    }

    http.end();
  }
  else
  {
    mostrarOLED("Error", "Sin WiFi", "");
  }

  rfid.PICC_HaltA();
  delay(3000);
  mostrarOLED("Listo", "Acerca tarjeta", "");
}