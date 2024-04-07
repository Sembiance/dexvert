import {Format} from "../../Format.js";

export class macromediaProjector extends Format
{
	name       = "Macromedia Projector";
	magic      = ["Macromedia Projector"];
	fileMeta   = ({macFileType, macFileCreator}) => macFileType==="APPL" && ["PJ93", "PJ95"].includes(macFileCreator);
	converters = ["director_files_extract"];
}
