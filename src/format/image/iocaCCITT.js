import {Format} from "../../Format.js";

export class iocaCCITT extends Format
{
	name           = "IOCA CCITT";
	ext            = [".ioc"];
	forbidExtMatch = true;
	magic          = ["IOCA CCITT :ioca:"];
	converters     = ["nconvert[format:ioca]"];
}
