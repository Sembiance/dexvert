import {Format} from "../../Format.js";

export class applesoftBASIC extends Format
{
	name           = "Applesoft BASIC Source Code";
	ext            = [".bas"];
	forbidExtMatch = true;
	// don't match against "Applesoft BASIC program data", it's FAR too weak
	idMeta         = ({proDOSTypeCode}) => proDOSTypeCode==="BAS";
	converters     = ["applesoftBASIC2txt"];
}
