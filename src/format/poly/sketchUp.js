import {Format} from "../../Format.js";

export class sketchUp extends Format
{
	name       = "SketchUp Model";
	website    = "http://fileformats.archiveteam.org/wiki/SKP";
	ext        = [".skp"];
	magic      = ["SketchUp Model", "SketchUp model", "Google SketchUp Model", "SketchUp component :skp:", /^fmt\/(1263|1264|1265|1266|1267|1268)( |$)/, /^x-fmt\/451( |$)/];
	converters = ["poly2glb[type:sketchUp]"]; // polyTrans does a GREAT job, but we don't run it anymore. so sketchup isn't a real file format. Instead it's a bunch of C++ object graph classes serialized to disk with MFC, so it's TOUGH to support
}
