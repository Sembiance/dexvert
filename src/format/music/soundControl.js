import {Format} from "../../Format.js";

export class soundControl extends Format
{
	name         = "Sound Control Module";
	ext          = [".sc", ".sct"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:SoundControl]"];
}
