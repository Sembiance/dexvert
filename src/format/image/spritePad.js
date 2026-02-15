import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class spritePad extends Format
{
	name       = "SpritePad";
	website    = "http://fileformats.archiveteam.org/wiki/SpritePad";
	ext        = [".spd"];
	magic      = ["Sprite Pad Data", /^fmt\/1561( |$)/];
	
	// .spd can be somewhat common of an extension, so only match if we have a magic match OR we have explicitly set an environment variable as commodore
	idCheck = (inputFile, detections, {magicMatch}) => magicMatch || RUNTIME.globalFlags?.osHint?.commodore;
	converters = ["recoil2png[format:SPD]", "view64"];
}
