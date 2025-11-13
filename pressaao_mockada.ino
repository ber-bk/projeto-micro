const int PINO_POTENCIOMETRO = A0;
const float COEF_A = 0.1333;
const float COEF_B = 0.5;
const float TENSAO_REFERENCIA = 5.0;

void setup() {
  Serial.begin(9600);
  pinMode(PINO_POTENCIOMETRO, INPUT);
  delay(1000);
}

void loop() {
  int valorAnalogico = analogRead(PINO_POTENCIOMETRO);
  float voltagem = (valorAnalogico * TENSAO_REFERENCIA) / 1023.0;
  float pressaoPSI = (voltagem - COEF_B) / COEF_A;
  
  // Formato CSV: valorADC,voltagem,pressao
  Serial.print(valorAnalogico);
  Serial.print(",");
  Serial.print(voltagem, 3);
  Serial.print(",");
  Serial.println(pressaoPSI, 2);
  
  delay(500);
}
