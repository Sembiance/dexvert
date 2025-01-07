import {Format} from "../../Format.js";

export class electricImage3DFile extends Format
{
	name       = "Electric Image 3D File";
	website    = "http://fileformats.archiveteam.org/wiki/FACT";
	ext        = [".fact", ".fac"];
	magic      = ["ElectricImage 3D file", "ElectricImage 3D model"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="FACT" && ["EIBC", "EIAM"].includes(macFileCreator);
	converters = ["polyTrans64[format:electricImage3DFile]"];
}
