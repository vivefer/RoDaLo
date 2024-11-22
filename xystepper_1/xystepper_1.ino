//Steps and Direction pins for motor 1
  int dir_pin1 = 2;
  int step_pin1 = 3;
  int enable_pin1 = 7;
  //Steps and Direction pins for motor 1
  int dir_pin2 = 4;
  int step_pin2 = 5;
  int enable_pin2 = 8;

  const int StepsPerRevolution = 200; // NEMA 17 standard
  const int StepsFor5mm = 80; //Adjust for precision // 80 steps cuz, 20 teeth pulley, 20 teeth * 2 mm pitch = 400 mm, for 5 mm, 400/5 = 80 steps

  const int GantryLenth = 500;
  const int GantryWidth = 500;

void setup(){
  
  //Pinmodes of both
  pinMode(dir_pin1, OUTPUT);
  pinMode(step_pin1, OUTPUT);
  pinMode(dir_pin2, OUTPUT);
  pinMode(step_pin2, OUTPUT);

  //enabling the drivers
  digitalWrite(enable_pin1, LOW);
  digitalWrite(enable_pin2, LOW);

  //kEEPING both motors direction forward at first
  digitalWrite(dir_pin1, HIGH);
  digitalWrite(dir_pin2, HIGH);

}

void loop(){
  
  //Loop to move x axis step, then y axis step
  for (int i = 0; i<=GantryLenth; i++){
    //Loop to move y axis width wise in each step of x axis
    for (int j = 0; j<=GantryWidth; j++){
      moveStepper(step_pin1, StepsFor5mm);
      delay(1000); // adjust the delay based on speed needed
    }
    digitalWrite(dir_pin1, !digitalRead(dir_pin1)); // motor 1 moving backward for even step in y axis
    moveStepper(step_pin2, StepsFor5mm);
    delay(250);
  }
  digitalWrite(dir_pin2, !digitalRead(dir_pin2)); // motor 2 moving backwards after reaching end of gantry
}

void moveStepper(int step_pin, int Steps){
  for (int i = 0; i< Steps; i++){
    digitalWrite(step_pin, HIGH);
    delay(200);
    digitalWrite(step_pin, LOW);
  }
}