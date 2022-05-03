import {Format} from "../../Format.js";

export class tiCalc extends Format
{
	name       = "Texas Instruments Calculator Image";
	website    = "http://fileformats.archiveteam.org/wiki/TI_picture_file";
	ext        = [".82i", ".8ca", ".8ci", ".92i", ".73i", ".83i", ".8xi", ".85i", ".86i", ".89i", ".9xi", ".v2i"];
	mimeType   = "application/x-ti-variable";
	magic      = ["TI bitmap", "Texas Instruments file format", /^TI-[89][2356]\+? Graphic Calculator/];
	converters = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "deark", "tomsViewer"];
}
