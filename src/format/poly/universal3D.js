import {Format} from "../../Format.js";

export class universal3D extends Format
{
	name       = "Universal 3D";
	website    = "http://fileformats.archiveteam.org/wiki/U3D";
	ext        = [".u3d"];
	magic      = ["ECMA-363, Universal 3D", "Universal 3D", /^fmt\/702( |$)/];
	converters = ["polyTrans64[format:universal3D]"];
}
