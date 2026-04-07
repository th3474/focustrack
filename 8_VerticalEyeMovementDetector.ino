int range1 = 0;
int lastDirection = 0;

int cycleCount = 0;
unsigned long startTime = 0;
const unsigned long windowTime = 10000; // 10 sec

void setup() {
  Serial.begin(115200);
  startTime = millis();
}

void loop() {
int sensor1 = analogRead(A0);
int constrainedInput1 = constrain(sensor1, 350, 650);
range1 = map(constrainedInput1, 350, 650, 0, 6);

switch (range1) {
case 0:
  if (lastDirection != -1) {
    Serial.println("Down");
  if (lastDirection == 1) {
    cycleCount++;
  }
    lastDirection = -1;}
break;

case 4:
  if (lastDirection != 1) {
  Serial.println("Up");lastDirection = 1;
  }
  break;

  default:
  Serial.println("0");
  break;
}

if (millis() - startTime >= windowTime) {float frequency = cycleCount / (windowTime / 1000.0);
Serial.print("Frequency = ");
Serial.print(frequency);
Serial.println(" Hz");

cycleCount = 0;
startTime = millis();
}

delay(50);
  }
