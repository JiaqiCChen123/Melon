/**
 * @license
 * Copyright 2020 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

setTimeout(init, 200);

function init() {
  document.getElementById('btnPlay').addEventListener('click', playAudio);
  document.getElementById('btnPause').addEventListener('click', pauseAudio);
}


var audioMp3 = new Audio();
audioMp3.src = 'music/test.mp3';

function playAudio(){
  audioMp3.play();
  document.getElementById('btnPause').disabled = false;
  document.getElementById('btnPlay').disabled = true;
}

function pauseAudio(){
  audioMp3.pause();
  document.getElementById('btnPause').disabled = true;
  document.getElementById('btnPlay').disabled = false;
}

function setup() {
  let myCanvas = createCanvas(300, 300);
  myCanvas.parent('canvas-container');
//   img = loadImage("assets/t3.png");

  r = random(255);
  g = random(255);
  b = random(255);
  fill(r, g, b, 127);
  stroke(r, g, b);
  rect(80, 120, 10, 10);
  rect(90, 110, 10, 10);
  rect(100, 120, 10, 10);
  rect(70, 130, 10, 10);
}

function draw() {
  background('white');

  // image(img, 0, 0);
  // imageMode(CENTER);

  strokeWeight(1);
  stroke(r, g, b);
  fill(r, g, b, 127);
  ellipse(150, 150, 300, 300);

  // geometry
  push();
  translate(width * 0.8, height * 0.3);
  rotate(frameCount / -100.0);
  polygon(0, 0, 50, 7);
  pop();

  //circle
  // push();
  // translate(width * 0.1, height * 0.2);
  // rotate(frameCount / 50.0);
  // polygon(0, 0, 80, 20);
  // pop();

  //triangle
  push();
  translate(width * 0.2, height * 0.8);
  rotate(frameCount / 200.0);
  polygon(0, 0, 82, 3);
  pop();

  textSize(40);
  fill('white');
  text('M E L O N', 80, 180);
}

function polygon(x, y, radius, npoints) {
  let angle = TWO_PI / npoints;
  beginShape();
  for (let a = 0; a < TWO_PI; a += angle) {
    let sx = x + cos(a) * radius;
    let sy = y + sin(a) * radius;
    vertex(sx, sy);
  }
  endShape(CLOSE);
}
