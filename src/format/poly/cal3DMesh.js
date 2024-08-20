import {Format} from "../../Format.js";

export class cal3DMesh extends Format
{
	name       = "Cal3D Mesh";
	ext        = [".cmf"];
	magic      = ["Cal3D Mesh File"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="CMF " && macFileCreator==="EIPH";
	converters = ["threeDObjectConverter"];
}
