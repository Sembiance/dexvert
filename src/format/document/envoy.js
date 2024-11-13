import {Format} from "../../Format.js";

export class envoy extends Format
{
	name       = "Envoy Document";
	website    = "http://fileformats.archiveteam.org/wiki/Envoy";
	ext        = [".evy"];
	magic      = ["Envoy document", /^fmt\/(1286|1287)( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="ENVD" || (macFileType==="EVYD" && macFileCreator==="ENVY");
	converters = ["envoyViewer"];
}
