import {xu} from "xu";
import {Format} from "../../Format.js";

export class pumaStreetSoccerPPM extends Format
{
	name           = "Puma Street Soccer PPM";
	website        = "http://fileformats.archiveteam.org/index.php?title=Puma_Street_Soccer_PPM&diff=51052&oldid=0";
	ext            = [".ppm"];
	forbidExtMatch = true;
	magic          = ["Puma Street Soccer PPM bitmap", "deark: pss_ppm (PSS PX)"];
	converters     = ["deark[module:pss_ppm]"];
}
