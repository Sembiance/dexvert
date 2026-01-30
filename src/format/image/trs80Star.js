import {Format} from "../../Format.js";

export class trs80Star extends Format
{
	name       = "TRS-80";
	ext        = [".grf", ".max", ".p41", ".pix"];
	byteCheck  = [{offset : 0, match : [0x00, 0x18]}];
	converters = ["recoil2png", "wuimg[format:trs80max]"];
}
