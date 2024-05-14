import {xu} from "xu";
import {Format} from "../../Format.js";

export class phVideo extends Format
{
	name        = "PH Video";
	ext         = [".ph"];
	magic       = ["PH video"];
	weakMagic   = true;
	auxFiles    = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()==="tmmplay.gxl");
	notes       = "No known converter or modern player. Could be kinda supported by using 'tmmplay.exe <filename>' in DOS to play the video. But it'll play in real time and sound capture will be hard to do.";
	unsupported = true;
}
