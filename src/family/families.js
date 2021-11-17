import {archive} from "./archive.js";
import {audio} from "./audio.js";
import {document} from "./document.js";
import {executable} from "./executable.js";
import {font} from "./font.js";
import {image} from "./image.js";
import {music} from "./music.js";
import {other} from "./other.js";
import {poly} from "./poly.js";
import {text} from "./text.js";
import {video} from "./video.js";

const families =
{
	archive    : archive.create(),
	audio      : audio.create(),
	document   : document.create(),
	executable : executable.create(),
	font       : font.create(),
	image      : image.create(),
	music      : music.create(),
	other      : other.create(),
	poly       : poly.create(),
	text       : text.create(),
	video      : video.create()
};
export {families};
