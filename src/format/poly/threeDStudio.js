import {Format} from "../../Format.js";

export class threeDStudio extends Format
{
	name           = "3D Studio";
	website        = "http://fileformats.archiveteam.org/wiki/3DS";
	ext            = [".3ds", ".max", ".asc"];
	forbidExtMatch = [".asc"];
	magic          = ["3D Studio model", "3D Studio mesh", "3D Studio Max Scene", "3D Studio ASCII format", /^fmt\/978( |$)/, /^x-fmt\/19( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["□3DS", "3DS4"].includes(macFileType) && ["C4D1", "gmMD"].includes(macFileCreator);
	converters     = ["blender[format:3ds]", "polyTrans64[format:threeDStudio]", "assimp", "noesis[type:poly]"];
}
