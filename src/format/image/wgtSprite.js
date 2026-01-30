import {Format} from "../../Format.js";

export class wgtSprite extends Format
{
	name           = "WGT Sprite";
	website        = "http://fileformats.archiveteam.org/wiki/WGT_Sprite";
	ext            = [".spr"];
	forbidExtMatch = true;
	magic          = ["WGT Sprite"];
	converters     = ["wuimg[format:wgtspr]"];
}
