#include <MCUFRIEND_kbv.h>
#include <Adafruit_GFX.h>
#include <ArduinoJson.h>

#define BUFFER_SIZE   256

/* RGB565 color definitions */
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

MCUFRIEND_kbv tft;

/* Serial buffer */
static char jsonBuffer[BUFFER_SIZE];

/* Persistent display state */
static uint16_t fgColor = WHITE;
static uint16_t bgColor = BLACK;
static uint8_t  textSize = 2;
static String   text = "Waiting for data...";

uint16_t parseColor(const char *c) {
  if (!c) return 0;

  if (!strcasecmp(c, "BLACK"))   return BLACK;
  if (!strcasecmp(c, "BLUE"))    return BLUE;
  if (!strcasecmp(c, "RED"))     return RED;
  if (!strcasecmp(c, "GREEN"))   return GREEN;
  if (!strcasecmp(c, "CYAN"))    return CYAN;
  if (!strcasecmp(c, "MAGENTA")) return MAGENTA;
  if (!strcasecmp(c, "YELLOW"))  return YELLOW;
  if (!strcasecmp(c, "WHITE"))   return WHITE;

  return (uint16_t)strtol(c, NULL, 16);
}

void redraw() {
  tft.fillScreen(bgColor);
  tft.setTextColor(fgColor, bgColor);
  tft.setTextSize(textSize);
  tft.setCursor(0, 0);
  tft.print(text);
  Serial.println("OK");
}

void setup() {
  Serial.begin(115200);

  uint16_t id = tft.readID();
  if (id == 0xD3D3 || id == 0xFFFF) {
    id = 0x9341;
  }

  tft.begin(id);
  tft.setRotation(1);
  tft.setTextSize(2);
  tft.fillScreen(BLACK);
  tft.setTextColor(GREEN, BLACK);
  tft.setCursor(0, 0);  
  tft.println("Send JSON over Serial with BAUD 115200:");
  tft.setTextColor(WHITE, BLACK);
  tft.println("{\"txt\":\"Hello\",\"fg\":\"RED\",\"bg\":\"0000\",\"size\":3}");
  tft.setTextColor(GREEN, BLACK);
  tft.println("All JSON keys are optional, so old ones will be used if omitted. Colors are RGB565, 4 digit HEX codes:");
  tft.setTextColor(WHITE, BLACK);
  tft.println("WHITE: FFFF");
  tft.setTextColor(RED, BLACK);
  tft.println("RED: F800"); 
  tft.setTextColor(GREEN, BLACK);
  tft.println("GREEN: 07E0"); 
  tft.setTextColor(BLUE, BLACK);
  tft.println("BLUE: 001F"); 
  tft.println("...");
  tft.setTextColor(BLACK, BLUE);
  tft.println("Waiting for JSON data..."); 
}

void loop() {
  if (!Serial.available()) return;

  size_t len = Serial.readBytesUntil('\n', jsonBuffer, sizeof(jsonBuffer) - 1);
  jsonBuffer[len] = '\0';

  StaticJsonDocument<BUFFER_SIZE> doc;
  DeserializationError err = deserializeJson(doc, jsonBuffer);
  if (err) {
    Serial.println("JSON parse error");
    return;
  }

  /* Update only provided keys */
  if (doc.containsKey("txt")) {
    text = (const char *)doc["txt"];
  }

  if (doc.containsKey("size")) {
    textSize = doc["size"];
    if (textSize < 1) textSize = 1;
    if (textSize > 5) textSize = 5;
  }

  if (doc.containsKey("fg")) {
    fgColor = parseColor(doc["fg"]);
  }

  if (doc.containsKey("bg")) {
    bgColor = parseColor(doc["bg"]);
  }

  redraw();
}
