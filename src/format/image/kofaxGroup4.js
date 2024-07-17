import {Format} from "../../Format.js";

export class kofaxGroup4 extends Format
{
	name       = "Kofax Group 4";
	ext        = [".kfx"];
	magic      = ["Kofax Group 4 bitmap"];
	converters = ["nconvert", "hiJaakExpress[matchType:magic]"];
}
