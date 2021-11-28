import {Format} from "../../Format.js";

export class grStar extends Format
{
	name       = "Graphics 7/8/9/9+/10/11 Image";
	website    = "http://fileformats.archiveteam.org/wiki/GR*";
	ext        = [".gr7", ".gr8", ".gr9", ".g9s", ".sfd", ".gr9p", ".g10", ".g11"];
	fileSize   = {".gr7" : 3844, ".gr8,.gr9" : [7680, 7682, 7684], ".g10" : 7689};
	converters = ["recoil2png"];
}
