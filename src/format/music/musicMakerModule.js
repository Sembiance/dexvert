import {Format} from "../../Format.js";

export class musicMakerModule extends Format
{
	name        = "MusicMaker Module";
	ext         = [".mm8"];
	magic       = ["MusicMaker v8 module"];
	unsupported = true;
}
