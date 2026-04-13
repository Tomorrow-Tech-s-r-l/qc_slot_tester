#define lockPin 2

String inputString = "";
int ledPins[] = {3, 5, 6, 9, 10, 11};
int pinCount = 6;

void setup() {
  Serial.begin(9600);
  pinMode(lockPin, OUTPUT);
  for (int i = 0; i < pinCount; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
  Serial.println("READY");  // Signal to host that the board finished booting
}

void loop() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      executeCommand(inputString);
      inputString = "";
    } else if (inChar != '\r') {  // Ignore carriage return (Windows line endings)
      inputString += inChar;
    }
  }
}

void executeCommand(String cmd) {
  cmd.trim();

  if (cmd == "LED_ON") {
    for (int i = 0; i < pinCount; i++) {
      analogWrite(ledPins[i], 138);  // ~54% brightness via PWM
    }
    Serial.println("OK:LED_ON");

  } else if (cmd == "LED_OFF") {
    for (int i = 0; i < pinCount; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    Serial.println("OK:LED_OFF");

  } else if (cmd == "Lock_ON") {
    digitalWrite(lockPin, HIGH);
    Serial.println("OK:Lock_ON");

  } else if (cmd == "Lock_OFF") {
    digitalWrite(lockPin, LOW);
    Serial.println("OK:Lock_OFF");

  } else if (cmd == "GET_STATUS") {
    Serial.println("SYSTEM_OK");

  } else if (cmd.length() > 0) {
    Serial.println("ERR:UNKNOWN_CMD");
  }
}
