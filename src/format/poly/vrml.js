import {Format} from "../../Format.js";

export class vrml extends Format
{
	name       = "Virtual Reality Modeling Language";
	website    = "http://fileformats.archiveteam.org/wiki/VRML";
	ext        = [".wrl", ".wrz"];
	magic      = ["Virtual Reality Modeling Language", "ISO/IEC 14772 VRML 97 file", /^VRML \d file/, /^fmt\/(93|94)( |$)/];
	auxFiles   = (input, otherFiles) =>
	{
		const supportFiles = otherFiles.filter(o => [".gif", ".jpg", ".tiff", ".tif"].includes(o.ext.toLowerCase()));
		return supportFiles.length===0 ? false : supportFiles;
	};
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics(/^fmt\/94( |$)/))
			r.push("polyTrans64[format:vrml2]");

		r.pushUnique("polyTrans64[format:vrml1]");
		r.push("AccuTrans3D", "blender[format:x3d]");
		return r;
	};
}
