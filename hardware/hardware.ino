#include <DHT11.h> // Include the DHT11 library

#define DHTPIN 10 // Define the pin where the DHT11 sensor is connected

DHT11 dht(DHTPIN); // Create a DHT11 object

void setup() {
  Serial.begin(9600);
  
}

void readDHT11() {
  float humidity = dht.readHumidity(); // Read humidity
  float temperature = dht.readTemperature(); // Read temperature


  Serial.print("humidity:");
  Serial.println(humidity);
  Serial.print("temperature:");
  Serial.println(temperature);

}

void loop() {
  readDHT11();

  float cdsValue = analogRead(A0); // Read the CDS sensor value
  unsigned long currentMillis = millis();
  float lux = cdsValue ; 

  static unsigned long lastCheckTime = 0;
  static unsigned long lowLuxTime = 0;

  if (lux <= 400) {
    if (lastCheckTime == 0) {
      lastCheckTime = currentMillis;
    } else {
      lowLuxTime += currentMillis - lastCheckTime;
      lastCheckTime = currentMillis;
    }
  } else {
    lastCheckTime = 0;  
    lowLuxTime = 0;
  }

  float flowSensor = analogRead(A5); // Assuming the flow sensor is connected to A5


  Serial.print("light:");
  Serial.println(lowLuxTime / 1000.0);
  Serial.print("windblow:");
  Serial.println(flowSensor/2.5);
}