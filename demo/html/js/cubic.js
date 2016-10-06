/*
 * Copyright 2016 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'use strict';

// Create viewer.
var viewer = new Marzipano.Viewer(document.getElementById('pano'));

var demo_panos = [
	"https://acc.atlas.amsterdam.nl/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000329_cubic",
	"https://acc.atlas.amsterdam.nl/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000330_cubic",
	"https://acc.atlas.amsterdam.nl/panorama/2016/03/24/TMX7315120208-000022/pano_0001_000529_cubic",
	"https://acc.atlas.amsterdam.nl/panorama/2016/04/18/TMX7315120208-000030/pano_0000_000853_cubic",
	"https://acc.atlas.amsterdam.nl/panorama/2016/04/18/TMX7315120208-000030/pano_0000_001797_cubic"
];

// Create source.
// The tiles were generated with the krpano tools, which indexes the tiles
// from 1 instead of 0. Hence, we cannot use ImageUrlSource.fromString()
// and must write a custom function to convert tiles into URLs.
var demo_pano = demo_panos[Math.floor(Math.random() * demo_panos.length)];

var source = Marzipano.ImageUrlSource.fromString(
		demo_pano + "/{z}/{f}/{y}/{x}.jpg",
		{ cubeMapPreviewUrl: demo_pano + "/preview.jpg" });

// Create geometry.
var geometry = new Marzipano.CubeGeometry([
	{ tileSize: 256, size: 256, fallbackOnly: true },
	{ tileSize: 512, size: 512 },
	{ tileSize: 512, size: 1024 },
	{ tileSize: 512, size: 2048 }
]);

// Create view.
var limiter = Marzipano.RectilinearView.limit.traditional(2048, 100*Math.PI/180);
var view = new Marzipano.RectilinearView(null, limiter);

// Create scene.
var scene = viewer.createScene({
	source: source,
	geometry: geometry,
	view: view,
	pinFirstLevel: true
});

// Display scene.
scene.switchTo();