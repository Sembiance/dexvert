import {Format} from "../../Format.js";

export class gameMusicCreator extends Format
{
	name         = "Game Music Creator Module";
	website      = "http://fileformats.archiveteam.org/wiki/Game_Music_Creator";
	ext          = [".gmc"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
