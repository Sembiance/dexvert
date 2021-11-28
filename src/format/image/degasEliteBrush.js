import {Format} from "../../Format.js";

export class degasEliteBrush extends Format
{
	name       = "Degas Elite Brush";
	website    = "http://fileformats.archiveteam.org/wiki/DEGAS_Elite_brush";
	ext        = [".bru"];
	fileSize   = 64;
	converters = ["recoil2png"];
}
