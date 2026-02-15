import {Format} from "../../Format.js";

export class trs80Star extends Format
{
	name       = "TRS-80";
	ext        = [".grf", ".max", ".p41", ".pix"];
	byteCheck  = [{offset : 0, match : [0x00, 0x18]}];
	converters = ["recoil2png[format:PIX.CocoMax,MAX.CocoMax,GRF.CocoMax,P41]", "wuimg[format:trs80max]"];
}
