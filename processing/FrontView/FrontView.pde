import peasy.*;
PeasyCam cam;
ArrayList pointList;                   // arraylist to store the points in

void setup() {
  //-------------------------------- GENERAL
  size(500, 500, P3D);
  background(0);
  cam = new PeasyCam(this, -190, -60, 0, 150);
  cam.setMinimumDistance(50);
  cam.setMaximumDistance(600);
  //cam.rotateX(0);  
  cam.rotateY(1.5);
  cam.rotateZ(.1);
  //-------------------------------- POINTS
  pointList = new ArrayList();    // instantiate an ArrayList
  importTextFile();               // call our custom function
}

void draw() {
  background(0);  
  //-------------------------------- VISUALIZE THE POINT SET
  for (int i = 0; i < pointList.size(); ++i) {        
    PVector V = (PVector) pointList.get(i);
    stroke((V.z*V.y)*20, V.z*240, 255);
    strokeWeight(2);
    point(V.x*100, -V.z*100, V.y*100);
    //println(V.z);
  }
  //--------------------------------
  if (frameCount == 10)  
  {  
    saveFrame("FrontView.png");
    exit();
  }
}
/*-----------------------------------------------------------------------------
 *** CUSTOM IMPORT FUNCTION ***
 -----------------------------------------------------------------------------*/
void importTextFile() {   
  String[] strLines = loadStrings("/home/vision/3dpoint cloud/Final.csv");        // the name and extension of the file to import!
  for (int i = 0; i < strLines.length; ++i) {
    String[] arrTokens = split(strLines[i], ',');       // use the split array with character to isolate each component
    float xx = float(arrTokens[0]);                     // cast string value to a float values!
    float yy = float(arrTokens[1]);                     // cast string value to a float values!
    float zz = float(arrTokens[2]);                     // cast string value to a float values!
    pointList.add( new PVector(xx, yy, zz) );           // add values to a new array slot
  }
}
