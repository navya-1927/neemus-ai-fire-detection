// PIN DEFINITIONS
const int ledRedPin = 25;
const int ledGreenPin = 26;
const int buzzerPin = 27;
const int relayPin = 23;

void setup() {
  // Start the serial communication (simulating our network connection to Jetson)
  Serial.begin(115200);

  // Configure all our hardware pins to send OUT voltage
  pinMode(ledRedPin, OUTPUT);
  pinMode(ledGreenPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(relayPin, OUTPUT);

  // Set the system to Normal (Green) upon boot
  setNormalState();

  // Print instructions for the presentation demo
  Serial.println("=====================================");
  Serial.println("ESP32 Distributed Alarm Node: READY");
  Serial.println("Waiting for Jetson Nano triggers...");
  Serial.println("Type 'F' for FIRE ALERT. Type 'N' for NORMAL.");
  Serial.println("=====================================");
}

void loop() {
  // Listen for incoming commands from the simulated Jetson Nano
  if (Serial.available() > 0) {
    char inCom = Serial.read();

    // If it receives an 'F' or 'f', trigger the fire protocol
    if (inCom == 'F' || inCom == 'f') {
      setFireState();
    }
    // If it receives an 'N' or 'n', reset the system
    else if (inCom == 'N' || inCom == 'n') {
      setNormalState();
    }
  }
}

//HARDWARE CONTROL FUNCTIONS

void setNormalState() {
  Serial.println("[STATUS] System Normal. Monitoring...");
  
  // LED turns Green
  digitalWrite(ledRedPin, LOW);
  digitalWrite(ledGreenPin, HIGH); 
  
  // Silence buzzer and turn off relay
  noTone(buzzerPin);               
  digitalWrite(relayPin, LOW);     
}

void setFireState() {
  Serial.println("\n [ALERT] FIRE SIGNATURE DETECTED! Triggering Alarms!");
  
  // LED turns Red
  digitalWrite(ledGreenPin, LOW);
  digitalWrite(ledRedPin, HIGH);   
  
  // Blast the buzzer at 1000Hz
  tone(buzzerPin, 1000);           
  
  // Throw the relay switch (to activate external sprinklers/sirens)
  digitalWrite(relayPin, HIGH);    
}