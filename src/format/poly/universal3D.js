import {Format} from "../../Format.js";

export class universal3D extends Format
{
	name        = "Universal 3D";
	website     = "http://fileformats.archiveteam.org/wiki/U3D";
	ext         = [".u3d"];
	magic       = ["ECMA-363, Universal 3D", "Universal 3D", /^fmt\/702( |$)/];
	unsupported = true;	// polyTrans supports this, but we don't support that program anymore. Only 7 files (all the same) on discmaster, so not worth vibing
}
