// Pin definitions
constexpr int pinV = A0; // Vertical EOG
constexpr int pinH = A1; // Horizontal EOG

// Thresholds
constexpr int threshH = 30;
constexpr int threshV = 30;

// Cursor position
int posX = 1;
int posY = 1;

// Cooldown
unsigned long lastMoveTime = 0;
constexpr int cooldown = 200;

constexpr int WINDOW = 5;
constexpr int SAMPLES = 200;

float baselineH = 0;
float baselineV = 0;

static String state = "CENTER";
static String prevState = "";

static int eyeMoveCount = 0;

struct MAResult {
  float h;
  float v;
};

MAResult movingAverage() {
  static float bufferV[WINDOW];
  static float bufferH[WINDOW];
  static int idx = 0;
  static float sumV = 0;
  static float sumH = 0;
  static bool initialized = false;

  if (!initialized) {
    for (int i = 0; i < WINDOW; i++) {
      bufferV[i] = analogRead(pinV);
      bufferH[i] = analogRead(pinH);
      sumV += bufferV[i];
      sumH += bufferH[i];
    }
    initialized = true;
  }

  sumV -= bufferV[idx];
  sumH -= bufferH[idx];

  bufferV[idx] = analogRead(pinV);
  bufferH[idx] = analogRead(pinH);

  sumV += bufferV[idx];
  sumH += bufferH[idx];

  idx = (idx + 1) % WINDOW;

  MAResult result;
  result.v = sumV / WINDOW;
  result.h = sumH / WINDOW;

  return result;
}

void calibrateBaseline() {
  long sumH = 0;
  long sumV = 0;

  Serial.println("Calibrating baseline... look straight");
  delay(2000);

  for (int i = 0; i < SAMPLES; i++) {
    MAResult result = movingAverage();
    sumH += result.h;
    sumV += result.v;
    delay(10);
  }

  baselineH = sumH / static_cast<float>(SAMPLES);
  baselineV = sumV / static_cast<float>(SAMPLES);

  Serial.print("Baseline H: ");
  Serial.println(baselineH);
  Serial.print("Baseline V: ");
  Serial.println(baselineV);
  delay(1000);
}

void getState() {
  if (posY == 2) state = "UP";
  else if (posY == 0) state = "DOWN";
  else if (posX == 0) state = "LEFT";
  else if (posX == 2) state = "RIGHT";
  else state = "CENTER";
}

void resetCursor() {
  posX = 1;
  posY = 1;
  state = "CENTER";
  prevState = "";

  Serial.println("Resetting...");
  delay(100);
  calibrateBaseline();
}

void setup() {
  Serial.begin(115200);
  calibrateBaseline();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'r') resetCursor();
  }

  MAResult result = movingAverage();

  float v = result.v;
  float h = result.h;

  float dh = h - baselineH;
  float dv = v - baselineV;

  unsigned long now = millis();

  bool moved = false;

  if (now - lastMoveTime > cooldown) {
    if (dh > threshH) {
      posX = min(posX + 1, 2);
      lastMoveTime = now;
      moved = true;
    }
    else if (dh < -threshH) {
      posX = max(posX - 1, 0);
      lastMoveTime = now;
      moved = true;
    }

    if (dv > threshV) {
      posY = min(posY + 1, 2);
      lastMoveTime = now;
      moved = true;
    }
    else if (dv < -threshV) {
      posY = max(posY - 1, 0);
      lastMoveTime = now;
      moved = true;
    }
  }

  getState();

  // EVENT,arduino_time_ms,posX,posY,state,rawH,rawV,deltaH,deltaV
  if (moved) {
    Serial.print("EVENT,");
    Serial.print(millis());
    Serial.print(",");
    Serial.print(posX);
    Serial.print(",");
    Serial.print(posY);
    Serial.print(",");
    Serial.print(state);
    Serial.print(",");
    Serial.print(h);
    Serial.print(",");
    Serial.print(v);
    Serial.print(",");
    Serial.print(dh);
    Serial.print(",");
    Serial.println(dv);

    eyeMoveCount++;
  }

  delay(30);
}