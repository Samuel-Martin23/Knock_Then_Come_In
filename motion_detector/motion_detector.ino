#define TRIG_PIN 8
#define ECHO_PIN 7


void setup() 
{
  Serial.begin(9600); 
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

}

void loop() 
{
  long duration = 0;
  long distance = 0;
  digitalWrite(TRIG_PIN,HIGH);
  delayMicroseconds(1000);
  digitalWrite(TRIG_PIN, LOW);
  duration=pulseIn(ECHO_PIN, HIGH);
  distance = (duration / 2) / 29.1;
  Serial.println(distance);
  delay(10);
}
