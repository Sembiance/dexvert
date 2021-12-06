import {Format} from "../../Format.js";

export class vgmMusicMaker extends Format
{
	name        = "VGM Music Maker Module";
	ext         = [".vge"];
	magic       = ["VGM Music Maker module"];
	unsupported = true;
}
