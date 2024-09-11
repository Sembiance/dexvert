import {Format} from "../../Format.js";

export class superscapeDo3DObject extends Format
{
	name        = "Superscape Do 3D VCA";
	ext         = [".vca"];
	magic       = ["Superscape Do 3D object"];
	notes       = "I was able to open these in Superscape VRT, but exporting to VRML didn't produce a usable result. The 'Do 3D' program doesn't work any better (also requires CD in drive)";
	unsupported = true;
}
