import {Format} from "../../Format.js";

export class gpFax extends Format
{
	name       = "GPFax FAX format";
	magic      = ["GPFax FAX format"];
	converters = ["wuimg[format:faxx]"];
}
