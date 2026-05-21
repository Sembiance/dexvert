import {Format} from "../../Format.js";

export class kml extends Format
{
	name        = "Keyhole Markup Language";
	website     = "http://fileformats.archiveteam.org/wiki/KML";
	ext         = [".kml", ".kmz"];
	magic       = ["XML 1.0 document text Google KML document", "Google Earth placemark", "OpenGIS KML document", "Google KML document", "Google Earth saved working session", /^fmt\/(244|724)( |$)/];
	unsupported = true;	// 891 unique kml files and 266 unique kmz files on discmaster, but since many just contain placemarks/nodes and no models/textures or very specific to an app like Google Earth, it's not a priority to support
}
