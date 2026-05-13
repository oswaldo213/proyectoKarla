#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include "SSD1306Wire.h"

#define RST_PIN  4
#define SS_PIN   5

MFRC522 rfid(SS_PIN, RST_PIN);
SSD1306Wire display(0x3C, 21, 22);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  rfid.PCD_SetAntennaGain(rfid.RxGain_max);

  display.init();
  display.flipScreenVertically();

  display.clear();
  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 0, "Listo.");
  display.drawString(0, 20, "Acerca tarjeta");
  display.display();
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.println("UID|" + uid);

  display.clear();
  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 0, "Leyendo...");
  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 16, uid);
  display.display();

  rfid.PICC_HaltA();
  delay(2000);

  display.clear();
  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 0, "Listo.");
  display.drawString(0, 20, "Acerca tarjeta");
  display.display();
}