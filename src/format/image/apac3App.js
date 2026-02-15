import {Format} from "../../Format.js";

export class apac3App extends Format
{
	name       = "Atari APAC3 APP Image";
	website    = "http://fileformats.archiveteam.org/wiki/Apac3_APP";
	ext        = [".app", ".aps", ".ils", ".pls"];
	magic      = ["APP raster bitmap"];
	converters = ["recoil2png[format:ILS,PLS,APP,APS]"];
}
