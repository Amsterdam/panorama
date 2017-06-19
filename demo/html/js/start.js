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
	"https://acc.data.amsterdam.nl/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000329/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/03/21/TMX7315120208-000021/pano_0000_000330/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/03/24/TMX7315120208-000022/pano_0001_000529/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/04/18/TMX7315120208-000030/pano_0000_000853/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/04/18/TMX7315120208-000030/pano_0000_001797/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/04/19/TMX7315120208-000033/pano_0000_006658/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/05/09/TMX7315120208-000038/pano_0002_000466/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/06/TMX7315120208-000067/pano_0011_000463/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/08/TMX7315120208-000072/pano_0007_000072/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/09/TMX7315120208-000073/pano_0004_000087/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/09/TMX7315120208-000073/pano_0004_000183/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/09/TMX7315120208-000073/pano_0005_001111/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/15/TMX7316060226-000020/pano_0000_000801/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/05/09/TMX7315120208-000038/pano_0000_000321/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/05/10/TMX7315120208-000045/pano_0000_009792/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/05/26/TMX7315120208-000059/pano_0005_000402/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/09/TMX7315120208-000073/pano_0005_001120/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/14/TMX7315120208-000085/pano_0000_002422/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/06/21/TMX7315080123-000304/pano_0000_001220/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/07/05/TMX7315120208-000100/pano_0000_000434/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/07/12/TMX7315120208-000110/pano_0000_000175/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/07/18/TMX7315120208-000143/pano_0000_001701/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/07/22/TMX7315120208-000162/pano_0004_000703/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/07/27/TMX7316060226-000006/pano_0001_001524/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/02/TMX7316010203-000040/pano_0001_001871/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/04/TMX7316010203-000046/pano_0000_000743/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/05/TMX7316060226-000014/pano_0000_007566/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/09/TMX7316010203-000053/pano_0000_002161/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/12/TMX7316060226-000017/pano_0005_001027/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/15/TMX7316060226-000021/pano_0002_000459/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/03/17/TMX7315120208-000020/pano_0000_000175/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/18/TMX7316010203-000079/pano_0006_000054/equirectangular/panorama_",
	"https://acc.data.amsterdam.nl/panorama/2016/08/23/TMX7316010203-000081/pano_0001_005553/equirectangular/panorama_"
];

var demo_pano = demo_panos[Math.floor(Math.random() * demo_panos.length)];

var source = new Marzipano.ImageUrlSource(function(tile) {
	return { url: demo_pano + tile._level._width + ".jpg" };
});

var geometry = new Marzipano.EquirectGeometry([
	{ width: 2000 },
	{ width: 4000 },
	{ width: 8000 }
]);

// Create view.
var limiter = Marzipano.RectilinearView.limit.traditional(2000, 100*Math.PI/180);
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