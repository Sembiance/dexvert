import {Format} from "../../Format.js";

export class sketchUp extends Format
{
	name       = "SketchUp Model";
	website    = "http://fileformats.archiveteam.org/wiki/SKP";
	ext        = [".skp"];
	magic      = ["SketchUp Model", "SketchUp model", "Google SketchUp Model", "SketchUp component :skp:", /^fmt\/(1263|1264|1265|1266|1267|1268)( |$)/, /^x-fmt\/451( |$)/];
	converters = ["polyTrans64[format:sketchUp]"];
}
