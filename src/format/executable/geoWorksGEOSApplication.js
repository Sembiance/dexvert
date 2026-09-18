import {Format} from "../../Format.js";

export class geoWorksGEOSApplication extends Format
{
	name           = "GeoWorks GEOS application";
	ext            = [".geo"];
	forbidExtMatch = true;
	magic          = ["GeoWorks GEOS application", "GeoWorks GEOS executable", "GeoWorks GEOS utility", /^GEOS executable,/, /^GeoWorks GEOS (socket|URL) driver/];
	converters     = ["vibeExtract"];
}
