// Inclusao das bibliotecas
#include <OneWire.h>
#include <DallasTemperature.h>

const int PINO_ONEWIRE = 12;         // Define pino do sensor
const int PINO_SENSOR = A0;          // Pino sensor pressao
OneWire oneWire(PINO_ONEWIRE);       // Cria um objeto OneWire
DallasTemperature sensor(&oneWire);  // Informa a referencia da biblioteca dallas temperature para Biblioteca onewire
DeviceAddress endereco_temp;         // Cria um endereco temporario da leitura do sensor

void setup() {
  Serial.begin(9600);                     // Inicia a porta serial
  Serial.println("Medindo Temperatura");  // Imprime a mensagem inicial
  sensor.begin();
  ;  // Inicia o sensor
}

void loop() {
  int leitura = analogRead(PINO_SENSOR);
  sensor.requestTemperatures();                // Envia comando para realizar a conversão de temperatura
  if (!sensor.getAddress(endereco_temp, 0)) {  // Encontra o endereco do sensor no barramento
    Serial.println("SENSOR NAO CONECTADO");    // Sensor conectado, imprime mensagem de erro
  } else {
    
                                                        // Converte leitura (0-1023) para tensao (0-5V)
    float tensao = leitura * (5.0 / 1023.0);

    // Converte tensao para pressão em psi
    // 0.5V = 0 psi ; 4.5V = 30 psi
    float psi = (tensao - 0.5) * (30.0 / 4.0);  // ou *7.5

    // Evita valores negativos se houver pequeno erro de offset
    if (psi < 0) psi = 0;

    Serial.print(" | Tensão: ");
    Serial.print(tensao, 3);
    Serial.print(" V");

    Serial.print(" | Pressao: ");
    Serial.print(psi, 2);
    Serial.print(" psi");

    Serial.print(" | Temperatura = ");                  // Imprime a temperatura no monitor serial
    Serial.println(sensor.getTempC(endereco_temp), 1);  // Busca temperatura para dispositivo
  }

  delay(1000);
}