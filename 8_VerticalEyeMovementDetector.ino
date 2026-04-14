//graph for up and down - done
//

int range1 = 0;
int range2;
int lastDirection = 0;

int cycleCount = 0;
unsigned long startTime = 0;
const unsigned long windowTime = 10000;  // 10 sec

float alpha = 0.1;
float filtered = 0;

void setup() {
  Serial.begin(115200);
  startTime = millis();
}

void loop() {
  delay(200);
  float sensor1 = analogRead(A0);
  float sensor2 = analogRead(A1);
  // filtered = alpha*sensor1+(1-alpha)*filtered;
  // Serial.println(filtered);

  int constrainedInput1 = constrain(sensor1, 350, 650);
  int constrainedInput2 = constrain(sensor2, 350, 650);

  range1 = map(constrainedInput1, 350, 650, 0, 6);
  range2 = map(constrainedInput2, 350, 650, 0, 6);
  switch (range1) {
  case 0:
    if (lastDirection != -1) {
      Serial.println("Down");
      lastDirection = -1;
      }
  break;

  case 4:
    if (lastDirection != 1) {
      Serial.println("Up");
      lastDirection = 1;
    }
      break;

    default:
    Serial.println("0");
    break;
  }

  switch (range2) {
  case 0:
    if (lastDirection != -1) {
      Serial.println("Left");
      lastDirection = -1;
      }
  break;

  case 4:
    if (lastDirection != 1) {
      Serial.println("Right");
      lastDirection = 1;
    }
      break;

    default:
    Serial.println("1");
    break;
  }

}
