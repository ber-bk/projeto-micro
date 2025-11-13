# projeto-micro

Roteiro Capacete
Vamos fazer um capacete de mergulho, sem nos preocuparmos com vedar, inserir vários sensores de biometria, camera e fonia, estes irão conectado num esp32, todos conectados através de uma protoboard.
O esp32, a camera e o fone irão se comunicar com o computador através de um cabo umbilical, onde o código neste computador receberá os dados dos sensores enviados pelo umbilical. Estes dados serão demonstrados numa dashboard visual, 
com o feed da camera, o audio, e um display dos sensores de pressao, etc. Criaremos logs por mergulho. Lembrando que sensores como pressão e temperatura, como tem uma taxa baixa de mudança, podem ser enviados um update por minuto.
Teremos a opção de exportar os dados(para um banco),também o video e a fonia

capacete:
  Bola de plastico rigido e translucido, 30cm de raio (60cm diametro)
  caixa plastica de 20x20x10 para colocar o arduino e sensores

microcontroladores:
  arduino

MVP:
  interno:
    fone com microfone

  externo:
    sensor de pressao
    câmera usb

desejado:
  batimento
  temperatura do mergulhador
  oximetria

dashboard:
  feed e comunicação por voz em tempo real
  Hud de dados de temperatura e pressao + desejados
  criar logs por mergulho, coletando info de tempo em tempo
  export do video em .avi
  export dos dados podem ficar num banco de dados




