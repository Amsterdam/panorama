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
	"http://localhost:8088/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000329_normalized.jpg",
	"http://localhost:8088/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000330_normalized.jpg",
	"http://localhost:8088/panorama/2016/03/24/TMX7315120208-000022/pano_0001_000529_normalized.jpg",
	"http://localhost:8088/panorama/2016/04/18/TMX7315120208-000030/pano_0000_000853_normalized.jpg",
	"http://localhost:8088/panorama/2016/04/18/TMX7315120208-000030/pano_0000_001797_normalized.jpg",
	"http://localhost:8088/panorama/2016/04/19/TMX7315120208-000033/pano_0000_006658_normalized.jpg",
	"http://localhost:8088/panorama/2016/05/09/TMX7315120208-000038/pano_0002_000466_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/06/TMX7315120208-000067/pano_0011_000463_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/08/TMX7315120208-000072/pano_0007_000072_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/09/TMX7315120208-000073/pano_0004_000087_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/09/TMX7315120208-000073/pano_0004_000183_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/09/TMX7315120208-000073/pano_0005_001111_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/15/TMX7316060226-000020/pano_0000_000801_normalized.jpg",
	"http://localhost:8088/panorama/2016/05/09/TMX7315120208-000038/pano_0000_000321_normalized.jpg",
	"http://localhost:8088/panorama/2016/05/10/TMX7315120208-000045/pano_0000_009792_normalized.jpg",
	"http://localhost:8088/panorama/2016/05/26/TMX7315120208-000059/pano_0005_000402_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/09/TMX7315120208-000073/pano_0005_001120_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/14/TMX7315120208-000085/pano_0000_002422_normalized.jpg",
	"http://localhost:8088/panorama/2016/06/21/TMX7315080123-000304/pano_0000_001220_normalized.jpg",
	"http://localhost:8088/panorama/2016/07/05/TMX7315120208-000100/pano_0000_000434_normalized.jpg",
	"http://localhost:8088/panorama/2016/07/12/TMX7315120208-000110/pano_0000_000175_normalized.jpg",
	"http://localhost:8088/panorama/2016/07/18/TMX7315120208-000143/pano_0000_001701_normalized.jpg",
	"http://localhost:8088/panorama/2016/07/22/TMX7315120208-000162/pano_0004_000703_normalized.jpg",
	"http://localhost:8088/panorama/2016/07/27/TMX7316060226-000006/pano_0001_001524_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/02/TMX7316010203-000040/pano_0001_001871_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/04/TMX7316010203-000046/pano_0000_000743_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/05/TMX7316060226-000014/pano_0000_007566_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/09/TMX7316010203-000053/pano_0000_002161_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/12/TMX7316060226-000017/pano_0005_001027_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/15/TMX7316060226-000021/pano_0002_000459_normalized.jpg",
	"http://localhost:8088/panorama/2016/03/17/TMX7315120208-000020/pano_0000_000175_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/18/TMX7316010203-000079/pano_0006_000054_normalized.jpg",
	"http://localhost:8088/panorama/2016/08/23/TMX7316010203-000081/pano_0001_005553_normalized.jpg"
];

var demo_pano = demo_panos[Math.floor(Math.random() * demo_panos.length)];

// Create source.
var source = Marzipano.ImageUrlSource.fromString(demo_pano);

// Create geometry.
var geometry = new Marzipano.EquirectGeometry([{ width: 8000 }]);

// Create view.
var limiter = Marzipano.RectilinearView.limit.traditional(1024, 100*Math.PI/180);
var view = new Marzipano.RectilinearView({ yaw: 0 }, limiter);

// Create scene.
var scene = viewer.createScene({
	source: source,
	geometry: geometry,
	view: view,
	pinFirstLevel: true
});

// Display scene.
scene.switchTo();