import {Format} from "../../Format.js";

export class garminVehicleImage extends Format
{
	name       = "Garmin Vehicale Images File";
	website    = "http://fileformats.archiveteam.org/wiki/SRF_(Garmin_vehicle)";
	ext        = [".srf"];
	magic      = ["Garmin Bitmap file", "Garmin vehicle image"];
	converters = ["srftopam"];
}
