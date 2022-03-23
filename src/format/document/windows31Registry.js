import {Format} from "../../Format.js";

export class windows31Registry extends Format
{
	name           = "Windows 3.1 Registry";
	magic          = ["MS Windows 3.1 registry file"];
	converters     = ["strings"];
}
