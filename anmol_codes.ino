#define STEPX 5
#define STEPY 4                                                                                                                                                                                    
#define DIRX 6
#define DIRY 3

void stepX();
void stepY();

int incomingByte;

void setup() {
  // put your setup code here, to run once:
    pinMode(STEPX, OUTPUT);
    pinMode(STEPY, OUTPUT);
    pinMode(DIRX, OUTPUT);
    pinMode(DIRY, OUTPUT);
    Serial.begin(9600);
    pinMode(2,OUTPUT);//this is set hight to enable the stepper motors
      digitalWrite(2,HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0)
  {
    incomingByte = Serial.read();
  }
  Serial.println(incomingByte,DEC);
  if(incomingByte == 'S')
  {
      Serial.println("ds");
      incomingByte = 0; 
      stepX();
  }
  if(incomingByte == 'R')
  {
    stepXinv();
    incomingByte = 0; 
  }
}

void stepX()
{
  digitalWrite(DIRX,HIGH);
Serial.println("itran");
  
  for(int a = 0; a < 50; ++a)
  {
    digitalWrite(STEPX, HIGH);
    delayMicroseconds(50000);
    digitalWrite(STEPX,LOW);
    delayMicroseconds(50000);
  }
  
}

void stepXinv()
{
  digitalWrite(DIRX,LOW);
  
  
  for(int a = 0; a < 50; ++a)
  {
    digitalWrite(STEPX, HIGH);
    delayMicroseconds(50000);
    digitalWrite(STEPX,LOW);
    delayMicroseconds(50000);
  }
  
}
