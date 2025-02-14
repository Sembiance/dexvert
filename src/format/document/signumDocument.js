import {Format} from "../../Format.js";

export class signumDocument extends Format
{
	name           = "Signum Document";
	website        = "https://github.com/Xiphoseer/sdo-tool/blob/main/docs/formats/sdoc.md";
	ext            = [".sdo"];
	forbidExtMatch = true;
	magic          = ["Signum 1/2 Document"];
	converters     = ["sdoTool"];
}
