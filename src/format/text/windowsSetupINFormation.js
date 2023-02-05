import {Format} from "../../Format.js";

export class windowsSetupINFormation extends Format
{
	name         = "Windows Setup INFormation";
	magic        = ["Windows setup INFormation", /^x-fmt\/420( |$)/];
	untouched    = true;
	metaProvider = ["text"];
}
