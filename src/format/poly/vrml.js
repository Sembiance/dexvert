import {Format} from "../../Format.js";

export class vrml extends Format
{
	name       = "Virtual Reality Modeling Language";
	website    = "http://fileformats.archiveteam.org/wiki/VRML";
	ext        = [".wrl", ".wrz"];
	magic      = ["Virtual Reality Modeling Language", "ISO/IEC 14772 VRML 97 file", "model/vrml", /^VRML \d file/, /^fmt\/(93|94)( |$)/];
	idMeta     = ({macFileType}) => macFileType==="VRML";
	auxFiles   = (input, otherFiles) =>
	{
		const supportFiles = otherFiles.filter(o => [".gif", ".jpg", ".tiff", ".tif"].includes(o.ext.toLowerCase()));
		return supportFiles.length===0 ? false : supportFiles;
	};
	keepFilename = true;
	converters   = ["AccuTrans3D", "blender[format:x3d]"];
}
