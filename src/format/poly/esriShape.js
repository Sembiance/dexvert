import {Format} from "../../Format.js";

export class esriShape extends Format
{
	name           = "ESRI/ArcView Shape";
	website        = "http://fileformats.archiveteam.org/wiki/Shapefile";
	ext            = [".shp"];
	forbidExtMatch = true;
	magic          = ["ArcView Shape", "ESRI Shapefile", /^x-fmt\/235( |$)/];
	weakMagic      = ["ESRI Shapefile"];
	converters     = ["polyTrans64[format:esriShape]"];
}
