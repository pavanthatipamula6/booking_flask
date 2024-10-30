#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // set the LCD address to 0x27 for a 16 chars and 2 line display



Servo myServo;
char input[9];

/*rfid spi
  * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 */
#include <SPI.h>
#include <MFRC522.h>


#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the class

MFRC522::MIFARE_Key key;



#define buzzer A3

#define ir1 4
#define ir2 5
#define ir3 6
#define ir4 7
#define ir5 8
#define ir6 A0

#define button A4

const int numIR = 6;  // Number of IR sensors
int irStates[numIR];  // Array to store IR states
int prevIrStates[numIR];

String tagID = "";

void printHex(byte* buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}


void buz_delay(int a = 1, int b = 1) {
  for (int i = 0; i <= a; i++) {
    digitalWrite(buzzer, HIGH);
    delay(100 * b);
    digitalWrite(buzzer, LOW);
    delay(100 * b);
  }
}
void setup() {

  pinMode(button, INPUT_PULLUP);
  pinMode(buzzer, OUTPUT);

  myServo.attach(3);
  Wire.begin();
  Serial.begin(9600);
  buz_delay();
  lcd.init();
  // Print a message to the LCD.
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Parking!");
  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522
  for (int i = 4; i < 9; i++) {
    pinMode(i, INPUT);
  }
  pinMode(A0, INPUT);
  delay(2000);
  lcd.clear();
}



void loop() {
  readRfid();
  readIr();
  //printChangedIrStates();

  // if (Serial.available()>0) {
  //   //char receivedChar = Serial.readBytes(8);
  //   //String receivedString = Serial.readString();
  //   String receivedString = Serial.readStringUntil('\n');  // Read until EOL character

  //   lcdUpdater(receivedString);
  // }



  if (Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n');

    // Compare receivedData with predefined strings
    if (receivedData == "open") {
      // Perform action for 'open' command (e.g., open the servo)
      myServo.write(90);  // Adjust the angle according to your servo's range
      // lcd.print("servo open");
      // delay(1000);  // Delay for stability
      // lcd.clear();
    } else if (receivedData == "close") {
      // Perform action for 'close' command (e.g., close the servo)
      myServo.write(0);  // Adjust the angle according to your servo's range
      // lcd.print("servo close");
      // delay(1000);  // Delay for stability
      // lcd.clear();
    }
    if (receivedData != "open" && receivedData != "close") {
      lcdUpdater(receivedData);
      delay(1000);
    }
  }
  lcdprintIrStates();
}

void readRfid() {
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;
  //printHex(rfid.uid.uidByte, rfid.uid.size);

  //Serial.println();
  tagID = "";
  // The MIFARE PICCs that we use have 4 byte UID
  for (uint8_t i = 0; i < 4; i++) {  //
    input[i] = rfid.uid.uidByte[i];
    // Convert each byte to a two-digit hexadecimal representation
    if (rfid.uid.uidByte[i] < 0x10) {
      tagID += "0";  // Ensure leading zero for single-digit values
    }

    tagID.concat(String(rfid.uid.uidByte[i], HEX));  // Adds the 4 bytes in a single String variable
  }
  tagID.toUpperCase();
  tagID.toCharArray(input, 9);
  rfid.PICC_HaltA();  // Stop reading
  //Serial.println("input");
  Serial.println(tagID);
  // Serial.println(input);
}


void readIr() {
  for (int i = 4; i < 9; i++) {
    irStates[i - 4] = digitalRead(i);  // Store IR state in the array
  }
  irStates[numIR - 1] = digitalRead(A0);  // Store additional IR state in the array
}

void printIrStates() {
  Serial.println("IR Sensor States:");
  for (int i = 0; i < numIR; i++) {
    Serial.print("Sensor ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println(irStates[i]);
  }
}


void printChangedIrStates() {
  bool anyChange = false;

  for (int i = 0; i < numIR; i++) {
    if (irStates[i] != prevIrStates[i]) {
      anyChange = true;
      break;  // Exit the loop if any change is found
    }
  }

  if (anyChange) {
    Serial.println("IR Sensor States (Changed):");
    for (int i = 0; i < numIR; i++) {
      if (irStates[i] != prevIrStates[i]) {
        Serial.print("Sensor ");
        Serial.print(i);
        Serial.print(": ");
        Serial.println(irStates[i]);
        prevIrStates[i] = irStates[i];  // Update the previous state
      }
    }
  }
}

void lcdUpdater(String receivedData) {
  lcd.clear();

  if (receivedData.length() < 16) {
    lcd.print(receivedData);
  } else {
    for (int i = 0; i < 16; i++) {
      lcd.print(receivedData[i]);
    }
    lcd.setCursor(0, 1);
    for (int i = 16; i < receivedData.length(); i++) {
      lcd.print(receivedData[i]);
    }
  }
}

void lcdprintIrStates() {
  lcd.clear();
  int count = 0;
  lcd.print("slots:");
  for (int i = 0; i < numIR; i++) {
    if (irStates[i] == 0) {
      count++;
    }
  }
  lcd.print(count);
  lcd.print("/6 filled");
}
