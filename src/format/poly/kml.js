import {Format} from "../../Format.js";

export class kml extends Format
{
	name        = "Keyhole Markup Language";
	website     = "http://fileformats.archiveteam.org/wiki/KML";
	ext         = [".kml", ".kmz"];
	magic       = ["XML 1.0 document text Google KML document", "Google Earth placemark", "Google Earth saved working session", /^fmt\/(244|724)( |$)/];
	unsupported = true;
}
